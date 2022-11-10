# Generated by Django 4.0.6 on 2022-07-15 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('octopgpyapp', '0008_alter_field_is_calculated_alter_field_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='field',
            name='type',
            field=models.CharField(blank=True, choices=[('text', 'text'), ('int', 'int'), ('numeric', 'numeric'), ('timestamp', 'timestamp')], default='text', max_length=30, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together={('name', 'document')},
        ),
    ]
