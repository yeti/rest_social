# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social', '0003_auto_20140926_0403'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='share',
            unique_together=set([('user', 'content_type', 'object_id', 'id')]),
        ),
    ]
