# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-16 05:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zohobasic', '0012_timesheet'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('end_date', models.CharField(blank=True, max_length=100, null=True)),
                ('sequence', models.CharField(blank=True, max_length=100, null=True)),
                ('start_date', models.CharField(blank=True, max_length=100, null=True)),
                ('flag', models.CharField(blank=True, max_length=100, null=True)),
                ('id_string', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zohobasic.Projects')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zohobasic.Tasks')),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'Time Sheet',
                'verbose_name_plural': 'Time Sheet',
            },
        ),
    ]
