# Generated by Django 4.1 on 2023-03-22 06:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0041_alter_modalities_options_alter_requisition_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='business_info',
            options={'verbose_name': 'Business Detail'},
        ),
        migrations.AlterModelOptions(
            name='procedures',
            options={'verbose_name': 'Procedure'},
        ),
        migrations.AlterModelOptions(
            name='referring_facilities',
            options={'verbose_name': 'Referring Facilitie'},
        ),
    ]
