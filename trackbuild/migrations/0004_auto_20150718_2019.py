# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('trackbuild', '0003_buildcounter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='build',
            old_name='count',
            new_name='buildno',
        ),
        migrations.AlterField(
            model_name='build',
            name='buildid',
            field=models.CharField(default=uuid.uuid4, max_length=100),
        ),
    ]
