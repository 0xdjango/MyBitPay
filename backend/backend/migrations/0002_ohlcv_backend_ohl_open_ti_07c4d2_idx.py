# Generated by Django 4.0.4 on 2022-07-05 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='ohlcv',
            index=models.Index(fields=['open_time'], name='backend_ohl_open_ti_07c4d2_idx'),
        ),
    ]
