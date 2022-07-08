import datetime
from datetime import timezone

import numpy as np
import pandas as pd
import pandas_ta as ta
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse

from backend.models import Symbol, OHLCV, TimeFrame

# based on minutes
custom_timeframes = [
    '2',
    '3',
    '4'
]


# convert 1m kline to multiplier minutes timeframe.
def split_list(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


def m1to(kline_items, multiplier):
    first_datetime = datetime.datetime.fromtimestamp(kline_items[0][0] / 1000.0, tz=datetime.timezone.utc)
    start_of_day = first_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    print(start_of_day.timestamp() * 1000)
    time_pointer = int(start_of_day.timestamp() * 1000)
    first_candle_found = False
    while not first_candle_found:
        timestamp_arrays = [int(x[0]) for x in kline_items]
        if int(time_pointer) in timestamp_arrays:
            # it means we are the start of a proposed minutes ( multiplier * 1m)
            # remove previous candles for correct formatting of candles.
            kline_items = kline_items[timestamp_arrays.index(int(time_pointer)):]
            first_candle_found = True

        else:
            time_pointer += int(multiplier) * 60 * 1000  # add
    print(len(kline_items))
    # find first timestamp of a given series based on 00 time of day.
    result_kline = []
    data = split_list(kline_items, int(multiplier))
    # print(len(list(data)))
    for new_kline_item in data:
        # print(new_kline_item)
        # import time
        # time.sleep(5)
        result = [
            float(new_kline_item[0][0]),
            float(new_kline_item[0][1]),
            max([float(x[2]) for x in new_kline_item]),
            min([float(x[3]) for x in new_kline_item]),
            float(new_kline_item[-1][4]),
            sum([float(x[5]) for x in new_kline_item]),
        ]
        # we just need to update low high close and volume => timestamp and open is unchanged
        # ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', "", "", "", "", "", ""]
        """for i in new_kline_item[1:]:
            result[2] = max(float(result[2]),float(i[2]))
            result[3] = min(float(result[3]),float(i[3]))
            result[4] = float(i[4])
            result[5]  =float(result[5])+float(i[5])
        """
        # print(result)
        result_kline.append(result)

    # df = pd.DataFrame(result_kline)
    # df.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    return result_kline


def config(request):
    response_data = {}
    response_data['supports_search'] = True
    response_data['supports_group_request'] = False
    response_data['supports_marks'] = True
    response_data['supports_timescale_marks'] = True
    response_data['supports_time'] = True
    response_data['supported_resolutions'] = ["1S", "5S", "30S", "1", "2", "5", "15", "60", "240", "1D", "3D", "1W",
                                              "1M"]
    response_data['exchanges'] = []
    response_data['exchanges'].append({"value": "", "name": "All Exchanges", "desc": ""})
    response_data['exchanges'].append({"value": "Binance", "name": "Binance", "desc": ""})
    response_data['symbols_types'] = [
        {"name": "All types", "value": ""},
        {"name": "Stock", "value": "stock"},
        {"name": "Crypto", "value": "Crypto"}
    ]
    return JsonResponse(response_data)


def symbol_info(request, group_name):
    response_data = {}
    all_symbols = Symbol.objects.all()
    response_data['symbol'] = [x.symbol for x in all_symbols]
    response_data['exchange-traded'] = [x.exchange_traded for x in all_symbols]
    response_data['exchange-listed'] = [x.exchange_listed for x in all_symbols]
    response_data['timezone'] = "UTC"
    response_data['minmov'] = 1
    response_data['minmov2'] = 0
    response_data['fractional'] = [x.fractional for x in all_symbols]
    response_data['pointvalue'] = 1
    response_data['session'] = "24x7"
    response_data['has_intraday'] = [x.has_intraday for x in all_symbols]
    response_data['has_no_volume'] = [x.has_no_volume for x in all_symbols]
    response_data['description'] = [x.description for x in all_symbols]
    response_data['type'] = [x.stype.symbol_type for x in all_symbols]
    response_data['exchange'] = "Binance"
    response_data['intraday_multipliers'] = []
    response_data['has_seconds'] = False
    response_data['seconds_multipliers'] = []
    response_data['listed_exchange'] = "Binance"
    response_data['supported_resolutions'] = ["1S", "5S", "30S", "1", "2", "5", "15", "60", "240", "1D", "3D", "1W",
                                              "1M"]
    response_data['pricescale'] = [10, 100]
    response_data['has_daily'] = False
    response_data['has_weekly_and_monthly'] = False
    response_data['has_empty_bars'] = False
    response_data['force_session_rebuild'] = True
    response_data['volume_precision'] = 0
    response_data['data_status'] = "streaming"
    response_data['expired'] = False
    response_data['expiration_date'] = 177777777
    response_data['sector'] = "Crypto"
    response_data['industry'] = "Crypto"
    response_data['currency_code'] = "Crypto"
    response_data['ticker'] = [x.ticker for x in all_symbols]

    return JsonResponse(response_data)


def symbols(request, symbol="BTCUSDT"):
    symbol_data = Symbol.objects.get(symbol=symbol.upper())
    response_data = {}
    response_data['name'] = symbol_data.symbol
    response_data['exchange-traded'] = symbol_data.exchange_traded
    response_data['exchange-listed'] = symbol_data.exchange_listed
    response_data['timezone'] = symbol_data.timezone.name
    response_data['minmov'] = symbol_data.minmovement
    response_data['minmov2'] = symbol_data.minmovement2
    response_data['fractional'] = symbol_data.fractional
    # response_data['pointvalue'] = symbol_data['pointvalue']
    response_data['session'] = "24x7"
    response_data['has_intraday'] = symbol_data.has_intraday
    response_data['has_no_volume'] = symbol_data.has_no_volume
    response_data['description'] = symbol_data.description
    response_data['type'] = symbol_data.stype.symbol_type
    # response_data['exchange'] = symbol_data['exchange']
    # response_data['intraday_multipliers'] = symbol_data['has_intraday']
    # response_data['has_seconds'] = False
    # response_data['seconds_multipliers'] = False
    # response_data['listed_exchange'] = "Binance"
    response_data['supported_resolutions'] = ["1S", "5S", "30S", "1", "2", "5", "15", "60", "240", "1D", "3D", "1W",
                                              "1M"]
    response_data['pricescale'] = symbol_data.pricescale
    response_data['has_daily'] = False
    response_data['has_weekly_and_monthly'] = False
    response_data['has_empty_bars'] = False
    response_data['force_session_rebuild'] = True
    response_data['volume_precision'] = 0
    response_data['data_status'] = "streaming"
    response_data['expired'] = False
    response_data['expiration_date'] = 177777777
    response_data['sector'] = "Crypto"
    response_data['industry'] = "Crypto"
    response_data['currency_code'] = "Crypto"
    response_data['ticker'] = symbol_data.ticker

    return JsonResponse(response_data)


def search(request):
    query = request.GET.get('query')
    r = Symbol.objects.filter(symbol__icontains=query)

    response_data = []
    temp_data = {}
    for item in r:
        temp_data['symbol'] = item.symbol
        temp_data['full_name'] = item.ticker
        temp_data['description'] = item.description
        temp_data['exchange'] = item.exchange_listed
        temp_data['type'] = item.stype.symbol_type
        temp_data['ticker'] = item.ticker
    response_data.append(temp_data)

    return JsonResponse(response_data, safe=False)


def history(request):
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
        "1M": "1M"
    }
    symbol = request.GET.get('symbol')
    time_from = request.GET.get('from')
    time_to = request.GET.get('to')
    resolution = request.GET.get('resolution')
    data = OHLCV.objects.filter(symbol__symbol=symbol, open_time__gt=time_from * 1000, open_time__lt=time_to * 1000,
                                tf__timeframe=tfs[resolution])
    open_list = [x.kopen for x in data]
    high_list = [x.khigh for x in data]
    low_list = [x.klow for x in data]
    close_list = [x.kclose for x in data]
    volume_list = [x.volume for x in data]
    open_time_list = [x.open_time for x in data]
    return JsonResponse({"t": open_time_list,
                         "o": open_list,
                         "h": high_list,
                         "l": low_list,
                         "c": close_list,
                         "v": volume_list,
                         "s": "ok"})


