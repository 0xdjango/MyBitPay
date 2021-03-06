# Generated by Django 4.0.4 on 2022-07-05 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SymbolType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol_type', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TimeFrame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeframe', models.CharField(max_length=3, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=600)),
                ('exchange_listed', models.CharField(default='', max_length=100)),
                ('exchange_traded', models.CharField(default='', max_length=100)),
                ('minmovement', models.FloatField(default=0.01)),
                ('minmovement2', models.FloatField(default=0.01)),
                ('fractional', models.BooleanField(default=True)),
                ('pricescale', models.IntegerField(default=1, help_text='1')),
                ('has_dwm', models.BooleanField(default=True)),
                ('has_intraday', models.BooleanField(default=True)),
                ('has_no_volume', models.BooleanField(default=True)),
                ('ticker', models.CharField(max_length=200)),
                ('session_regular', models.CharField(default='24x7', help_text='24x7', max_length=200)),
                ('stype', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.symboltype')),
                ('timezone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.timezone')),
            ],
        ),
        migrations.CreateModel(
            name='OHLCV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_time', models.BigIntegerField(db_index=True)),
                ('kopen', models.FloatField()),
                ('khigh', models.FloatField()),
                ('klow', models.FloatField()),
                ('kclose', models.FloatField()),
                ('volume', models.FloatField()),
                ('atr', models.FloatField(default=-1)),
                ('atr24', models.FloatField(default=-1, null=True)),
                ('xhash', models.CharField(max_length=254, null=True, unique=True)),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.symbol')),
                ('tf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.timeframe')),
            ],
        ),
        migrations.CreateModel(
            name='NewStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=251)),
                ('description', models.CharField(max_length=2000)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('ticker_name', models.CharField(max_length=50)),
                ('symbol', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.symbol')),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=-12345678, null=True)),
                ('indicator_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.indicator')),
                ('ohlcv_candle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.ohlcv')),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=900)),
                ('supports_search', models.BooleanField(default=False)),
                ('supports_group_request', models.BooleanField(default=False)),
                ('supports_marks', models.BooleanField(default=True)),
                ('supports_timescale_marks', models.BooleanField(default=False)),
                ('supported_resolutions', models.ManyToManyField(to='backend.timeframe')),
            ],
        ),
    ]
