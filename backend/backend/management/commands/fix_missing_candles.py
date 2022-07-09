# descending red or green candles.
# candles which use prevoous candles.
from os import remove
import os.path
import requests
from django.core.management.base import BaseCommand, CommandError
from backend.models import *
from django.db.models import Max
import sys
import hashlib

def get_missing_ids(symbol, tf, missing_items):
    try:
        symbol_obj = Symbol.objects.get(symbol=symbol)
        timeframe_obj = TimeFrame.objects.get(timeframe=tf)
        result = []
        finished = False
        while not finished:
            print("remaining items: ",len(missing_items),end="\r")
            first_len = len(missing_items)
            url = "https://fapi.binance.com/fapi/v1/klines?symbol={}&interval={}&limit=1000&startTime={}".format(symbol.upper(),tf,missing_items[0])
            print(url)
            data = requests.get(url).json()
            if len(data)!=0:
                for idx,item in enumerate(data):
                    #result.append(item) # ts open high low close volume
                    x=tf+symbol +str(item[0])
                    
                    if(item[0] in missing_items):
                        #print(item)
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
                                xhash=hashlib.sha256(x.encode()).hexdigest()    
                            )
                        )
                        missing_items.remove(item[0])
                    #print(first_len, len(missing_items))
                    if(first_len == len(missing_items)):
                        finished = True
            else:
                finished = True
            if len(missing_items)==0:
                finished= True

                
            #print(s"+str(len(missing_items)),end="\r")
        return result
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



tfs = {"1m":1 ,
        "5m": 5,
        "3m": 3,
        "15m": 15,
        "30m": 30,
        "1h":60 ,
        "2h":120,
        "4h":240,
        "8h":480,
        "6h":360,
       "12h":720,
       "1d":1440,
}
class Command(BaseCommand):
    help = 'fix all reptitive candles with newest one.'
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for symbol in Symbol.objects.all():
            for tf in TimeFrame.objects.all():
                try:
                    print(symbol.symbol,"=>",tf)
                    all_ohlcv = OHLCV.objects.filter(symbol__symbol=symbol.symbol).filter(tf__timeframe=tf.timeframe)
                    all_ohlcv.latest('open_time').delete()
                    open_times = list(all_ohlcv.values_list('open_time',flat=True))

                    first_timestamp_in_db = min(open_times)
                    step = open_times[2]-open_times[1]
                    #print(step)
                    calculated_timestamps = []
                    calculated_timestamps.append(first_timestamp_in_db)
                    url = "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval={}&limit=1".format(tf.timeframe)
                    last_timestamp_server = requests.get(url).json()[0][0]
                    while first_timestamp_in_db <= last_timestamp_server:
                        first_timestamp_in_db += step
                        calculated_timestamps.append(first_timestamp_in_db)
                    dif = set(calculated_timestamps) - set(open_times)
                    print("Missing Candles Count {}".format(len(list(dif))))
                    objects = get_missing_ids(symbol.symbol,tf.timeframe,list(dif))
                    OHLCV.objects.bulk_create(objects,batch_size=500,ignore_conflicts=True)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)