def quotes(request):
    tickers = request.GET.get('symbols').upper().split(',')
    res = {
        "s": "ok",
        "d": [
            {
                "s": "ok",
                "n": "NYSE:AA",
                "v": {
                    "ch": "+0.16",
                    "chp": "0.98",
                    "short_name": "AA",
                    "exchange": "NYSE",
                    "description": "Alcoa Inc. Common",
                    "lp": "16.57",
                    "ask": "16.58",
                    "bid": "16.57",
                    "open_price": "16.25",
                    "high_price": "16.60",
                    "low_price": "16.25",
                    "prev_close_price": "16.41",
                    "volume": "4029041"
                }
            },
            {
                "s": "ok",
                "n": "NYSE:F",
                "v": {
                    "ch": "+0.15",
                    "chp": "0.89",
                    "short_name": "F",
                    "exchange": "NYSE",
                    "description": "Ford Motor Company",
                    "lp": "17.02",
                    "ask": "17.03",
                    "bid": "17.02",
                    "open_price": "16.74",
                    "high_price": "17.08",
                    "low_price": "16.74",
                    "prev_close_price": "16.87",
                    "volume": "7713782"
                }
            }
        ]
    }
    return JsonResponse(res, safe=False)


def marks(request, symbol, time_from, time_to, resolution):
    return JsonResponse([], safe=False)


