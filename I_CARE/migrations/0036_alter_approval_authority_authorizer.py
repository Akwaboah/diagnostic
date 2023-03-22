# Generated by Django 4.1 on 2023-03-22 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('I_CARE', '0035_approval_authority_requisition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval_authority',
            name='Authorizer',
            field=models.ForeignKey(db_column='Authorizer', on_delete=django.db.models.deletion.CASCADE, to='I_CARE.user_details'),
        ),
    ]
