# Generated by Django 5.1.7 on 2025-05-03 08:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_payment_orderplaced'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderplaced',
            name='ordered_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
