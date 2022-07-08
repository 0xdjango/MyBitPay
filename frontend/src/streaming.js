import { parseFullSymbol } from './helpers.js';

var globalTimer;
var list_of_subscriptions = {};
function getRandomInt(max) {
	return Math.floor(Math.random() * max);
  }
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}
function pop(object, propertyName) {
    let temp = object[propertyName];
    delete object[propertyName];
    return temp;
}
let minute_timeframes = {
		"1":"1m",
		"5":"5m",
		"15":"15m",
		"30":"30m",
		
}
let hour_timeframes = {
	"60":"1h"
}




export function subscribeOnStream(
	
	symbolInfo,
    resolution,
    onRealtimeCallback,
    subscribeUID,
    onResetCacheNeededCallback,
    lastDailyBar

){
	/*
	globalTimer = 0;

	if(resolution in minute_timeframes || resolution in hour_timeframes){
		
		
		//console.log(timeframes.resolution);
		// live subscription is only available for 1h and lower timeframes
		
		var timeframe = "";
		if(resolution in minute_timeframes){
			
			timeframe = resolution+'m';
			
		}
		else if(resolution in hour_timeframes){
			timeframe = resolution/60+'h';
			
		}
		//console.log('wss://fstream.binance.com/ws/stream?streams=btcusdt_perpetual@Kline_'+timeframe)
		let ws = new WebSocket("wss://fstream.binance.com/ws/stream?streams=btcusdt_perpetual@Kline_"+timeframe);
		// subscribe to candles 
		var sid = getRandomInt(100);
		
		ws.onopen = function() {
			console.log('[socket] Connected');
			var sub = {
				"method": "SUBSCRIBE",
				"params": [
				  "btcusdt@kline_"+timeframe,
				],
				"id": sid
			  }
			
			list_of_subscriptions[subscribeUID] = [sid,timeframe];
			console.log(JSON.stringify(sub));
			ws.send(JSON.stringify(sub));
			
			var unsub = {
				"method": "UNSUBSCRIBE",
				"params": [
				  "btcusdt@kline_"+timeframe
				],
				"id": sid
			  }
			  //console.log(JSON.stringify(unsub));
			  list_of_subscriptions[subscribeUID] = [ws,unsub];
			  //ws.send(JSON.stringify(unsub));

			//list_of_subscriptions.subscribeUID = ;
			//console.log("\{\"method\": \"SUBSCRIBE\",\"params\": [\"btcusdt@kline_"+timeframes[resolution]+"\"],\"id\": 1}");
		}
	ws.onmessage = (event)=> {
		globalTimer +=1;
		var tf = {
			"1m": "1",
			"5m": "5",
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
		}
		//console.log(event.data);
		let result = JSON.parse(event.data);
		//console.log(result);
		
		if('k' in result){ 
			var symbol = result['k']['s'];
			var timeframe = tf[result['k']['i']];
			var time = result['k']['t'];
			var open = result['k']['o'];
			var high = result['k']['h'];
			var low = result['k']['l'];
			var close = result['k']['c'];
			var volume = result['k']['v'];
			var data={
				'symbol':symbol,
				'tf':timeframe,
				'time':time,
				'open':open,
				'high':high,
				'low':low,
				'close':close,
				'volume':volume

		};
	
		//console.log(data);
		if(globalTimer>5){
		var url = new URL('http://localhost:8000/update_database');
		url.search = new URLSearchParams(data); 
		httpGet(url.toString());
		console.log(url.toString());
		globalTimer = 0;}
	
	
	
	}	//cnsole.log(result);
	}
	ws.onclose = function(reason) {
		console.log('[socket] Disconnected:', reason);
		//ws.send("\{\"method\": \"UNSUBSCRIBE\",\"params\": [\"btcusdt@kline_1m\"],\"id\": 1}");
	  };
	}

	*/
	}
	

  /*const channelToSubscription = new Map();
  // ...
  export function subscribeOnStream(
	  symbolInfo,
	  resolution,
	  onRealtimeCallback,
	  subscribeUID,
	  onResetCacheNeededCallback,
	  lastDailyBar
  ) {
	  
	let ws = new WebSocket("wss://fstream.binance.com/ws/stream?streams=btcusdt_perpetual@Kline_1m");
ws.onopen = function() {
	console.log('[socket] Connected');
    ws.send("\{\"method\": \"SUBSCRIBE\",\"params\": [\"btcusdt@kline_1m\"],\"id\": 1}");
  }
  
  ws.onmessage = (event)=> {
	let result = JSON.parse(event.data);
	
	//console.log(result.k);
	if('k' in result){ 
		console.log(new Date(result.k.t).toISOString());
	var open_time =new Date(result.k.t).toISOString();
	var kopen = result.k.o;
	var khigh = result.k.h;
	var klow = result.k.l;
	var kclose = result.k.c;
	var kvolume = result.k.v;
	onRealtimeCallback(
		{open_time, kclose, kopen, khigh, klow, kvolume}
	);};

	//cnsole.log(result);
}
ws.onclose = function(reason) {
	console.log('[socket] Disconnected:', reason);
    ws.send("\{\"method\": \"UNSUBSCRIBE\",\"params\": [\"btcusdt@kline_1m\"],\"id\": 1}");
  };
  }
  */

