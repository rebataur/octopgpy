# Generated by Django 4.0.4 on 2022-04-25 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octopgpyapp', '0003_remove_field_test_alter_field_calculation_func_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='calculation_func_args',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
