# DrivePort RentCar

Bu loyiha aeroportdan avtomobil ijarasi uchun tayyor Django + SQLite web sayt.

## Python versiyasi

Loyiha `Python 3.11.14` uchun moslangan.

- Tavsiya etilgan versiya: `3.11.14`
- Qo'llab-quvvatlanadigan liniya: `Python 3.11.x`
- `Python 3.14.x` bilan ishlatilmang, chunki `Django 5.0.14` bilan admin sahifalarda moslik xatosi chiqadi.

## Windows uchun eng oson ishga tushirish

1. Zip faylni oching.
2. Papkani VSCode ichida oching.
3. VSCode terminalini **Administrator** qilib oching.
4. Shu bitta buyruqni ishga tushiring:

```powershell
.\start_windows.cmd
```

Skript avtomatik ravishda quyidagilarni bajaradi:

- kerak bo'lsa Python topadi yoki o'rnatadi
- lokal virtual environment yaratadi
- barcha Python kutubxonalarni o'rnatadi
- `.env` faylni SQLite uchun tayyorlaydi
- Django migratsiyalarini bajaradi
- demo aeroport va mashinalarni bazaga yozadi
- Django admin user yaratadi
- frontend va backend serverni ishga tushiradi

## Ishga tushgandan keyin ochiladigan manzillar

- Sayt: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Mashinalar: [http://127.0.0.1:8000/mashinalar/](http://127.0.0.1:8000/mashinalar/)
- Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Admin login

- Login: `admin`
- Parol: `DrivePort2026!`

## SQLite fayli

Loyiha endi lokal `SQLite` bazadan foydalanadi.

- Database file: `db.sqlite3`
- Engine: `django.db.backends.sqlite3`

## Muhim eslatma

- Birinchi ishga tushirish internet talab qiladi.
- Birinchi ishga tushirish nisbatan uzoqroq davom etadi.
- Agar Windows Python o'rnatishga ruxsat so'rasa, tasdiqlang.
- Server ishlayotgan paytda terminalni yopmang.

## Mac yoki qo'lda ishga tushirish

Agar loyihani macOS yoki oddiy terminal orqali ishga tushirsangiz, virtual environment ni `Python 3.11.14` bilan yarating:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Terminalda ko'rinadigan yakuniy natija

Skript to'g'ri tugasa terminalda taxminan shu ma'lumotlar chiqadi:

```text
DrivePort tayyor.
Frontend va backend: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/
Admin login: admin
Admin parol: DrivePort2026!
Database: SQLite
SQLite file: db.sqlite3
```

## Loyiha ichidagi asosiy fayllar

- `start_windows.cmd` - Windows uchun bitta buyruqli launcher
- `start_windows.ps1` - to'liq avtomatik bootstrap skript
- `requirements.txt` - Python kutubxonalari
- `templates/` - frontend sahifalar
- `rental/` - Django backend
- `config/` - loyiha sozlamalari
