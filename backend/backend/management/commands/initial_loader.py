# descending red or green candles.
# candles which use prevoous candles.
import os.path

from django.core.management.base import BaseCommand, CommandError
from backend.models import *


class Command(BaseCommand):
    help = 'load 1m chart into database.'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        # get exchange info
        filename = options['filename'][0]
        symbol = filename.split('.')[0]

        sym_o, sym_c = Symbol.objects.get_or_create(symbol=symbol.upper())

        if os.path.exists(filename):
            self.stdout.write(self.style.SUCCESS('Reading {}...'.format(filename)))
            with open(filename, "r") as f:
                klines = f.read().splitlines()[1:]
                bulk_klines = []
                self.stdout.write(self.style.SUCCESS('Preparing {} Klines for add to DB.'.format(len(klines))))
                total = len(klines)
                for idx, item in enumerate(klines):
                    open_time, kopen, khigh, klow, kclose, volume, atr, tf = item.split(',')
                    print(idx, "/", total, end="\r")
                    bulk_klines.append(
                        OHLCV(
                            symbol=sym_o,
                            tf=TimeFrame.objects.get(timeframe=tf),
                            open_time=int(open_time),
                            kopen=float(kopen),
                            khigh=float(khigh),
                            klow=float(klow),
                            kclose=float(kclose),
                            volume=float(volume),
                            atr=float(atr),
                        )
                    )
                self.stdout.write(self.style.SUCCESS('Adding {} Klines to DB.'.format(str(len(bulk_klines)))))
                OHLCV.objects.bulk_create(bulk_klines, batch_size=2000)