def time(request):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    return JsonResponse(utc_timestamp, safe=False)


def timescale_marks(request, symbol, time_from, time_to, resolution):
    return JsonResponse([], safe=False)


def news(request):
    return HttpResponse('Hello Django')


def futuresmag(request):
    return HttpResponse('Hello Django')


def future_klines(request):
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
        "1M": "1M"
    }
    try:
        symbol = request.GET.get('symbol')
    except Exception as e:
        return JsonResponse({'error': 'symbol parameter needed.'}, safe=False)
    try:
        interval = request.GET.get('interval')
    except Exception as e:
        return JsonResponse({'error': 'interval parameter needed.'}, safe=False)
    # try:
    #    limit = request.GET.get('limit')
    # except Exception as e:
    #    limit=1000
    try:
        startTime = request.GET.get('startTime')
    except Exception as e:
        return JsonResponse({'error': 'startTime parameter needed.'}, safe=False)
    try:
        endTime = request.GET.get('endTime')
    except Exception as e:
        return JsonResponse({'error': 'endTime parameter needed.'}, safe=False)
    # custom time frames are calculated based on 1m data.
    if interval not in ['2', '4']:
        candles = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe=tfs[interval],
            open_time__gte=startTime,
            open_time__lte=endTime
        ).order_by('open_time')  # this little fix save my life ! tradingview need ordered data based on timestamp => .order_by('open_time')
    else:
        candles = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe="1m",
            open_time__gte=startTime,
            open_time__lte=endTime
        ).order_by('open_time') # this little fix save my life ! tradingview need ordered data based on timestamp => .order_by('open_time')
    klines = []
    for item in candles:
        candle_type = ""
        candle_type24=""
        candle_range = (item.khigh-item.klow)
        candle_body = abs(item.kopen - item.kclose)
        candle_shadow=candle_range - candle_body
        if candle_range>2.4*item.atr24 and candle_body>candle_shadow:
            candle_type24 = "spikebar24"
        if candle_range > 2.4 * item.atr24 and candle_body < candle_shadow:
            candle_type24 = "spikeshadow24"
        elif 1.2*item.atr24<candle_range<2.4*item.atr24 and candle_body>candle_shadow:
            candle_type24 = "longbar24"
        elif 1.2 * item.atr24 < candle_range < 2.4 * item.atr24 and candle_body < candle_shadow:
            candle_type24 = "longshadow24"
        elif 0.8*item.atr24<candle_range<1.2*item.atr24:
            candle_type24="master"


        if candle_range>2.4*item.atr and candle_body>candle_shadow:
            candle_type = "spikebar"
        if candle_range > 2.4 * item.atr and candle_body < candle_shadow:
            candle_type = "spikeshadow"
        elif 1.2*item.atr<candle_range<2.4*item.atr and candle_body>candle_shadow:
            candle_type = "longbar"
        elif 1.2 * item.atr < candle_range < 2.4 * item.atr and candle_body < candle_shadow:
            candle_type = "longshadow"
        elif 0.8*item.atr<candle_range<1.2*item.atr:
            candle_type="master"
        klines.append(
            [
                item.open_time,
                item.kopen,
                item.khigh,
                item.klow,
                item.kclose,
                item.volume,
                item.atr,
                item.atr24,
                candle_type,
                candle_type24
            ]
        )
    # if interval not in ['1', '2', '3', '4', '5']:
    #    res = klines
    # else:
    #    res = m1to(klines,interval)

    result = JsonResponse(klines, safe=False)

    return result
    # return JsonResponse({'code': "{} candles available.".format(candles.count())}, safe=False)


