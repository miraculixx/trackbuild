# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('buildid', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=100)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['updated'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('major', models.IntegerField()),
                ('minor', models.IntegerField()),
                ('patch', models.IntegerField()),
                ('product', models.ForeignKey(related_name='releases', to='trackbuild.Product')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'product', 'name'],
            },
        ),
        migrations.AddField(
            model_name='build',
            name='release',
            field=models.ForeignKey(related_name='builds', to='trackbuild.Release'),
        ),
        migrations.AddField(
            model_name='build',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('user', 'product')]),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('user', 'name')]),
        ),
    ]
