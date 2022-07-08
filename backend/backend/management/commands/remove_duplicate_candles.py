# descending red or green candles.
# candles which use prevoous candles.
import os.path
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Func, Value
import requests
from django.core.management.base import BaseCommand, CommandError
from backend.models import *
from django.db.models import Max
import sys
from django.db.models import Count
import pandas as pd


def get_missing_ids(symbol, tf, missing_items):
    symbol_obj = Symbol.objects.get(symbol=symbol)
    timeframe_obj = TimeFrame.objects.get(timeframe=tf)
    result = []
    while len(missing_items)>1:
        #print(len(missing_items))
        url = "https://fapi.binance.com/fapi/v1/klines?symbol={}&interval={}&limit=1000&startTime=".format(symbol.upper(),tf,missing_items[0])
        data = requests.get(url).json()
        for item in data:
            #result.append(item) # ts open high low close volume
            result.append(
                OHLCV(
                    symbol=symbol_obj,
                    tf=timeframe_obj,
                    open_time=item[0],
                    kopen=item[1],
                    khigh=item[2],
                    klow=item[3],
                    kclose=item[4],
                    volume=item[5],
                )
            )
        open_times = [x[0] for x in data]
        missing_items = list(set(missing_items)-set(open_times))
    return result


class Command(BaseCommand):
    help = 'fix all reptitive candles with newest one.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for symbol in Symbol.objects.all():
            for tf in TimeFrame.objects.all():
                try:
                    print(symbol.symbol,"=>",tf)

                    df = pd.DataFrame(list(OHLCV.objects.filter(symbol=symbol, tf=tf).values()))
                    df.columns=['id','symbol_id','tf_id','open_time','kopen','khigh','klow','kclose','volume','atr','atr24','xhash']

                    #duplicate_ids = (OHLCV.objects.filter(symbol=symbol, tf=tf).values('open_time').annotate(ids=ArrayAgg('id')).annotate(c=Func('ids', Value(1), function='array_length')).filter(c__gt=1).annotate(ids=Func('ids', function='unnest')).values_list('ids', flat=True))


                    #duplicate_entries = OHLCV.objects.filter(symbol=symbol, tf=tf).values('open_time','tf__timeframe','symbol__symbol').annotate(count=Count('id')).filter(count__gt=1)
                    #duplicate_objects = OHLCV.objects.filter(open_time__in=[item['open_time'] for item in duplicate_entries])
                    print(duplicate_ids)


                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)