# Generated by Django 4.1 on 2023-03-19 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0016_patients_referred_doctor_patients_referring_facility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patients',
            name='Emergency_Tel',
            field=models.CharField(default='None', max_length=15),
        ),
    ]