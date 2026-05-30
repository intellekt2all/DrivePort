$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}
Set-Location $PSScriptRoot

$ProjectName = "DrivePort"
$PythonVersion = "3.11"
$PythonExactVersion = "3.11.14"
$PythonVersionId = "Python.Python.3.11"
$AdminUsername = "admin"
$AdminEmail = "admin@driveport.local"
$AdminPassword = "DrivePort2026!"
$EnvFile = Join-Path $PSScriptRoot ".env"
$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

function Write-Step($Message) {
    Write-Host "[$ProjectName] $Message"
}

function Assert-LastExitCode($Message, $ExitCode = $LASTEXITCODE) {
    if ($ExitCode -ne 0) {
        throw "$Message Exit code: $ExitCode"
    }
}

function Find-CommandPath($Names) {
    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    return $null
}

function Get-PythonCommandVersion($FilePath, $ArgumentList = @()) {
    if (-not $FilePath) {
        return $null
    }

    try {
        $version = & $FilePath @ArgumentList -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }

        return ($version | Select-Object -First 1).Trim()
    } catch {
        return $null
    }
}

function Test-PythonVersionMatch($Version) {
    return $Version -and $Version.StartsWith("$PythonVersion.")
}

function Ensure-Winget {
    $winget = Find-CommandPath @("winget")
    if (-not $winget) {
        throw "winget topilmadi. Windows App Installer o'rnatilgan bo'lishi kerak."
    }

    return $winget
}

function Resolve-PythonInvocation {
    $pyLauncher = Find-CommandPath @("py")
    if ($pyLauncher) {
        $pyVersion = Get-PythonCommandVersion -FilePath $pyLauncher -ArgumentList @("-$PythonVersion")
        if (Test-PythonVersionMatch $pyVersion) {
            return @{
                Path = $pyLauncher
                Args = @("-$PythonVersion")
                Version = $pyVersion
            }
        }
    }

    foreach ($name in @("python3.11", "python")) {
        $pythonPath = Find-CommandPath @($name)
        $pythonVersion = Get-PythonCommandVersion -FilePath $pythonPath
        if (Test-PythonVersionMatch $pythonVersion) {
            return @{
                Path = $pythonPath
                Args = @()
                Version = $pythonVersion
            }
        }
    }

    return $null
}

function Ensure-Python {
    $python = Resolve-PythonInvocation
    if ($python) {
        return $python
    }

    $winget = Ensure-Winget
    Write-Step "Python o'rnatilmoqda..."
    & $winget install -e --id $PythonVersionId --accept-source-agreements --accept-package-agreements --silent
    Assert-LastExitCode -Message "Python o'rnatilmadi."

    $python = Resolve-PythonInvocation
    if (-not $python) {
        throw "Python $PythonExactVersion o'rnatildi, lekin terminal uni ko'rmadi. VSCode terminalni qayta ochib skriptni yana ishga tushiring."
    }

    return $python
}

function Ensure-Venv {
    $pythonLauncher = Ensure-Python
    $existingVenvVersion = Get-PythonCommandVersion -FilePath $VenvPython
    if ($existingVenvVersion -and -not (Test-PythonVersionMatch $existingVenvVersion)) {
        Write-Step "Eski virtual environment ($existingVenvVersion) o'chirilmoqda..."
        Remove-Item -Recurse -Force (Join-Path $PSScriptRoot ".venv")
    }

    if (-not (Test-Path $VenvPython)) {
        Write-Step "Python $($pythonLauncher.Version) bilan virtual environment yaratilmoqda..."
        & $pythonLauncher.Path @($pythonLauncher.Args + @("-m", "venv", ".venv"))
        Assert-LastExitCode -Message "Virtual environment yaratilmadi."
    }
}

function Write-ProjectEnv {
    $envContent = @"
DJANGO_SECRET_KEY=driveport-windows-local-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_DATABASE_ENGINE=sqlite
SQLITE_NAME=db.sqlite3
"@

    Set-Content -Path $EnvFile -Value $envContent -Encoding ASCII
}

function Ensure-PythonDependencies {
    Write-Step "Python kutubxonalari o'rnatilmoqda..."
    & $VenvPython -m pip install --upgrade pip
    Assert-LastExitCode -Message "pip yangilanmadi."
    & $VenvPython -m pip install -r requirements.txt
    Assert-LastExitCode -Message "Python kutubxonalari o'rnatilmadi."
}

function Ensure-DjangoAdmin {
    $shellScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='$AdminUsername',
    defaults={'email': '$AdminEmail', 'is_staff': True, 'is_superuser': True},
)
user.email = '$AdminEmail'
user.is_staff = True
user.is_superuser = True
user.set_password('$AdminPassword')
user.save()
print('admin_created=' + str(created))
"@

    $shellScript | & $VenvPython manage.py shell
    Assert-LastExitCode -Message "Django admin user yaratilmadi."
}

Ensure-Venv
Write-ProjectEnv
Ensure-PythonDependencies

Write-Step "Migratsiya bajarilmoqda..."
& $VenvPython manage.py migrate --noinput
Assert-LastExitCode -Message "Migratsiya bajarilmadi."

Write-Step "Demo ma'lumotlar yozilmoqda..."
& $VenvPython manage.py seed_driveport
Assert-LastExitCode -Message "Demo ma'lumotlar yozilmadi."

Write-Step "Admin foydalanuvchi yaratilmoqda..."
Ensure-DjangoAdmin

Write-Host ""
Write-Host "DrivePort tayyor."
Write-Host "Frontend va backend: http://127.0.0.1:8000/"
Write-Host "Admin: http://127.0.0.1:8000/admin/"
Write-Host "Admin login: $AdminUsername"
Write-Host "Admin parol: $AdminPassword"
Write-Host "Database: SQLite"
Write-Host "SQLite file: db.sqlite3"
Write-Host ""

& $VenvPython manage.py runserver 127.0.0.1:8000
Assert-LastExitCode -Message "Django server ishga tushmadi."
