from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rental", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="car",
            name="badge",
        ),
        migrations.RemoveField(
            model_name="car",
            name="emoji",
        ),
        migrations.AlterField(
            model_name="car",
            name="photo_url",
            field=models.TextField(blank=True),
        ),
    ]
