# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('df_order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('trade_id', models.CharField(null=True, unique=True, max_length=100, blank=True)),
                ('order', models.ForeignKey(to='df_order.OrderInfo')),
            ],
        ),
    ]
