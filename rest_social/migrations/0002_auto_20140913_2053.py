# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_social_providers(apps, schema_editor):
    SocialProvider = apps.get_model("rest_social", "SocialProvider")
    SocialProvider.objects.create(name="facebook")
    SocialProvider.objects.create(name="twitter")

class Migration(migrations.Migration):

    dependencies = [
        ('rest_social', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_social_providers),
    ]
