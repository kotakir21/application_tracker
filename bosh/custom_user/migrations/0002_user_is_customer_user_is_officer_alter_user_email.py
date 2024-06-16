# Generated by Django 5.0.6 on 2024-06-16 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_customer",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_officer",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
