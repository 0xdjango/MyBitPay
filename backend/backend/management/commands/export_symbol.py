# descending red or green candles.
# candles which use prevoous candles.
import os.path
import sys
import pandas as pd
import datetime

from django.core.management.base import BaseCommand, CommandError
from backend.models import *


class Command(BaseCommand):
    help = 'Export database to files.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        #df = pd.DataFrame(list(OHLCV.objects.all().values()))
        #df = pd.DataFrame(list(OHLCV.objects.filter(date__gte=datetime.datetime(2012, 5, 1)).values()))

        # limit which fields


        for t in Symbol.objects.all():
            #print(options['symbol'][0])
            df = pd.DataFrame(list(OHLCV.objects.filter(symbol=t).values('symbol__symbol','open_time', 'kopen', 'khigh','klow', 'kclose','volume', 'atr','tf__timeframe')))
            print(t.symbol,"data selected.")
                #ohlcv_data = OHLCV.objects.filter(symbol__symbol=p.symbol)

                #total = ohlcv_data.count()
                #data_string = 'ts,open,high,low,close,volume,atr,tf\n'
            df.to_csv(t.symbol.upper() +".json", sep=',', index=False)
            print("OK.")
