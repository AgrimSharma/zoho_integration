# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-15 12:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zohobasic', '0010_auto_20190115_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='created_time',
            field=models.DateField(blank=True, null=True),
        ),
    ]
