# Generated by Django 5.1 on 2024-09-01 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_alter_application_program_alter_application_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationstatus',
            name='additional_documents',
            field=models.FileField(blank=True, null=True, upload_to='additional_documents/'),
        ),
        migrations.DeleteModel(
            name='AdditionalDocument',
        ),
    ]
