# descending red or green candles.
# candles which use prevoous candles.
import os.path

from django.core.management.base import BaseCommand, CommandError
from backend.models import *
import glob
tfs = {
            "1m": "1",
            "5m": "5",
            "3m": "3",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "8h" : "480",
            "6h": "360",
            "12h": "720",
            "1d": "1D",
            "3d": "3D",
            "1w": "1W",
            "1M": "1M",
        }

class Command(BaseCommand):
    help = 'load csv files into database'

    def add_arguments(self, parser):
        parser.add_argument('folder', nargs='+', type=str)

    def handle(self, *args, **options):
        # get exchange info
        folder_name = options['folder'][0]
        files = glob.glob(os.path.join(folder_name,"*.csv"))
        for i in files:
            filename = os.path.basename(i)
            sname,tf,garb,garb2 =filename.split('-')
            sym_o, sym_c = Symbol.objects.get_or_create(symbol=sname.upper())
            sym_type_o, sym_type_c = SymbolType.objects.get_or_create(
                symbol_type='futures'
            )
            tzone_o, tzone_c = TimeZone.objects.get_or_create(name="UTC")
            if sym_c:
                sym_o.exchange_listed = sname.upper()
                sym_o.exchange_traded = sname.upper()
                sym_o.ticker = sname.upper()
                sym_o.stype = sym_type_o
                sym_o.timezone = tzone_o
                sym_o.save()

            if os.path.exists(i):
                self.stdout.write(self.style.SUCCESS('Reading {}...'.format(i)))
                with open(i, "r") as f:
                    time_values = []
                    klines = f.read().splitlines()
                    tf_o, tf_c = TimeFrame.objects.get_or_create(timeframe=tfs[tf])
                    t=OHLCV.objects.filter(symbol=sym_o,tf=tf_o).values_list('open_time')
                    for i in t:
                        time_values.append(i[0])
                    bulk_klines = []
                    self.stdout.write(self.style.SUCCESS('Preparing {} Klines for add to DB.'.format(len(klines))))
                    total = len(klines)
                    for idx, item in enumerate(klines):
                        open_time, kopen, khigh, klow, kclose, volume, close_time, qvolume, x, x2, x3, x4 = item.replace(
                            '"', '').replace("'", '').split(',')
                        if open_time not in time_values:
                            print(idx, "/", total, end="\r")
                            bulk_klines.append(
                                OHLCV(
                                    symbol=sym_o,
                                    tf=tf_o,
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
                    self.stdout.write(self.style.SUCCESS('Adding {} Klines to DB.'.format(str(len(bulk_klines)))))
                    OHLCV.objects.bulk_create(bulk_klines, batch_size=500)