def spot_klines(request):
    return JsonResponse([], safe=False)


def zc(src, retVal):
    # print(np.where(src == 0, 0, retVal))
    return pd.DataFrame(np.where(src == 0, 0, retVal))


# return percent difference from price change and current price
def diff_percent(source_price, price_change):
    return price_change / source_price * 100


def crypto_atr(src):
    df = pd.DataFrame()
    # df['DataFrame Column'] = df['DataFrame Column'].fillna(0)
    df['atr5'] = ta.rma(src, 5)
    df['atr11'] = ta.rma(src, 11)
    df['atr22'] = ta.rma(src, 22)
    df['atr45'] = ta.rma(src, 45)
    df['atr91'] = ta.rma(src, 91)
    df['atr182'] = ta.rma(src, 182)
    df['atr364'] = ta.rma(src, 364)

    # print(df.tail(20))
    df['divNum1'] = zc(df['atr364'], 13) + zc(df['atr182'], 8) + zc(df['atr91'], 5) + \
                    zc(df['atr45'], 3) + zc(df['atr22'], 2) + zc(df['atr11'], 1) + zc(df['atr5'], 1)

    df['f_atr'] = (df['atr364'] * 13 + df['atr182'] * 8 + df['atr91'] * 5 + df['atr45'] * 3 + df['atr22'] * 2 + df[
        'atr11'] * 1 + df['atr5'] * 1) / df['divNum1']

    return df['f_atr']

    # tr = ta.true_range(high=df.High, low=df.Low, close=df.Close, drift=1)
    # atr = ta.ma("rma", tr, length=l)

def get_trex_info_range(request):
    result = {
        '1m': "",
        '5m': "",
        '15m': "",
        '1h': "",
        '4h': "",
        '1d': "",
        '1w': "",
        'shadow': ""
    }

    main_timeframes = ["1", "5", "15", "60", "240", "D", "1W"]
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "D": "1d",
        "3D": "3d",
        "1W": "1w",
    }

    try:
        symbol = request.GET.get('symbol')
    except Exception as e:
        return JsonResponse({'error': 'symbol parameter needed.'}, safe=False)
    try:
        interval = request.GET.get('interval')
    except Exception as e:
        return JsonResponse({'error': 'interval parameter needed.'}, safe=False)
    try:
        endTime = request.GET.get('endTime')
    except Exception as e:
        return JsonResponse({'error': 'endTime parameter needed.'}, safe=False)

    for timeframe_item in main_timeframes:
        candles = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe=tfs[timeframe_item],
            open_time__gte=0,
            open_time__lte=endTime
        ).order_by('-id')[:20000][::-1]

        klines = []
        for item in candles:
            if timeframe_item == interval:
                if item.kopen > item.kclose:
                    result["shadow"] = max(item.khigh - item.kopen, item.kclose - item.klow)
                else:
                    result["shadow"] = max(item.khigh - item.kclose, item.kopen - item.klow)
            klines.append(
                [
                    item.open_time,
                    item.kopen,
                    item.khigh,
                    item.klow,
                    item.kclose,
                    item.volume,
                    item.close_time,
                    item.qvolume,
                    "",
                    "",
                    "",
                    ""
                ]
            )

        df = pd.DataFrame(klines)
        df.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', "", "", "", "", "", ""]
        df["atr_" + tfs[timeframe_item]] = crypto_atr(
            ta.true_range(high=df.High, low=df.Low, close=df.Close, drift=1).fillna(value=np.nan).fillna(0))

        result[tfs[timeframe_item]] = str(df["atr_" + tfs[timeframe_item]].tolist()[-1])
        print(timeframe_item, interval)
        if timeframe_item == interval:
            result['current_atr'] = str(df["atr_" + tfs[timeframe_item]].tolist()[-1])

    return JsonResponse(result, safe=False)


