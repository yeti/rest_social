# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social', '0004_auto_20140926_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='related_tags',
            field=models.ManyToManyField(to='rest_social.Tag', null=True, blank=True),
            preserve_default=True,
        ),
    ]
