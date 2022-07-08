# descending red or green candles.
# candles which use prevoous candles.
import os.path
import requests
from django.core.management.base import BaseCommand, CommandError
from backend.models import *
from django.core import management


class Command(BaseCommand):
    help = 'Update Local Data base from Binance Servers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # get exchange info
        symbols = Symbol.objects.all()
        timeframes = [5, 15, 30]
        for symbol in symbols:
            for tf in timeframes:
                management.call_command('update_klines', symbol, tf, symbol.stype.symbol_type, verbosity=0,
                                        interactive=False)