# we optimize this function with just limiting time frames (5m,15m,1h,4h,1d)
def get_atr_data(request):
    result = {
        '1m': "",
        '3m': "",
        '5m': "",
        '15m': "",
        '30m': "",
        '1h': "",
        '2h': "",
        '4h': "",
        '6h': "",
        '12h': "",
        '1d': "",
        '3d':"",
        '1w': "",
        '1M': ""
    }
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
    }

    try:
        symbol = request.GET.get('symbol')
    except Exception as e:
        return JsonResponse({'error': 'symbol parameter needed.'}, safe=False)
    try:
        interval = request.GET.get('interval')
    except Exception as e:
        return JsonResponse({'error': 'interval parameter needed.'}, safe=False)
    try:
        endTime = request.GET.get('endTime')
    except Exception as e:
        return JsonResponse({'error': 'endTime parameter needed.'}, safe=False)

    for timeframe_item in tfs:
        candle = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe=tfs[timeframe_item],
            open_time__lte=endTime
        ).order_by('open_time').reverse()[0]  # get last item in query
        if timeframe_item == interval:
            result['current_atr'] = candle.atr
            result['upper_shadow'] = candle.khigh - max(candle.kopen,candle.kclose)
            result['lower_shadow'] = min(candle.kopen,candle.kclose) - candle.klow
            result['body'] = abs(candle.kopen - candle.kclose)
        result[tfs[timeframe_item]] = candle.atr
    return JsonResponse(result, safe=False)
def get_trex_info(request):
    result = {
        '1m': "",
        '5m': "",
        '15m': "",
        '1h': "",
        '4h': "",
        '1d': "",
        '1w': "",
        'shadow': ""
    }

    main_timeframes = ["1", "5", "15", "60", "240", "D", "1W"]
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "D": "1d",
        "3D": "3d",
        "1W": "1w",
    }

    try:
        symbol = request.GET.get('symbol')
    except Exception as e:
        return JsonResponse({'error': 'symbol parameter needed.'}, safe=False)
    try:
        interval = request.GET.get('interval')
    except Exception as e:
        return JsonResponse({'error': 'interval parameter needed.'}, safe=False)
    try:
        endTime = request.GET.get('endTime')
    except Exception as e:
        return JsonResponse({'error': 'endTime parameter needed.'}, safe=False)

    for timeframe_item in main_timeframes:
        candles = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe=tfs[timeframe_item],
            open_time__gte=0,
            open_time__lte=endTime
        ).order_by('-id')[:20000][::-1]

        klines = []
        for item in candles:
            if timeframe_item == interval:
                if item.kopen > item.kclose:
                    result["shadow"] = max(item.khigh - item.kopen, item.kclose - item.klow)
                else:
                    result["shadow"] = max(item.khigh - item.kclose, item.kopen - item.klow)
            klines.append(
                [
                    item.open_time,
                    item.kopen,
                    item.khigh,
                    item.klow,
                    item.kclose,
                    item.volume,
                    item.close_time,
                    item.qvolume,
                    "",
                    "",
                    "",
                    ""
                ]
            )

        df = pd.DataFrame(klines)
        df.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', "", "", "", "", "", ""]
        df["atr_" + tfs[timeframe_item]] = crypto_atr(
            ta.true_range(high=df.High, low=df.Low, close=df.Close, drift=1).fillna(value=np.nan).fillna(0))

        result[tfs[timeframe_item]] = str(df["atr_" + tfs[timeframe_item]].tolist()[-1])
        print(timeframe_item,interval)
        if timeframe_item == interval:
            result['current_atr'] = str(df["atr_" + tfs[timeframe_item]].tolist()[-1])

    return JsonResponse(result, safe=False)


def update_database(request):
    try:

        symbol = request.GET.get('symbol')

        symbol_obj = Symbol.objects.get(symbol=symbol.upper())
        tf = request.GET.get('tf')

        tf_obj = TimeFrame.objects.get(timeframe=tf)
        ktime = request.GET.get('time')
        kopen = request.GET.get('open')
        khigh = request.GET.get('high')
        klow = request.GET.get('low')
        kclose = request.GET.get('close')
        kvolume = request.GET.get('volume')
        oh_o, oh_c = OHLCV.objects.update_or_create(
            symbol=symbol_obj,
            tf=tf_obj,
            open_time=ktime,
        )
        oh_o.kopen = float(kopen)
        oh_o.khigh = float(khigh)
        oh_o.klow = float(klow)
        oh_o.kclose = float(kclose)
        oh_o.volume = float(kvolume)
        oh_o.save()
        return JsonResponse({'ok': 'symbol parameter udpated.'}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False)


