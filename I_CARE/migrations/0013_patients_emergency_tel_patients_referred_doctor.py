# Generated by Django 4.1 on 2023-03-17 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0012_presenting_complaints_vitals'),
    ]

    operations = [
        migrations.AddField(
            model_name='patients',
            name='Emergency_Tel',
            field=models.CharField(default='00', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patients',
            name='Referred_Doctor',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]