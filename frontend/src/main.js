// Datafeed implementation, will be added later
import Datafeed from './datafeed.js';
import {
    makeApiRequest,
    generateSymbol,
    parseFullSymbol,
} from './helpers.js';

function atr(high, low, close, window) {
    let tr = trueRange(high, low, close);
    return ema(tr, 2 * window - 1);
}

function trueRange(high, low, close) {
    let tr = [high[0] - low[0]];
    for (let i = 1, len = low.length; i < len; i++) {
        tr.push(Math.max(high[i] - low[i], Math.abs(high[i] - close[i - 1]), Math.abs(low[i] - close[i - 1])));
    }
    return tr;
}

function mean(series) {
    let sum = 0;
    for (let i = 0; i < series.length; i++) {
        sum += series[i];
    }
    return sum / series.length;
}

function rolling(operation, series, window) {
    let result = [];
    for (let i = 0, len = series.length; i < len; i++) {
        let j = i + 1 - window;
        result.push(operation(series.slice((j > 0) ? j : 0, i + 1)));
    }
    return result;
}

function sma(series, window) {
    return rolling((s) => mean(s), series, window);
}

function ema(series, window, start) {
    let weight = 2 / (window + 1);
    let ema = [start ? start : mean(series.slice(0, window))];
    for (let i = 1, len = series.length; i < len; i++) {
        ema.push(series[i] * weight + (1 - weight) * ema[i - 1]);
    }
    return ema;
}

function rma(sseries, window, start) {
    let weight = 1 / window;
    let rma = [start ? start : mean(sseries.slice(0, window))];
    for (let i = 1, len = sseries.length; i < len; i++) {
        rma.push(sseries[i] * weight + (1 - weight) * rma[i - 1]);
    }
    return rma;
}

//  functions
function zc(src, retVal) {
    let zc_series = []
    for (let i = 0; i < src.length; i++) {
        if (src[i] == 0) {
            zc_series.push(0)
        } else {
            zc_series.push(retVal)
        }

    }
    return zc_series
}

function nz(src) {
    let nz_series = []
    for (let i = 0; i < src.length; i++) {
        if (isNaN(src[i])) {
            nz_series.push(0)
        } else {
            nz_series.push(src[i])
        }

    }
    return nz_series
}

/*function pine_rma(x, length) {
    let alpha = 1/length
    let initial_value = [0.0]
    let sum = []
    for (let i = 0 ; i < x.length; i++) {
        if(i==0){
           sum.push(
               alpha * x[i]
           )
            console.log(alpha*x[i])
        }
        else {
            sum.push(alpha * x[i] + (1 - alpha) * nz(sum[i-1]))
        }
    }
    return sum

}
*/
function avg_atr_Crypto(src) {
    var atr5 = nz(rma(src, 5))
    //console.log(atr5)
    var atr11 = nz(rma(src, 11))
    //console.log(atr11)
    var atr22 = nz(rma(src, 22))
    //console.log(atr22)
    var atr45 = nz(rma(src, 45))
    //console.log(atr45)
    var atr91 = nz(rma(src, 91))
    //console.log(atr91)
    var atr182 = nz(rma(src, 182))
    //console.log(atr182)
    var atr364 = nz(rma(src, 364))
    //console.log(atr364)
    let div_num_series = []
    let fatr_series = []
    for (let i = 0; i < src.length; i++) {
        div_num_series.push(
            zc(atr364, 13)[i] + zc(atr182, 8)[i] + zc(atr91, 5)[i] + zc(atr45, 3)[i] + zc(atr22, 2)[i] + zc(atr11, 1)[i] + zc(atr5, 1)[i]
        )

    }
    for (let i = 0; i < div_num_series.length; i++) {
        fatr_series.push(
            (atr364[i] * 13 + atr182[i] * 8 + atr91[i] * 5 + atr45[i] * 3 + atr22[i] * 2 + atr11[i] * 1 + atr5[i] * 1) / div_num_series[i]
        )

    }


    return fatr_series

}

function autosave() {
    tvWidget.saveChartToServer()
}

setInterval(autosave, 60000);

let Shape = new Array();
var LastTimeLocation;

