# Generated by Django 4.1 on 2023-03-17 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0011_vitals_department_vitals_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='presenting_complaints',
            name='Vitals',
            field=models.ForeignKey(db_column='Vitals', null=True, on_delete=django.db.models.deletion.SET_NULL, to='I_CARE.vitals'),
        ),
    ]
