# descending red or green candles.
# candles which use prevoous candles.
import os.path
import sys

import requests
from django.core.management.base import BaseCommand, CommandError
from backend.models import *


class Command(BaseCommand):
    help = 'Find Long Bar & Long Shadow Candles '

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # get exchange info
        tf = {
            "1m": "1",
            "5m": "5",
            "3m": "3",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "6h": "360",
            "12h": "720",
            "1d": "1D",
            "3d": "3D",
            "1w": "1W",
            "1M": "1M",
        }

        for p in Symbol.objects.all():
            for t in TimeFrame.objects.all():
                # print(t.timeframe)
                latest_server_timestamp = \
                    requests.get("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=1").json()[
                        0][0]

                base_url = "https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit=1000&startTime=".format(
                    symbol=p.symbol, timeframe=t.timeframe)
                if p.stype.symbol_type == 'futures':
                    base_url = "https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit=1000&startTime=".format(
                        symbol=p.symbol, timeframe=t.timeframe)
                stype_o = SymbolType.objects.get(symbol_type=p.stype.symbol_type)
                try:
                    sym_o = Symbol.objects.get(symbol=p.symbol.upper(), stype=stype_o)
                    ohlcv_data = OHLCV.objects.filter(symbol=sym_o, tf__timeframe=t.timeframe)
                    if ohlcv_data.count() == 0:
                        latest_timestamp_available_in_database = 0
                    else:
                        latest_timestamp_available_in_database = ohlcv_data.order_by('-open_time')[1:2][0].open_time
                        #print(latest_timestamp_available_in_database)

                    finished = False

                    if latest_server_timestamp > latest_timestamp_available_in_database:
                        while not finished:
                            self.stdout.write(self.style.SUCCESS(
                                'Fetching new data start from {}'.format(latest_timestamp_available_in_database)))
                            bulk_klines = []
                            bulk_update = []

                            # print(base_url + str(latest_timestamp_available_in_database))
                            data = requests.get(
                                base_url + str(latest_timestamp_available_in_database)).json()

                            # print(data)
                            atidb = ohlcv_data.values_list('open_time')
                            available_timestamps_in_database = []
                            for i in atidb:
                                available_timestamps_in_database.append(i[0])

                            for idx, item in enumerate(data):
                                # print(data)
                                # print(item)
                                open_time, kopen, khigh, klow, kclose, volume, close_time, qvolume, x, x2, x3, x4 = item
                                # check if the candle is in database or not.
                                #candle = OHLCV.objects.get(open_time=open_time,tf__timeframe=t.timeframe)
                                #print()

                                if open_time in available_timestamps_in_database:

                                    try:
                                        x = OHLCV.objects.get(symbol=sym_o,
                                                          tf=TimeFrame.objects.get_or_create(timeframe=t.timeframe)[0],
                                                          open_time=int(open_time))
                                        x.kopen = float(kopen)
                                        x.khigh = float(khigh)
                                        x.klow = float(klow)
                                        x.kclose = float(kclose)
                                        x.volume = float(volume)
                                        x.qvolume = float(qvolume)
                                        x.close_time = int(close_time)
                                        x.save()
                                    except Exception as e:
                                        print(e)
                                        print(open_time)
                                        x = OHLCV.objects.filter(symbol=sym_o,
                                                              tf=TimeFrame.objects.get_or_create(timeframe=t.timeframe)[
                                                                  0],
                                                              open_time=int(open_time))
                                        x[0].delete()
                                else:
                                    bulk_klines.append(
                                        OHLCV(
                                            symbol=sym_o,
                                            tf=TimeFrame.objects.get_or_create(timeframe=t.timeframe)[0],
                                            open_time=int(open_time),
                                            kopen=float(kopen),
                                            khigh=float(khigh),
                                            klow=float(klow),
                                            kclose=float(kclose),
                                            volume=float(volume),
                                            qvolume=float(qvolume),
                                            close_time=int(close_time)
                                        )
                                    )
                            OHLCV.objects.bulk_create(bulk_klines, batch_size=500)
                            #OHLCV.objects.bulk_update(bulk_update,
                            #                         ['kopen', 'klow', 'kclose', 'khigh', 'volume', 'qvolume'])
                            latest_timestamp_available_in_database = data[-1][0]
                            # print(len(data))
                            if len(data) < 999:
                                finished = True


                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
