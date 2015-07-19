# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackbuild', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('release', 'buildid')]),
        ),
    ]
