from django.db import models
from postgres_copy import CopyManager

# Create your models here.
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class SymbolType(models.Model):
    # type ["stock", "stock", "index"]
    symbol_type = models.CharField(max_length=200)

    def __str__(self):
        return self.symbol_type


class TimeZone(models.Model):
    name = models.CharField(max_length=200)  # “America/New_York”


class Symbol(models.Model):
    symbol = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=600)
    exchange_listed = models.CharField(max_length=100, default="")
    exchange_traded = models.CharField(max_length=100, default="")
    minmovement = models.FloatField(default=0.01)
    minmovement2 = models.FloatField(default=0.01)
    fractional = models.BooleanField(default=True)
    pricescale = models.IntegerField(default=1, help_text="1")
    has_dwm = models.BooleanField(default=True)
    has_intraday = models.BooleanField(default=True)
    has_no_volume = models.BooleanField(default=True)
    stype = models.ForeignKey("SymbolType", on_delete=models.CASCADE, null=True)  # original parameter : type
    ticker = models.CharField(max_length=200)
    timezone = models.ForeignKey("TimeZone", on_delete=models.CASCADE, null=True)
    session_regular = models.CharField(max_length=200, help_text="24x7", default="24x7")

    def __str__(self):
        return self.ticker + ":" + self.symbol


class TimeFrame(models.Model):
    timeframe = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.timeframe


class OHLCV(models.Model):
    symbol = models.ForeignKey("Symbol", on_delete=models.CASCADE)
    tf = models.ForeignKey("TimeFrame", on_delete=models.CASCADE)
    open_time = models.BigIntegerField(db_index=True)
    kopen = models.FloatField()
    khigh = models.FloatField()
    klow = models.FloatField()
    kclose = models.FloatField()
    volume = models.FloatField()
    atr = models.FloatField(default=-1)
    atr24 = models.FloatField(default=-1, null=True)
    xhash = models.CharField(max_length=254, null=True, unique=True)
    objects = CopyManager()

    def __str__(self):
        return self.symbol.symbol + ":" + self.tf.timeframe + ":" + str(self.open_time)

    class Meta:
        indexes = [models.Index(fields=['open_time', ]), ]


class Config(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=900)
    supports_search = models.BooleanField(default=False)
    supports_group_request = models.BooleanField(default=False)
    supported_resolutions = models.ManyToManyField("TimeFrame")
    supports_marks = models.BooleanField(default=True)
    supports_timescale_marks = models.BooleanField(default=False)


class NewStudy(models.Model):
    name = models.CharField(max_length=251)
    description = models.CharField(max_length=2000)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    ticker_name = models.CharField(max_length=50)
    symbol = models.ForeignKey("Symbol", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.ticker_name


class Indicator(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class IndicatorValue(models.Model):
    indicator_name = models.ForeignKey("Indicator", on_delete=models.CASCADE)
    value = models.FloatField(default=-12345678, null=True)
    ohlcv_candle = models.ForeignKey("OHLCV", on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}:{}:{}".format(self.indicator_name, self.ohlcv_candle.symbol.symbol,
                                    self.ohlcv_candle.tf.timeframe, self.value)
