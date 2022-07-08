from django.contrib import admin
from backend.models import *
import copy
# Register your models here.
class OHLCVAdmin(admin.ModelAdmin):
    list_filter = ['symbol__symbol','tf__timeframe']
    search_fields = ['open_time']

admin.site.register(OHLCV,OHLCVAdmin)

class IndicatorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Indicator,IndicatorAdmin)

class IndicatorValueAdmin(admin.ModelAdmin):
    readonly_fields = ['ohlcv_candle']
    list_filter = ['ohlcv_candle__tf','ohlcv_candle__symbol',"ohlcv_candle__khigh","ohlcv_candle__klow"]
admin.site.register(IndicatorValue,IndicatorValueAdmin)
admin.site.register(Symbol)
admin.site.register(TimeFrame)
admin.site.register(SymbolType)
admin.site.register(TimeZone)
class NewStudyAdmin(admin.ModelAdmin):
    actions = ['build_new_study']
    def build_new_study(self,request,queryset):
        obj = queryset[0]
        symbol_object,symbol_c = Symbol.objects.get_or_create(
            symbol=obj.name,
            description=obj.symbol.symbol,
            exchange_listed=obj.symbol.symbol,
            exchange_traded=obj.symbol.symbol,
            stype=SymbolType.objects.get_or_create(symbol_type='TestStudy')[0],
            ticker = obj.name
        )
        print(obj.symbol.symbol)
        print(int(obj.end_date.timestamp()*1000))
        print(int(obj.start_date.timestamp()*1000))
        ohlcv_objects = OHLCV.objects.filter(symbol__symbol__exact=obj.symbol.symbol,open_time__gte=int(obj.start_date.timestamp()*1000),
                                             open_time__lte=int(obj.end_date.timestamp()*1000))
        queries = []
        #print(ohlcv_objects.count())
        for item in ohlcv_objects:
            x = OHLCV(
                    symbol=Symbol.objects.get(symbol=obj.name),
                    tf = item.tf,
                    open_time = item.open_time,
                    kopen = item.kopen,
                    khigh = item.khigh,
                    klow = item.klow,
                    kclose = item.kclose,
                    volume = item.volume,
                    qvolume = item.qvolume,
                    close_time = item.close_time,

            )
            queries.append(x)
        
        
        OHLCV.objects.bulk_create(queries,batch_size=500)
        
        """for item in ohlcv_objects:
            queries.append(
                OHLCV(
                    open_time=item.open_time,
                    tf = item.tf,
                    symbol=symbol_object,
                    kopen=item.kopen,
                    khigh=item.khigh,
                    klow=item.klow,
                    kclose = item.kclose,
                    volume=item.volume,
                    qvolume=item.qvolume,
                    close_time = item.close_time

                )
            )
        """
        #print(len(queries))

        #OHLCV.objects.bulk_create(queries)



admin.site.register(NewStudy,NewStudyAdmin)