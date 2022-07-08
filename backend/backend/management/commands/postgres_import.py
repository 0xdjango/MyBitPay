# descending red or green candles.
# candles which use prevoous candles.
import os.path
from contextlib import closing
from io import StringIO

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from backend.models import *
def in_memory_csv(data):
    """Creates an in-memory csv.

    Assumes `data` is a list of dicts
    with native python types."""

    mem_csv = StringIO()
    pd.DataFrame(data).to_csv(mem_csv, index=False)
    mem_csv.seek(0)
    return mem_csv
tfs = {

}
for x in TimeFrame.objects.all():
    tfs[x.timeframe] = x.id
syms = {}
for y in Symbol.objects.all():
    syms[y.symbol.upper()] = y.id


class Command(BaseCommand):
    help = 'load_data postgres copy'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        # get exchange info
        filename = options['filename'][0]
        if os.path.exists(filename):
            self.stdout.write(self.style.SUCCESS('Reading {}...'.format(filename)))
            x = pd.read_csv(filename)
            x.columns = ['symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                         "atr", "atr24","xhash"]
            x = x.sort_values(by='open_time')
            #print(x['xhash'].duplicated())

            mem_csv = StringIO()

            x['symbol'] = syms[x['symbol'].tolist()[-1]]
            x['tf'] = tfs[x.tf.tolist()[-1]]
            x.to_csv(mem_csv,
                      columns=['symbol', 'tf', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume',
                               "atr", "atr24","xhash"],
                      line_terminator='\n', index=False)
            mem_csv.seek(0)
            with closing(mem_csv) as csv_io:
                OHLCV.objects.from_csv(csv_io)
            #x['tf__timeframe'] = x['tf__timeframe'].map(tfs)
            #x['symbol__symbol'] = x['symbol__symbol'].map(syms)
            #x = x.rename(columns={'tf__timeframe': 'tf', 'symbol__symbol': 'symbol'})
            #with open("TmpFileName.name", "w") as output:
            #    output.write(
            #        x.to_csv(columns=['symbol', 'open_time', 'kopen', 'khigh', 'klow', 'kclose', 'volume', 'atr', 'tf'],
            #                 line_terminator='\n', index=False))
            #OHLCV.objects.from_csv("TmpFileName.name")
            self.stdout.write(self.style.SUCCESS('Added OK.'))
