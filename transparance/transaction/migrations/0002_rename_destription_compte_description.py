# Generated by Django 5.1.1 on 2024-09-06 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compte',
            old_name='destription',
            new_name='description',
        ),
    ]