export function unsubscribeFromStream(subscribeUID) {
	
	/*let ws = list_of_subscriptions[subscribeUID][0];
	ws.send(JSON.stringify(list_of_subscriptions[subscribeUID][1]));
	pop(list_of_subscriptions,subscribeUID);
	//console.log(list_of_subscriptions);
	*/
}
/*
socket.on('m', data => {
	console.log('[socket] Message:', data);
	const [
		eventTypeStr,
		exchange,
		fromSymbol,
		toSymbol,
		,
		,
		tradeTimeStr,
		,
		tradePriceStr,
	] = data.split('~');

	if (parseInt(eventTypeStr) !== 0) {
		// skip all non-TRADE events
		return;
	}
	const tradePrice = parseFloat(tradePriceStr);
	const tradeTime = parseInt(tradeTimeStr);
	const channelString = `0~${exchange}~${fromSymbol}~${toSymbol}`;
	const subscriptionItem = channelToSubscription.get(channelString);
	if (subscriptionItem === undefined) {
		return;
	}
	const lastDailyBar = subscriptionItem.lastDailyBar;
	const nextDailyBarTime = getNextDailyBarTime(lastDailyBar.time);

	let bar;
	if (tradeTime >= nextDailyBarTime) {
		bar = {
			time: nextDailyBarTime,
			open: tradePrice,
			high: tradePrice,
			low: tradePrice,
			close: tradePrice,
		};
		console.log('[socket] Generate new bar', bar);
	} else {
		bar = {
			...lastDailyBar,
			high: Math.max(lastDailyBar.high, tradePrice),
			low: Math.min(lastDailyBar.low, tradePrice),
			close: tradePrice,
		};
		console.log('[socket] Update the latest bar by price', tradePrice);
	}
	subscriptionItem.lastDailyBar = bar;

	// send data to every subscriber of that symbol
	subscriptionItem.handlers.forEach(handler => handler.callback(bar));
});

function getNextDailyBarTime(barTime) {
	const date = new Date(barTime * 1000);
	date.setDate(date.getDate() + 1);
	return date.getTime() / 1000;
}

export function subscribeOnStream(
	symbolInfo,
	resolution,
	onRealtimeCallback,
	subscribeUID,
	onResetCacheNeededCallback,
	lastDailyBar,
) {
	const parsedSymbol = parseFullSymbol(symbolInfo.full_name);
	const channelString = `0~${parsedSymbol.exchange}~${parsedSymbol.fromSymbol}~${parsedSymbol.toSymbol}`;
	const handler = {
		id: subscribeUID,
		callback: onRealtimeCallback,
	};
	let subscriptionItem = channelToSubscription.get(channelString);
	if (subscriptionItem) {
		// already subscribed to the channel, use the existing subscription
		subscriptionItem.handlers.push(handler);
		return;
	}
	subscriptionItem = {
		subscribeUID,
		resolution,
		lastDailyBar,
		handlers: [handler],
	};
	channelToSubscription.set(channelString, subscriptionItem);
	console.log('[subscribeBars]: Subscribe to streaming. Channel:', channelString);
	socket.emit('SubAdd', { subs: [channelString] });
}

export function unsubscribeFromStream(subscriberUID) {
	// find a subscription with id === subscriberUID
	for (const channelString of channelToSubscription.keys()) {
		const subscriptionItem = channelToSubscription.get(channelString);
		const handlerIndex = subscriptionItem.handlers
			.findIndex(handler => handler.id === subscriberUID);

		if (handlerIndex !== -1) {
			// remove from handlers
			subscriptionItem.handlers.splice(handlerIndex, 1);

			if (subscriptionItem.handlers.length === 0) {
				// unsubscribe from the channel, if it was the last handler
				console.log('[unsubscribeBars]: Unsubscribe from streaming. Channel:', channelString);
				socket.emit('SubRemove', { subs: [channelString] });
				channelToSubscription.delete(channelString);
				break;
			}
		}
	}
}
*/

