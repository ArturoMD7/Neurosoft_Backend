# Generated by Django 5.1.7 on 2025-03-29 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudios', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estudio',
            name='imagen',
        ),
        migrations.AddField(
            model_name='estudio',
            name='ruta_archivo',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