window.tvWidget = new TradingView.widget({

    symbol: 'BTCUSDT', // default symbol
    favorites: {
        intervals: ["1", "15", "60", "240", "1D", "3D"],
    },
    theme: "Light",

    interval: '240', // default interval
    fullscreen: true, // displays the chart in the fullscreen mode
    container: 'tv_chart_container',
    datafeed: Datafeed,
    debug: true,
    library_path: '../charting_library_clonned_data/charting_library/',
    charts_storage_url: "http://localhost:8000/api",
    client_id: 'localtradingview2',
    charts_storage_api_version: "1.1",
    user_id: 'bahman2',
    enabled_features: ['use_localstorage_for_settings', 'side_toolbar_in_fullscreen_mode'],
    auto_save_delay: 5,
    load_last_chart: true,
    widgetbar: {
        watchlist: true,
        watchlist_settings: {
            default_symbols: ["BTCUSDT:BTCUSDT", "ETHUSDT:ETHUSDT"],
            readonly: false
        },
        news: false,
        datawindow: false,
    }





});


tvWidget.onChartReady(function () {

    var button = tvWidget.createButton();
    button.setAttribute('title', 'This button save current middle of  chart location.');
    button.addEventListener('click', function () {
        var all_shapes = tvWidget.chart().getAllShapes();
        all_shapes.forEach(element => {
            if (element.name == 'date_range') {

                var date_range = tvWidget.activeChart().getShapeById(element.id).getPoints();
                var start_range = Math.min(date_range[0].time, date_range[1].time);
                var end_range = Math.max(date_range[0].time, date_range[1].time);
                tvWidget.activeChart().setVisibleRange(
                    {
                        from: parseInt(start_range),
                        to: parseInt(end_range)
                    }
                )
                //button.setAttribute('title', start_range+":"+end_range);
                //console.log(start_range,end_range);
            }
        });
        //var trange = tvWidget.activeChart().getVisibleRange() ;
        //var middle = (trange.from + trange.to)/2;
        //button.setAttribute('title', middle);
    });
    //button.addEventListener('click', function() { tvWidget.activeChart().setVisibleRange({from:1646910000-parseInt(tvWidget.activeChart().resolution()*50*60),to:1646946000+parseInt(tvWidget.activeChart().resolution()*50*60)}) });
    button.textContent = 'D';
    var barinfo = tvWidget.createButton();
    barinfo.setAttribute('title', 'Bar Information.');
    barinfo.textContent = 'B';
    var current_atr = tvWidget.createButton();
    current_atr.setAttribute('title', 'Targets');
    current_atr.textContent = 'current_atr';



    var actions = tvWidget.createDropdown(
        {
            title: 'Strategies',
            tooltip: 'Strategies Shortcuts',
            items: [
                {
                    title: 'Show Flag Limits 24',
                    onSelect: () => {
                        var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    let candle_open = obj[i][1]
                                    let candle_close = obj[i][4]
                                    let candle_color = "red"
                                    if (candle_open < candle_close) {
                                        candle_color = 'green'
                                    }
                                    let pcandle_open = obj[i+1][1]
                                    let pcandle_close = obj[i+1][4]
                                    let pcandle_color = "red"
                                    if (pcandle_open < pcandle_close) {
                                        pcandle_color = 'green'
                                    }
                                    //console.log(obj[i]);
                                    if (((obj[i][9] == 'longbar24' || obj[i][9] == 'spikebar24' ) && (obj[i+1][9] == 'longbar24' || obj[i+1][9] == 'spikebar24' )))  {
                                        if(pcandle_color===candle_color){


                                            console.log("FL Found")
                                            var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                                time: obj[i+1][0] / 1000,
                                            }, {shape: 'icon'}));
                                            l.setProperties(
                                                {
                                                    icon: "0xf06b",
                                                }
                                            );
                                        }

                                    }
                                }
                            }
                        }

                        xhr.send();
                    },
                },
                {
                    title: 'Show Flag Limits',
                    onSelect: () => {
                        var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    let candle_open = obj[i][1]
                                    let candle_close = obj[i][4]
                                    let candle_color = "red"
                                    if (candle_open < candle_close) {
                                        candle_color = 'green'
                                    }
                                    let pcandle_open = obj[i+1][1]
                                    let pcandle_close = obj[i+1][4]
                                    let pcandle_color = "red"
                                    if (pcandle_open < pcandle_close) {
                                        pcandle_color = 'green'
                                    }
                                    //console.log(obj[i]);
                                    if (((obj[i][8] == 'longbar' || obj[i][8] == 'spikebar' ) && (obj[i+1][8] == 'longbar' || obj[i+1][8] == 'spikebar' )))  {
                                        if(pcandle_color===candle_color){


                                            console.log("FL Found")
                                            var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                                time: obj[i+1][0] / 1000,
                                            }, {shape: 'icon'}));
                                            l.setProperties(
                                                {
                                                    icon: "0xf06b",
                                                }
                                            );
                                        }

                                    }
                                }
                            }
                        }

                        xhr.send();
                    },
                },
                {
                    title: 'Show Long Bars',
                    onSelect: () => {

                        var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    console.log(obj[i]);
                                    if (obj[i][8] == 'longbar' || obj[i][8] == 'spikebar') {
                                        var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                            time: obj[i][0] / 1000,
                                        }, {shape: 'icon'}));
                                        l.setProperties(
                                            {
                                                icon: "0xf05b",
                                            }
                                        );
                                    }
                                }
                            }
                        }

                        xhr.send();



                    },
                },
                {
                    title: 'Show Long Bars (ATR24)',
                    onSelect: () => {
                        var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    console.log(obj[i]);
                                    if (obj[i][9] == 'longbar24' || obj[i][9] == 'spikebar24') {
                                        var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                            time: obj[i][0] / 1000,
                                        }, {shape: 'icon'}));
                                        l.setProperties(
                                            {
                                                icon: "0xf05b",
                                            }
                                        );
                                    }
                                }
                            }
                        }

                        xhr.send();
                    },
                },
                {
                    title: 'Show Long Shadows (ATR24)',
                    onSelect: () => {
                        var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    if (obj[i][9] == 'longshadow24' || obj[i][9] == 'spikeshadow24') {
                                        var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                            time: obj[i][0] / 1000,
                                        }, {shape: 'icon'}));
                                        l.setProperties(
                                            {
                                                icon: "0xf05b",
                                            }
                                        );
                                    }
                                }
                            }
                        }

                        xhr.send();


                    },
                },
                {
                    title: 'Show Long Shadows ',
                    onSelect: () => {var price_range = tvWidget.activeChart().getVisiblePriceRange();
                        var time_range = tvWidget.activeChart().getVisibleRange();
                        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
                        const urlParameters = {
                            symbol: tvWidget.activeChart().symbol().split(':')[1],
                            interval: tvWidget.activeChart().resolution(),
                            startTime: time_range.from * 1000,
                            endTime: time_range.to * 1000

                        };
                        const query = Object.keys(urlParameters)
                            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                            .join('&');
                        var xhr = new XMLHttpRequest();
                        var url = `http://127.0.0.1:8000/fapi/v1/klines?${query}`;

                        xhr.open("GET", url, true);
                        xhr.onreadystatechange = function () {
                            if (this.readyState == 4 && this.status == 200) {
                                const obj = JSON.parse(this.responseText);
                                //console.log(obj)
                                for (let i = 0; i < obj.length; i++) {
                                    if (obj[i][8] == 'longshadow' || obj[i][8] == 'spikeshadow') {
                                        var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                                            time: obj[i][0] / 1000,
                                        }, {shape: 'icon'}));
                                        l.setProperties(
                                            {
                                                icon: "0xf05b",
                                            }
                                        );
                                    }
                                }
                            }
                        }

                        xhr.send();
                    },
                }
            ],
            icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28"><g fill="none" stroke="currentColor"><circle cx="10" cy="10" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path stroke-linecap="square" d="M17.5 7.5l-7 13"/></g></svg>`,
        }
    ).then(myDropdownApi => {
        // Use myDropdownApi if you need to update the dropdown:
        // myDropdownApi.applyOptions({
        //     title: 'a new title!'
        // });

        // Or remove the dropdown:
        // myDropdownApi.remove();
    });










    var replay_panel = tvWidget.createButton();
    replay_panel.setAttribute('title', 'Replay');
    replay_panel.textContent = 'Replay';
    replay_panel.addEventListener('click', function () {


    });




    var supply_demand_zones = tvWidget.createButton();
    supply_demand_zones.setAttribute('title', 'SupplyDemands');
    supply_demand_zones.textContent = 'SD';



    var bar_information = tvWidget.createButton();
    bar_information.setAttribute('title', 'Bar Information');
    bar_information.textContent = ' ';

    var m5atr = tvWidget.createButton();
    m5atr.setAttribute('title', 'ATR5m');
    m5atr.textContent = 'ATR5m';

    var m15atr = tvWidget.createButton();
    m15atr.setAttribute('title', 'ATR15m');
    m15atr.textContent = 'ATR15m';

    var h1atr = tvWidget.createButton();
    h1atr.setAttribute('title', 'ATR1h');
    h1atr.textContent = 'ATR1h';

    var h4atr = tvWidget.createButton();
    h4atr.setAttribute('title', 'ATR4h');
    h4atr.textContent = 'ATR4h';


    var d1atr = tvWidget.createButton();
    d1atr.setAttribute('title', 'ATR1D');
    d1atr.textContent = 'ATR1D';

    /*var w1atr = tvWidget.createButton();
    w1atr.setAttribute('title', 'ATR1W');
    w1atr.textContent = 'ATR1W';

    var M1atr = tvWidget.createButton();
    M1atr.setAttribute('title', 'ATR1M');
    M1atr.textContent = 'ATR1M';
    */
    var err;
    barinfo.addEventListener('click', () => {
            let candles = []
            tvWidget.activeChart().requestSelectBar()
                .then(function (time) {
                    //console.log(time)
                    let highs = []
                    let lows = []
                    let opens = []
                    let closes = []


                    var chart_series = tvWidget.activeChart().getSeries()
                    var chart_data = chart_series.data()
                    /*
                    for (var i = 0; i < chart_data.m_bars._items.length; i++) {
                        opens.push(chart_data.m_bars._items[i]['value'][1])
                        highs.push(chart_data.m_bars._items[i]['value'][2])
                        lows.push(chart_data.m_bars._items[i]['value'][3])
                        closes.push(chart_data.m_bars._items[i]['value'][4])
                        //candles.push([chart_data.m_bars._items[i]['value'][2], chart_data.m_bars._items[i]['value'][4], chart_data.m_bars._items[i]['value'][3]])
                    }
                    let fly_atr3 = atr(highs,lows,closes,3)
                    let fly_atr5 = atr(highs,lows,closes,5)
                    let fly_atr7 = atr(highs,lows,closes,7)
                    let fly_tr = trueRange(highs,lows,closes)
                    //console.log("fly_tr",fly_tr)
                    //console.log("closes",closes)
                    var current_candle_index = chart_data.m_bars._items.findIndex(obj => {
                        return obj.timeMs === time * 1000
                    })
                    let matr = avg_atr_Crypto(trueRange(highs,lows,closes))
                    console.log(matr)*/
                    /*console.log("candle_index:", current_candle_index)
                    console.log("true range:", fly_tr)
                    console.log("rma :", pine_rma(fly_tr, 5))
                    console.log("nz rma :", nz(pine_rma(fly_tr, 5)))
                    console.log("avg_crypto :", avg_atr_Crypto(fly_tr))*/
                    /*let u5 = nz(pine_rma(fly_tr, 5))
                    let u11 = nz(pine_rma(fly_tr, 11))
                    let u22 = nz(pine_rma(fly_tr, 22))
                    let u45 = nz(pine_rma(fly_tr, 45))
                    let u91 = nz(pine_rma(fly_tr, 91))
                    let u182 = nz(pine_rma(fly_tr, 182))
                    let u364 = nz(pine_rma(fly_tr, 364))
                    let z5 = zc(u5,5)
                    let z11 = zc(u11,11)
                    let z22 = zc(u22,22)
                    let z45 = zc(u45,45)
                    let z91 = zc(u91,91)
                    let z182 = zc(u182,182)
                    let z364 = zc(u364,364)*/


                    //console.log("zc atr364 :",zc(atr364, 13))
                    var current_candle_index = chart_data.m_bars._items.findIndex(obj => {
                        return obj.timeMs === time * 1000
                    })
                    var open = chart_data.m_bars._items[current_candle_index]['value'][1]
                    var high = chart_data.m_bars._items[current_candle_index]['value'][2]
                    var low = chart_data.m_bars._items[current_candle_index]['value'][3]
                    var close = chart_data.m_bars._items[current_candle_index]['value'][4]
                    var volume = chart_data.m_bars._items[current_candle_index]['value'][5]
                    var candle_max = (high - low).toFixed(1)
                    var candle_body_length = Math.abs(open - close).toFixed(1)
                    bar_information.textContent = "V:" + candle_max + "/Body:" + candle_body_length + "/shadow:" + (candle_max - candle_body_length).toFixed(1)
                    bar_information.textContent += "/" + (Math.max(candle_body_length, (candle_max - candle_body_length)) / candle_max).toFixed(3) + "/"
                    bar_information.textContent += "/B2S:" + (candle_body_length / (candle_max - candle_body_length)).toFixed(3) + "/"


                    const urlParameters = {
                        symbol: tvWidget.activeChart().symbol().split(':')[1],
                        interval: tvWidget.activeChart().resolution(),
                        endTime: time * 1000

                    };
                    //console.log(time * 1000)
                    const query = Object.keys(urlParameters)
                        .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                        .join('&');

                    var xhr = new XMLHttpRequest();
                    var url = `http://localhost:8000/get_atr_data?${query}`;
                    xhr.open("GET", url, true);
                    xhr.onreadystatechange = function () {
                        if (this.readyState == 4 && this.status == 200) {
                            const obj = JSON.parse(this.responseText);
                            //console.log(obj)
                            var atr5 = parseFloat(obj["5m"]).toFixed(1)
                            var atr15 = parseFloat(obj["15m"]).toFixed(1)
                            var atr60 = parseFloat(obj["1h"]).toFixed(1)
                            var atr240 = parseFloat(obj["4h"]).toFixed(1)
                            var atr1d = parseFloat(obj["1d"]).toFixed(1)
                            //var atr1w = parseFloat(obj["1w"]).toFixed(1)

                            m5atr.textContent = "5m: " + atr5
                            m15atr.textContent = "15m: " + atr15
                            h1atr.textContent = "1h: " + atr60
                            h4atr.textContent = "4h: " + atr240
                            d1atr.textContent = "1d: " + atr1d
                            //w1atr.textContent = "1w: " + atr1w


                            var catr = parseFloat(obj["current_atr"]).toFixed(1)

                            current_atr.textContent = catr + "|" + (3 * catr).toFixed(1) + "|" + (5 * catr).toFixed(1) + "|" + (7 * catr).toFixed(1)
                            //console.log(catr)
                            //let catr = fly_tr[current_candle_index]
                            //console.log(fly_tr[current_candle_index])
                            //bar_information.textContent += "/"+catr

                            if (candle_max > 2.4 * catr) {
                                bar_information.textContent += "Spike"

                            } else if (1.2 * catr < candle_max) {
                                bar_information.textContent += "Long Bar"

                            } else if (0.8 * catr < candle_max) {
                                bar_information.textContent += "Master"

                            } else {
                                bar_information.textContent += "Nothing"
                            }


                            if ((c.toLowerCase() != "nan") && (c > atr1w)) {

                                current_atr.textContent = c + "current: 5m " + parseFloat(obj["current_atr"]).toFixed(6)
                            } else if (c < atr15) {
                                console.log("lower than 15m :" + c + ":" + atr15)
                                current_atr.textContent = c + "current: 15m " + parseFloat(obj["current_atr"]).toFixed(6)
                            } else if (c < atr60) {
                                console.log("lower than 1h :" + c + ":" + atr60)
                                current_atr.textContent = c + "current: 1h " + parseFloat(obj["current_atr"]).toFixed(6)
                            } else if (c < atr240) {
                                console.log("lower than 240 :" + c + ":" + atr240)
                                current_atr.textContent = c + "current: 4h " + parseFloat(obj["current_atr"]).toFixed(6)
                            } else if (c < atr1d) {
                                console.log("lower than 1d :" + c + ":" + atr1d)
                                current_atr.textContent = "current: 1d " + parseFloat(obj["current_atr"]).toFixed(6)
                            } else if (c < atr1w) {
                                console.log("lower than 1w :" + c + ":" + atr1w)
                                current_atr.textContent = "current: 1w " + parseFloat(obj["current_atr"]).toFixed(6)
                            }

                        }
                    }
                    //  START OLD METHOD
                    /**
                     const urlParameters = {
                        symbol: tvWidget.activeChart().symbol().split(':')[1],
                        interval: tvWidget.activeChart().resolution(),
                        limit: 500,
                        startTime: 0,
                        endTime: time * 1000

                    };
                     //console.log(time * 1000)
                     const query = Object.keys(urlParameters)
                     .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                     .join('&');


                     var xhr = new XMLHttpRequest();
                     var url = `http://localhost:8000/get_trex_info?${query}`;

                     xhr.open("GET", url, true);

                     // function execute after request is successful
                     xhr.onreadystatechange = function () {
                        if (this.readyState == 4 && this.status == 200) {
                            const obj = JSON.parse(this.responseText);
                            //console.log(obj)
                            var atr5 = parseFloat(obj["5m"]).toFixed(1)
                            var atr15 = parseFloat(obj["15m"]).toFixed(1)
                            var atr60 = parseFloat(obj["1h"]).toFixed(1)
                            var atr240 = parseFloat(obj["4h"]).toFixed(1)
                            var atr1d = parseFloat(obj["1d"]).toFixed(1)
                            var atr1w = parseFloat(obj["1w"]).toFixed(1)

                            m5atr.textContent = "5m: " + atr5
                            m15atr.textContent = "15m: " + atr15
                            h1atr.textContent = "1h: " + atr60
                            h4atr.textContent = "4h: " + atr240
                            d1atr.textContent = "1d: " + atr1d
                            w1atr.textContent = "1w: " + atr1w


                            var catr = parseFloat(obj["current_atr"]).toFixed(1)

                            current_atr.textContent = catr + "|" + (3 * catr).toFixed(1) + "|" + (5 * catr).toFixed(1) + "|" + (7 * catr).toFixed(1)
                            //console.log(catr)
                            //let catr = fly_tr[current_candle_index]
                            //console.log(fly_tr[current_candle_index])
                            //bar_information.textContent += "/"+catr

                            if (candle_max > 2.4 * catr) {
                                bar_information.textContent += "Spike"

                            } else if (1.2 * catr < candle_max) {
                                bar_information.textContent += "Long Bar"

                            } else if (0.8 * catr < candle_max) {
                                bar_information.textContent += "Master"

                            } else {
                                bar_information.textContent += "Nothing"
                            }


                            # should comment this section if we use old method
                            if ((c.toLowerCase() != "nan") && (c>atr1w)) {

                                current_atr.textContent = c+"current: 5m "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr15) {
                                console.log("lower than 15m :" + c + ":"+atr15 )
                                current_atr.textContent = c+"current: 15m "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr60) {
                                console.log("lower than 1h :" + c + ":"+atr60 )
                                current_atr.textContent = c+"current: 1h "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr240) {
                                console.log("lower than 240 :" + c + ":"+atr240 )
                                current_atr.textContent = c+"current: 4h "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr1d) {
                                console.log("lower than 1d :" + c + ":"+atr1d )
                                current_atr.textContent = "current: 1d "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr1w) {
                                console.log("lower than 1w :" + c + ":"+atr1w )
                                current_atr.textContent = "current: 1w "+parseFloat(obj["current_atr"]).toFixed(6)
                            }# should comment this section if we use old method


                        }
                    }

                     **/
                    //  END OLD METHOD
                    // Sending our request
                    xhr.send();


                    //conosle.log(avg_atr_Crypto(closes))

                    //candle_voltality.textContent = "Max: " + candle_max
                    //candle_body.textContent = "Body: " +candle_body_length
                    //max_shadow.textContent = "Shadow:"+ (candle_max - candle_body_length).toFixed(1)


                    //alert("First clicked.");


                })
                .catch(err)
            {
                console.log(err)
            }
            ;
            //.catch(function () {
            //    console.log('bar selection was rejected');
            //});


        }
    );


    /*tvWidget.activeChart().crossHairMoved().subscribe(
        null,
        ({ time, price }) => {
            var chart_series = tvWidget.activeChart().getSeries()
             var chart_data = chart_series.data()
             var current_candle = chart_data.m_bars._items.filter(obj=> {return obj.timeMs===time*1000})
             //console.log(current_candle[0]['value'])
             var open = current_candle[0]['value'][1]
             var high = current_candle[0]['value'][2]
             var low = current_candle[0]['value'][3]
             var close = current_candle[0]['value'][4]
             var volume = current_candle[0]['value'][5]
             var candle_max = (high -low ).toFixed(1)
             var candle_body_length = Math.abs(open-close).toFixed(1)
            candle_voltality.textContent = "Max: " + candle_max
            candle_body.textContent = "Body: " +candle_body_length
            max_shadow.textContent = "Shadow:"+ (candle_max - candle_body_length).toFixed(1)
        }//button.textContent = "Current CrossHair Position: "+time}
        
    );*/

    /*
        // custom context menu
        tvWidget.onContextMenu(function(unixtime, price) {
            return [
                {
                position: "top",
                //text: "ATR3:" + unixtime + ", price: " + price,
                text: "Get Trex Info.",
                click: function() {
                    const urlParameters = {
                        symbol: tvWidget.activeChart().symbol().split(':')[1],
                        interval: tvWidget.activeChart().resolution(),
                        limit: 500,
                        startTime:0,
                        endTime:unixtime*1000

                    };
                    console.log(unixtime*1000)
                    const query = Object.keys(urlParameters)
                        .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                        .join('&');




                    var xhr = new XMLHttpRequest();
                    var url = `http://localhost:8000/get_trex_info?${query}`;

                    xhr.open("GET", url, true);

                    // function execute after request is successful
                    xhr.onreadystatechange = function () {
                        if (this.readyState == 4 && this.status == 200) {
                            const obj = JSON.parse(this.responseText);
                            //console.log(obj)
                            var atr5 = parseFloat(obj["5m"]).toFixed(1)
                            var atr15 = parseFloat(obj["15m"]).toFixed(1)
                            var atr60 = parseFloat(obj["1h"]).toFixed(1)
                            var atr240 = parseFloat(obj["4h"]).toFixed(1)
                            var atr1d = parseFloat(obj["1d"]).toFixed(1)
                            var atr1w = parseFloat(obj["1w"]).toFixed(1)

                            m5atr.textContent = "5m: "+atr5
                            m15atr.textContent = "15m: "+atr15
                            h1atr.textContent = "1h: "+atr60
                            h4atr.textContent = "4h: "+atr240
                            d1atr.textContent = "1d: "+atr1d
                            w1atr.textContent = "1w: "+atr1w
                            var c = parseFloat(obj["shadow"]).toFixed(1)
                            var catr = parseFloat(obj["current_atr"]).toFixed(1)
                            current_atr.textContent =catr +"|"+(3*catr).toFixed(1)+"|"+(5*catr).toFixed(1)+"|"+(7*catr).toFixed(1)

                            if (c<atr5) {

                                current_atr.textContent = c+"current: 5m "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr15) {
                                current_atr.textContent = c+"current: 15m "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr60) {
                                current_atr.textContent = c+"current: 1h "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr240) {
                                current_atr.textContent = c+"current: 4h "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr1d) {
                                current_atr.textContent = "current: 1d "+parseFloat(obj["current_atr"]).toFixed(6)
                            }
                            else if (c<atr1w) {
                                current_atr.textContent = "current: 1w "+parseFloat(obj["current_atr"]).toFixed(6)
                            }


                        }
                    }
                    // Sending our request
                    xhr.send();

                    //alert("First clicked.");
                }
                },

            { text: "-", position: "top" },
            //{ text: "-Objects Tree..." },
            ,
            {
                position: "bottom",
                text: "Bottom menu item",
                click: function() { alert("Third clicked."); }
            }];
        }); */


    // create monthly button.
    /* var show_monthly_levels = tvWidget.createButton();
    show_monthly_levels.setAttribute('title', 'Show/Hide Monthly Levels.');
    show_monthly_levels.textContent = 'M';
    show_monthly_levels.addEventListener('click', function () {
        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
        var price_range = tvWidget.activeChart().getVisiblePriceRange();

        //const data = await makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1M&limit=10&symbol='+clean_symbol);
        const monthly_levels = makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1M&symbol=' + clean_symbol+"&from="+price_range.from+"&to="+price_range.to);
        monthly_levels.then(function (res) {
            res.data.forEach(element => {
                var eprice = parseFloat(element.split(':')[1])
                var etime = parseInt(element.split(':')[0]) / 1000
                var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                    price: eprice,
                    time: etime
                }, {shape: 'horizontal_ray'}));

                l.setProperties(
                    {
                        linecolor: 'rgba(41, 98, 255, 0.5)',
                        linewidth: 4,
                        showPrice: false,
                    }
                );
            });

        });


    });
    // weekly
    var show_weekly_levels = tvWidget.createButton();
    show_weekly_levels.setAttribute('title', 'Show/Hide Weekly Levels.');
    show_weekly_levels.textContent = 'W';
    show_weekly_levels.addEventListener('click', function () {
        var price_range = tvWidget.activeChart().getVisiblePriceRange();
        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
        //const data = await makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1M&limit=10&symbol='+clean_symbol);
        console.log('http://127.0.0.1:8000/get_levels?timeframe=1W&limit=10&symbol=' + clean_symbol)
        const monthly_levels = makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1W&symbol=' +clean_symbol+"&from="+price_range.from+"&to="+price_range.to);
        monthly_levels.then(function (res) {
            res.data.forEach(element => {
                var eprice = parseFloat(element.split(':')[1])
                var etime = parseInt(element.split(':')[0]) / 1000
                var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                    price: eprice,
                    time: etime
                }, {shape: 'horizontal_ray'}));

                l.setProperties(
                    {
                        linecolor: 'rgba(76, 175, 80, 0.5)',
                        linewidth: 3,
                        showPrice: false,
                    }
                );

            });

        });

    });
    // daily

    var show_daily_levels = tvWidget.createButton();
    show_daily_levels.setAttribute('title', 'Show/Hide Daily Levels.');
    show_daily_levels.textContent = 'D';
    show_daily_levels.addEventListener('click', function () {
        var price_range = tvWidget.activeChart().getVisiblePriceRange();
        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
        //const data = await makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1M&limit=10&symbol='+clean_symbol);
        const monthly_levels = makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1D&symbol=' + clean_symbol+"&from="+price_range.from+"&to="+price_range.to);
        monthly_levels.then(function (res) {
            res.data.forEach(element => {
                var eprice = parseFloat(element.split(':')[1])
                var etime = parseInt(element.split(':')[0]) / 1000
                var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                    price: eprice,
                    time: etime
                }, {shape: 'horizontal_ray'}));

                l.setProperties(
                    {
                        linecolor: 'rgba(183, 28, 28, 1)',
                        linewidth: 2,
                        showPrice: false,
                    }
                );

            });

        });

    });


    // 4h 
    var show_4h_levels = tvWidget.createButton();
    show_4h_levels.setAttribute('title', 'Show/Hide 4h Levels.');
    show_4h_levels.textContent = '4h';
    show_4h_levels.addEventListener('click', function () {
        var clean_symbol = tvWidget.activeChart().symbol().split(':')[1];
        var price_range = tvWidget.activeChart().getVisiblePriceRange();
        //const data = await makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=1M&limit=10&symbol='+clean_symbol);
        const monthly_levels = makeApiRequest('http://127.0.0.1:8000/get_levels?timeframe=240&symbol=' + clean_symbol+"&from="+price_range.from+"&to="+price_range.to);
        monthly_levels.then(function (res) {
            res.data.forEach(element => {
                var eprice = parseFloat(element.split(':')[1])
                var etime = parseInt(element.split(':')[0]) / 1000
                var l = tvWidget.activeChart().getShapeById(tvWidget.activeChart().createShape({
                    price: eprice,
                    time: etime
                }, {shape: 'horizontal_ray'}));

                l.setProperties(
                    {
                        linecolor: 'rgba(42, 46, 57, 0.5)',
                        linewidth: 1,
                        showPrice: false,
                    }
                );

            });

        });

    });*/


    /*
    tvWidget.activeChart().crossHairMoved().subscribe(
        null,
        ({ time, price }) => button.textContent = time//button.textContent = "Current CrossHair Position: "+time
    );
    */
    /*var button2 = tvWidget.createButton();
    button2.setAttribute('title', 'Resume Working.');
    button2.addEventListener('click', function() { 
        console.log(button.getAttribute('title'));
        var new_range = button.getAttribute('title').split(':');
        tvWidget.activeChart().setVisibleRange(
            {
                from: parseInt(new_range[0]),
                to:	parseInt(new_range[1])
            }
            )
    
    
    });
    //button.addEventListener('click', function() { tvWidget.activeChart().setVisibleRange({from:1646910000-parseInt(tvWidget.activeChart().resolution()*50*60),to:1646946000+parseInt(tvWidget.activeChart().resolution()*50*60)}) });
    button2.textContent = 'Save Middle Location.';
    */


});


/*
window.tvWidget.activeChart().crossHairMoved().subscribe(
    null,
    ({ time, price }) => {
		LastTimeLocation = time;
			console.log(time, price)
	}
);
window.tvWidget.activeChart().onIntervalChanged().subscribe(
    null,
    (interval, timeframeObj) => {
		console.log(interval,timeframeObj);
		
		tvWidget.activeChart().setVisibleRange({
			from:LastTimeLocation-50*parseInt(tvWidget.activeChart().resolution),
			to:LastTimeLocation+50*parseInt(tvWidget.activeChart().resolution)},
			
    		{ percentRightMargin: 20 }
		)
		
	}
);
*/
//widget.activeChart().onIntervalChanged().subscribe(null, (interval, timeframeObj) => timeframeObj.timeframe = "12M");
