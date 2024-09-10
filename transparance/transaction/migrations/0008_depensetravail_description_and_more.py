# Generated by Django 5.1.1 on 2024-09-09 11:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0007_alter_travail_date_fin'),
    ]

    operations = [
        migrations.AddField(
            model_name='depensetravail',
            name='description',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='montantpayetravail',
            name='description',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]