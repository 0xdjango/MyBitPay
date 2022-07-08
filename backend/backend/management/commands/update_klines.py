# descending red or green candles.
# candles which use prevoous candles.
import os.path
import sys
from contextlib import closing
from io import StringIO

import numpy as np
import pandas as pd
import requests
from django.core.management.base import BaseCommand, CommandError
from backend.models import *
import pandas_ta as ta

# make backup of all items.
backup_directory = ".\\kline_backup\\"
def zc(src, retVal):
    # print(np.where(src == 0, 0, retVal))
    return pd.DataFrame(np.where(src == 0, 0, retVal))


def in_memory_csv(data):
    """Creates an in-memory csv.

    Assumes `data` is a list of dicts
    with native python types."""

    mem_csv = StringIO()
    pd.DataFrame(data).to_csv(mem_csv, index=False)
    mem_csv.seek(0)
    return mem_csv


# return percent difference from price change and current price
def diff_percent(source_price, price_change):
    return price_change / source_price * 100


def crypto_atr(src):
    df = pd.DataFrame()
    df['atr5'] = ta.rma(src, 5)
    df['atr11'] = ta.rma(src, 11)
    df['atr22'] = ta.rma(src, 22)
    df['atr45'] = ta.rma(src, 45)
    df['atr91'] = ta.rma(src, 91)
    df['atr182'] = ta.rma(src, 182)
    df['atr364'] = ta.rma(src, 364)
    df['divNum1'] = zc(df['atr364'], 13) + zc(df['atr182'], 8) + zc(df['atr91'], 5) + \
                    zc(df['atr45'], 3) + zc(df['atr22'], 2) + zc(df['atr11'], 1) + zc(df['atr5'], 1)
    df['f_atr'] = (df['atr364'] * 13 + df['atr182'] * 8 + df['atr91'] * 5 + df['atr45'] * 3 + df['atr22'] * 2 + df[
        'atr11'] * 1 + df['atr5'] * 1) / df['divNum1']
    return df['f_atr']


def get_add_to_list(timeframe, symbol, startTime):
    data = []
    resume = True
    while resume:
        base_url = "https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit=1000&startTime=".format(
            symbol=symbol, timeframe=timeframe)
        d = requests.get(base_url + str(startTime)).json()
        for g in d:
            data.append(g)
        startTime = d[-1][0]
        print(startTime)
        if len(d) < 999:
            resume = False
    return data

tfs = {

}
for x in TimeFrame.objects.all():
    tfs[x.timeframe] = x.id
syms = {}
for y in Symbol.objects.all():
    syms[y.symbol.upper()] = y.id


