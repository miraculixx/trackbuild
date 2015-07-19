# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackbuild', '0004_auto_20150718_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='previous',
            field=models.ForeignKey(to='trackbuild.Release', null=True),
        ),
    ]
