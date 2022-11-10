# Generated by Django 4.0.6 on 2022-07-15 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('octopgpyapp', '0011_rename_actual_name_field_descriptive_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CTE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='octopgpyapp.document')),
                ('parent_cte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='octopgpyapp.cte')),
            ],
        ),
        migrations.CreateModel(
            name='CTEFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('agg', models.CharField(choices=[('sum', 'sum'), ('avg', 'avg')], max_length=30)),
                ('cte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='octopgpyapp.cte')),
            ],
        ),
    ]