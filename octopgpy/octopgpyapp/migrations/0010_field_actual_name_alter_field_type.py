# Generated by Django 4.0.6 on 2022-07-15 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octopgpyapp', '0009_alter_field_name_alter_field_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='actual_name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='field',
            name='type',
            field=models.CharField(blank=True, choices=[('text', 'text'), ('integer', 'integer'), ('numeric', 'numeric'), ('timestamp', 'timestamp')], default='text', max_length=30, null=True),
        ),
    ]