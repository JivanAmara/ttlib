# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-07 14:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='minfreq11',
            name='recording',
        ),
        migrations.DeleteModel(
            name='MinFreq11',
        ),
    ]
