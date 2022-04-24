# Generated by Django 4.0.4 on 2022-04-23 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('child_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sub_child', to='octopgpyapp.document')),
            ],
        ),
        migrations.CreateModel(
            name='Func',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('body', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Param',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('paramtype', models.CharField(max_length=30)),
                ('func', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='octopgpyapp.func')),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('test', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=30)),
                ('is_calculated', models.CharField(max_length=30)),
                ('calculation_func', models.CharField(max_length=30)),
                ('calculation_func_args', models.JSONField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='octopgpyapp.document')),
            ],
        ),
    ]
