# Generated by Django 5.1.7 on 2025-03-29 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checklistcausas',
            old_name='paciente',
            new_name='paciente_id',
        ),
    ]
