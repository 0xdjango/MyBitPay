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

backup_directory = ".\\kline_backup_atr\\"


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

        for p in Symbol.objects.all():
            for t in TimeFrame.objects.all():
                print(p.symbol, t.timeframe)
                if t.timeframe not in []:
                    all_klines = OHLCV.objects.filter(symbol=p, tf__timeframe=t.timeframe).order_by("open_time")
                    df = pd.DataFrame(list(all_klines.values()))

                    df.columns = ['id', 'symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                                  "atr", "atr24"]
                    src = ta.true_range(high=df.khigh, low=df.klow, close=df.kclose, drift=1).fillna(
                        value=np.nan).fillna(0)
                    df["atr24"] = ta.rma(src, 24)
                    df["atr24"] = df["atr24"].fillna(0)
                    df["matr"] = crypto_atr(src)
                    df["matr"] = df["matr"].fillna(0)
                    mem_csv = StringIO()

                    df.to_csv(mem_csv,
                              columns=['symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                                       "atr", "atr24"],
                              line_terminator='\n', index=False)
                    mem_csv.seek(0)
                    self.stdout.write(self.style.SUCCESS(p.symbol + " " + t.timeframe + ' Saved to memory OK.'))
                    self.stdout.write(self.style.SUCCESS('Importing OK.'))
                    with closing(mem_csv) as csv_io:
                        OHLCV.objects.from_csv(csv_io)
                    self.stdout.write(self.style.SUCCESS('Finished Importing.'))

                    """bulk_update = []
                    total = all_klines.count()

                    for idx, q in enumerate(all_klines):
                        print(str(idx) + "/" + str(total), end="\r")
                        temp_atr = df.loc[df["id"] == q.id]['matr_' + t.timeframe].tolist()[0]
                        try:
                            float(temp_atr)
                        except Exception as e:
                            temp_atr = 0
                        q.atr = temp_atr
                        # print(q.atr)
                        bulk_update.append(q)
                    # print(bulk_update[0].atr,bulk_update[0].id,bulk_update[0].open_time)
                    OHLCV.objects.bulk_update(bulk_update, ['atr'], batch_size=500)"""
