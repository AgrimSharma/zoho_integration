# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-14 11:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zohobasic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokens',
            name='access_token',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tokens',
            name='code',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tokens',
            name='refresh_token',
            field=models.TextField(max_length=100),
        ),
    ]
