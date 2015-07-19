# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackbuild', '0005_release_previous'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='previous',
            field=models.ForeignKey(related_name='followers', to='trackbuild.Release', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('user', 'product', 'name', 'major', 'minor', 'patch')]),
        ),
    ]
