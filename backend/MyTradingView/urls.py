"""MyTradingView URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/1.0/', include('api.v10.urls')),
    path('api/1.1/', include('api.v11.urls')),
    #path('config', views.config),
    #path('time', views.time),
    #path('symbols', views.symbols),
    #path('search', views.search),
    #path('history', views.history),
    #path('marks', views.marks),
    #path('quotes', views.quotes),
    #path('timescale_marks', views.timescale_marks),
    path('symbol_info', views.symbol_info),
    path('fapi/v1/klines', views.future_klines),
    path('allklines', views.future_klines_all),
    path('api/v3/klines', views.spot_klines),
    #path('update_database', views.update_database),
    path('get_levels', views.get_levels),
    path('get_trex_info', views.get_trex_info),
    path('get_atr_data', views.get_atr_data),
    path("fapi/v1/exchangeInfo",views.exchangeinfo_futures)
]
