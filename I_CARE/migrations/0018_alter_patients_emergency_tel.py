# Generated by Django 4.1 on 2023-03-19 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0017_alter_patients_emergency_tel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patients',
            name='Emergency_Tel',
            field=models.CharField(max_length=15, null=True),
        ),
    ]