def exchangeinfo_futures(request):
    response_data = {}
    temp_data = {"symbols": []}
    for sym in Symbol.objects.all():
        temp_data["symbols"].append(
            {
                'symbol': sym.symbol,
                'name' : sym.symbol,
                'full_name' : sym.symbol,
                'exchange-traded' : sym.exchange_traded,
                'exchange-listed' : sym.exchange_listed,
                'timezone' : sym.timezone.name,
                'minmov' : sym.minmovement,
                'minmov2' : sym.minmovement2,
                'fractional' : sym.fractional,
                # response_data['pointvalue'] = symbol_data['pointvalue']
                'session' : "24x7",
                'has_intraday' : sym.has_intraday,
                'has_no_volume' : sym.has_no_volume,
                'description' : sym.description,
                'type' : sym.stype.symbol_type,
                # response_data['intraday_multipliers'] = symbol_data['has_intraday']
                # response_data['has_seconds'] = False
                # response_data['seconds_multipliers'] = False
                # response_data['listed_exchange'] = "Binance"
                'pricescale' : sym.pricescale,
                'has_daily' : False,
                'has_weekly_and_monthly' : False,
                'has_empty_bars' : False,
                'force_session_rebuild' : True,
                'volume_precision' : 0,
                'data_status' : "streaming",
                'expired' : False,
                'expiration_date' : 177777777,
                'sector' : "Crypto",
                'industry' : "Crypto",
                'currency_code' : "Crypto",
                'ticker' : sym.ticker,
                }

        )

    return JsonResponse(temp_data, safe=False)


def get_levels(request):
    tfs = {
        "1": "1m",
        "5": "5m",
        "3": "3m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
        "1M": "1M"
    }
    response_data = {
        'data': []
    }
    symbol = request.GET.get('symbol')
    limit = int(request.GET.get('limit'))
    if limit is None:
        limit = 10
    timeframe = tfs[request.GET.get('timeframe')]  # 1M,1w,1d,4h
    result = []
    symbol_obj = Symbol.objects.get(symbol=symbol.upper())
    tf_obj = TimeFrame.objects.get(timeframe=timeframe)
    if timeframe in ['1M', '1w', '1d', '4h']:
        monthly_levels = OHLCV.objects.filter(symbol=symbol_obj, tf=tf_obj).order_by('open_time')
        print(monthly_levels)
        open_times = list(monthly_levels.values_list('open_time', flat=True))
        for item in monthly_levels:
            if open_times.count(item.open_time) > 1:
                last_id = monthly_levels.filter(open_time=item.open_time).latest('id')
                it = monthly_levels.get(id=last_id.id)

                result.append("{}:{}".format(it.open_time, it.kopen))
                result.append("{}:{}".format(it.open_time, it.khigh))
                result.append("{}:{}".format(it.open_time, it.klow))
                result.append("{}:{}".format(it.open_time, it.kclose))
            if open_times.count(item.open_time) == 1:
                it = item
                result.append("{}:{}".format(it.open_time, it.kopen))
                result.append("{}:{}".format(it.open_time, it.khigh))
                result.append("{}:{}".format(it.open_time, it.klow))
                result.append("{}:{}".format(it.open_time, it.kclose))
            result.reverse()
        response_data['data'] = list(set(result[5:limit * 3]))
    return JsonResponse(response_data, safe=False)


def future_klines_all(request):
    tfs = {
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "480": "8h",
        "360": "6h",
        "720": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
        "1M": "1M"
    }
    try:
        symbol = request.GET.get('symbol')
    except Exception as e:
        return JsonResponse({'error': 'symbol parameter needed.'}, safe=False)
    try:
        interval = request.GET.get('interval')
    except Exception as e:
        return JsonResponse({'error': 'interval parameter needed.'}, safe=False)

    if interval not in ['1', '3', '5']:
        candles = OHLCV.objects.filter(
            symbol__symbol__exact=symbol,
            tf__timeframe=tfs[interval]
        )

        klines = []
        for item in candles:
            klines.append(
                [
                    item.open_time,
                    item.kopen,
                    item.khigh,
                    item.klow,
                    item.kclose,
                    item.volume,
                    item.close_time,
                    item.qvolume,
                    "",
                    "",
                    "",
                    "",
                    item.atr
                ]
            )
        # if interval not in ['1', '2', '3', '4', '5']:
        #    res = klines
        # else:
        #    res = m1to(klines,interval)

        result = JsonResponse(klines, safe=False)

        return result
    # return JsonResponse({'code': "{} candles available.".format(candles.count())}, safe=False)
