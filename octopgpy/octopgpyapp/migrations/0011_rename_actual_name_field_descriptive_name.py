# Generated by Django 4.0.6 on 2022-07-15 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('octopgpyapp', '0010_field_actual_name_alter_field_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='field',
            old_name='actual_name',
            new_name='descriptive_name',
        ),
    ]