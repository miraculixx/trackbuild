# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackbuild', '0002_auto_20150718_1936'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildCounter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('release', models.ForeignKey(related_name='buildcounter', to='trackbuild.Release')),
            ],
        ),
    ]
