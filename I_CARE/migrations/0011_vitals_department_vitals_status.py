# Generated by Django 4.1 on 2023-03-17 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0010_alter_business_info_fav_icon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vitals',
            name='Department',
            field=models.CharField(default='Nursing Department', max_length=50),
        ),
        migrations.AddField(
            model_name='vitals',
            name='Status',
            field=models.CharField(default='Waiting', max_length=50),
        ),
    ]