"""
1. find latest time stamp on db
2. find latest time stamp on server
3. get new bars from sever and append to database bars ( and specify starting timestamp of newdata )
4. calculate atr & atr24 to dataframe  
5. 

"""
class Command(BaseCommand):
    help = 'Update Local Data base from Binance Servers.'

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
        # get latest item from db
        #remove latest item
        # get new candles
        # add candles.
        for p in Symbol.objects.all():
            for t in TimeFrame.objects.all():
                if t.timeframe not in []:
                    print(p, t)
                    # print(t.timeframe)
                    latest_server_timestamp = \
                        requests.get(
                            "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=1").json()[
                            0][0]

                    stype_o = SymbolType.objects.get(symbol_type=p.stype.symbol_type)
                    try:
                        sym_o = Symbol.objects.get(symbol=p.symbol.upper(), stype=stype_o)
                        ohlcv_data = OHLCV.objects.filter(symbol=sym_o, tf__timeframe=t.timeframe)
                        # at first delete latest item ( incomplete )
                        ohlcv_data.order_by('-open_time')[0:1][0].delete()
                        if ohlcv_data.count() == 0:
                            latest_timestamp_available_in_database = 0
                        else:
                            latest_timestamp_available_in_database = ohlcv_data.order_by('-open_time')[0:1][0].open_time
                            # print(latest_timestamp_available_in_database)

                        if latest_server_timestamp > latest_timestamp_available_in_database:
                            self.stdout.write(self.style.SUCCESS(
                                'Fetching new data start from {}'.format(latest_timestamp_available_in_database)))
                            new_data = get_add_to_list(t.timeframe, p.symbol, latest_timestamp_available_in_database)
                            df = pd.DataFrame(
                                list(ohlcv_data.values('symbol__symbol', 'open_time', 'kopen', 'khigh', 'klow',
                                                       'kclose', 'volume', 'atr', 'tf__timeframe','atr24')))

                            df_new_data = pd.DataFrame(new_data)
                            df_new_data.columns = ['open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                                                   'close_time', 'qvolume', 'x', 'x2', 'x3', 'x4']
                            # remove unnecessary fields
                            del df_new_data["close_time"]
                            del df_new_data["qvolume"]
                            del df_new_data["x"]
                            del df_new_data["x2"]
                            del df_new_data["x3"]
                            del df_new_data["x4"]

                            df_new_data['atr'] = -1
                            df_new_data['atr24'] = -1
                            df_new_data['symbol__symbol'] = p.id
                            df_new_data['tf__timeframe'] = t.id

                            df = df.append(df_new_data, ignore_index=True)
                            src = ta.true_range(high=df.khigh.astype(float), low=df.klow.astype(float), close=df.kclose.astype(float), drift=1).fillna(
                                value=np.nan).fillna(0)
                            df["atr24"] = ta.rma(src, 24)
                            df["atr24"] = df["atr24"].fillna(0)
                            df["atr"] = crypto_atr(src)
                            df["atr"] = df["atr"].fillna(0)

                            not_in_db_df = df[df['open_time'] >= latest_timestamp_available_in_database]
                            not_in_db_df = not_in_db_df.rename(
                                columns={'tf__timeframe': 'tf', 'symbol__symbol': 'symbol'})
                            not_in_db_df['symbol'] = p.id
                            not_in_db_df['tf'] = t.id
                            print(p.symbol, "data selected.")
                            mem_csv = StringIO()
                            """not_in_db_df.to_csv("test.csv",
                                                columns=['symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow',
                                                         'kclose', 'volume',
                                                         "atr", "atr24"],
                                                line_terminator='\n', index=False)
                            """
                            not_in_db_df.to_csv(mem_csv,
                                     columns=['symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                                              "atr", "atr24"],
                                     line_terminator='\n', index=False)
                            mem_csv.seek(0)
                            self.stdout.write(self.style.SUCCESS(
                                'Writing new data to database, {} new rows'.format(len(not_in_db_df.index))))
                            with closing(mem_csv) as csv_io:
                                OHLCV.objects.from_csv(csv_io)
                            '''for idx, item in enumerate(new_data):
                                print(idx, "/", len(new_data), end="\r")
                                open_time, kopen, khigh, klow, kclose, volume, close_time, qvolume, x, x2, x3, x4 = item
                                i = {
                                    "symbol__symbol": p.symbol,
                                    'open_time': open_time,
                                    'kopen': kopen,
                                    'khigh': khigh,
                                    'klow': klow,
                                    'kclose': kclose,
                                    'volume': volume,
                                    'atr': -1,
                                    'tf__timeframe': t.timeframe
                                }
                                df = df.append(i, ignore_index=True)
                            '''

                            # ohlcv_data = OHLCV.objects.filter(symbol__symbol=p.symbol)

                            # total = ohlcv_data.count()
                            # data_string = 'ts,open,high,low,close,volume,atr,tf\n'
                            #not_in_db_df = not_in_db_df.rename(columns={'tf__timeframe': 'tf', 'symbol__symbol': 'symbol'})
                            #df_new_data = df_new_data.rename(columns={'tf__timeframe': 'tf', 'symbol__symbol': 'symbol'})
                            #df.to_csv(os.path.join(backup_directory,p.symbol.upper() + "_" + t.timeframe + "_.json"), sep=',', index=False,
                            #          line_terminator='\n')
                            # write new data to database.

                            #not_in_db_df.to_csv("new_data_"+p.symbol.upper() + "_" + t.timeframe + "_.json",
                            #          sep=',', index=False,
                            #          line_terminator='\n')
                            # import ohlcv from csv using postgres copy


                            '''bulk_klines = []
                            # print(data)
                            atidb = ohlcv_data.values_list('open_time')
                            available_timestamps_in_database = []
                            for i in atidb:
                                available_timestamps_in_database.append(i[0])
    
                            for idx, item in enumerate(new_data):
                                # print(data)
                                # print(item)
                                open_time, kopen, khigh, klow, kclose, volume, close_time, qvolume, x, x2, x3, x4 = item
                                # check if the candle is in database or not.
                                # candle = OHLCV.objects.get(open_time=open_time,tf__timeframe=t.timeframe)
                                # print()
                                print(idx, "/", len(new_data), end="\r")
                                if open_time in enumerate(available_timestamps_in_database):
    
                                    try:
                                        x = OHLCV.objects.get(symbol=sym_o,
                                                              tf=TimeFrame.objects.get_or_create(timeframe=t.timeframe)[
                                                                  0],
                                                              open_time=int(open_time))
                                        x.kopen = float(kopen)
                                        x.khigh = float(khigh)
                                        x.klow = float(klow)
                                        x.kclose = float(kclose)
                                        x.volume = float(volume)
                                        x.save()
                                    except Exception as e:
                                        print(e)
                                        print(open_time)
                                        x = OHLCV.objects.filter(symbol=sym_o,
                                                                 tf=
                                                                 TimeFrame.objects.get_or_create(timeframe=t.timeframe)[
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
                                        )
                                    )
                            OHLCV.objects.bulk_create(bulk_klines, batch_size=500)
                            '''
                            """if t.timeframe not in ["1m"]:
                                all_klines = OHLCV.objects.filter(symbol=sym_o, tf__timeframe=t.timeframe).order_by("open_time")
                                df = pd.DataFrame(list(all_klines.values()))
            
                                df.columns = ['id', 'symbol_id', 'tf_id', 'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                                              "qvolume", "close_time", "atr_value"]
                                src = ta.true_range(high=df.High, low=df.Low, close=df.Close, drift=1).fillna(
                                    value=np.nan).fillna(0)
                                df["matr_" + t.timeframe] = crypto_atr(src)
                                df["matr_" + t.timeframe] = df["matr_" + t.timeframe].fillna(0)
                                bulk_update = []
                                total = all_klines.count()
                                for idx, q in enumerate(all_klines):
                                    print(str(idx)+"/"+str(total),end="\r")
                                    temp_atr = df.loc[df["id"] == q.id]['matr_' + t.timeframe].tolist()[0]
                                    try:
                                        float(temp_atr)
                                    except Exception as e:
                                        temp_atr = 0
                                    q.atr = temp_atr
                                    #print(q.atr)
                                    bulk_update.append(q)
                                #print(bulk_update[0].atr,bulk_update[0].id,bulk_update[0].open_time)
                                OHLCV.objects.bulk_update(bulk_update,['atr'],batch_size=500)"""
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
