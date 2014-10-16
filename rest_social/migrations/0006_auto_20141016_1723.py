# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_social', '0005_comment_related_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='airshiptoken',
            name='user',
        ),
        migrations.DeleteModel(
            name='AirshipToken',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='reporter',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.AlterUniqueTogether(
            name='notificationsetting',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='notificationsetting',
            name='user',
        ),
        migrations.DeleteModel(
            name='NotificationSetting',
        ),
    ]
