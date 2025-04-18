# Generated by Django 5.1.7 on 2025-04-03 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudios', '0003_rename_paciente_estudio_paciente_id'),
        ('pacientes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudio',
            name='paciente_id',
            field=models.ForeignKey(db_column='paciente_id', on_delete=django.db.models.deletion.CASCADE, to='pacientes.paciente', verbose_name='Paciente'),
        ),
    ]
