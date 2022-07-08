import {
	makeApiRequest,
	generateSymbol,
	parseFullSymbol,
} from './helpers.js';
import {
	subscribeOnStream,
	unsubscribeFromStream,
} from './streaming.js';


const lastBarsCache = new Map();

const configurationData = {
	supported_resolutions: ['1S','5S','30S','1','2','3','4','5','15','30','60','120','240','480','720','1D','2D','3D', '1W', '1M'],
	exchanges: [{
		value: 'Binance',
		name: 'Binance',
		desc: 'Binance Exchange',
	},
	{
		// `exchange` argument for the `searchSymbols` method, if a user selects this exchange
		value: 'Kucoin',

		// filter name
		name: 'Kucoin',

		// full exchange name displayed in the filter popup
		desc: 'Kucoin Exchange',
	},
	],
	symbols_types: [{
		name: 'crypto',

		// `symbolType` argument for the `searchSymbols` method, if a user selects this symbol type
		value: 'crypto',
	},
		// ...
	],
};

async function getAllSymbols() {
	//const data = await makeApiRequest('data/v3/all/exchanges');
	const data = await makeApiRequest('http://127.0.0.1:8000/fapi/v1/exchangeInfo');
	let allSymbols = [];

	for (const exchange of configurationData.exchanges) {
		const pairs = data.symbols;
		//const pairs = data.Data[exchange.value].pairs;
		//console.log(pairs);
		//for (const leftPairPart of pairs) {
		for (const symbol of pairs) {
			allSymbols.push(
				{
					symbol: symbol.symbol,
					full_name: symbol.symbol,
					has_intraday:true,
					ticker: symbol.ticker,
					name: symbol.symbol,
					description: symbol.description,
					type: symbol.type,
					session: '24x7',
					timezone: 'UTC',
					exchange: symbol.exchange,
					minmov: symbol.minmov,
					pricescale: symbol.pricescale,
					has_weekly_and_monthly: true,
					has_daily : true,
				}
			);
			//const symbols = pairs[leftPairPart].map(rightPairPart => {
				//const symbol = generateSymbol(exchange.value, leftPairPart, rightPairPart);

			//});

		}
		//console.log(allSymbols);
	}
	//console.log(allSymbols);
	return allSymbols;
}

export default {
	onReady: (callback) => {
		console.log('[onReady]: Method call');
		setTimeout(() => callback(configurationData));
	},

	searchSymbols: async (
		userInput,
		exchange,
		symbolType,
		onResultReadyCallback,
	) => {
		console.log('[searchSymbols]: Method call');
		const symbols = await getAllSymbols();
		const newSymbols = symbols.filter(symbol => {
			const isExchangeValid = exchange === '' || symbol.exchange === exchange;
			const isFullSymbolContainsInput = symbol.full_name
				.toLowerCase()
				.indexOf(userInput.toLowerCase()) !== -1;
			return isExchangeValid && isFullSymbolContainsInput;
		});
		onResultReadyCallback(newSymbols);
	},

	resolveSymbol: async (
		symbolName,
		onSymbolResolvedCallback,
		onResolveErrorCallback,
	) => {
		console.log('[resolveSymbol]: Method call', symbolName);
		const symbols = await getAllSymbols();
		const symbolItem = symbols.find(({
			full_name,
		}) => full_name === symbolName);
		if (!symbolItem) {
			console.log('[resolveSymbol]: Cannot resolve symbol', symbolName);
			onResolveErrorCallback('cannot resolve symbol');
			return;
		}

		// get symbol info
		const symbolInfo = {
			ticker: symbolItem.ticker,
			name: symbolItem.symbol,
			full_name : symbolItem.symbol,
			description: symbolItem.description,
			type: symbolItem.type,
			session: '24x7',
			timezone: 'UTC',
			exchange: symbolItem.exchange,
			minmov: symbolItem.minmov,
			pricescale: symbolItem.pricescale,
			has_intraday: true,
			has_no_volume: false,
			has_weekly_and_monthly: true,
			has_daily : true,
			supported_resolutions: configurationData.supported_resolutions,
			volume_precision: 2,
			data_status: 'streaming',
		};

		console.log('[resolveSymbol]: Symbol resolved', symbolInfo);
		onSymbolResolvedCallback(symbolInfo);
	},

	getBars: async (symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) => {
		const { from, to, firstDataRequest } = periodParams;
		console.log('[getBars]: Method call', symbolInfo, resolution, from, to);

		const urlParameters = {
			symbol: symbolInfo.name,
			interval: resolution,
			limit: 500,
			startTime:from*1000,
			endTime:to*1000

		};
		const query = Object.keys(urlParameters)
			.map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
			.join('&');
		try {
			
			//const data = await makeApiRequest(`https://fapi.binance.com/fapi/v1/klines?${query}`);
			const data = await makeApiRequest(`http://localhost:8000/fapi/v1/klines?${query}`);
			if (data.Code  || data.length === 0) {
				// "noData" should be set if there is no data in the requested period.
				onHistoryCallback([], {
					noData: false,
				});
				return;
			}
			let bars = [];
			data.forEach(bar => {
				//console.log(bar);
				bars.push({
						time: parseInt(bar[0]) ,
						open: parseFloat(bar[1]),
						high: parseFloat(bar[2]),
						low: parseFloat(bar[3]),
						close: parseFloat(bar[4]),
						volume: parseInt(bar[5])
					});
				/*if (bar[0] >= from && bar[0] < to) {
					bars = [...bars, {
						time: parseInt(bar[0]) * 1000,
						open: parseFloat(bar[1]),
						high: parseFloat(bar[2]),
						low: parseFloat(bar[3]),
						close: parseFloat(bar[4]),
					}];
				}*/
			});

			/*
			data.forEach(bar => {
				//console.log(bar[0]);
				if (bar[0] >= from && bar[0] < to) {
					bars.push(
						{time: bar[0] / 1000,
						low: bar[4],
						high: bar[3],
						open: bar[1],
						close: bar[5]}
					);
				};
			});*/
			//console.log("BARS:",bars);
			if (firstDataRequest) {
				lastBarsCache.set(symbolInfo.full_name, {
					...bars[bars.length - 1],
				});
			}
			console.log(`[getBars]: returned ${bars.length} bar(s)`);
			onHistoryCallback(bars, {
				noData: false,
			});
		} catch (error) {
			console.log('[getBars]: Get error', error);
			onErrorCallback(error);
		}
	},

	subscribeBars: (
		symbolInfo,
		resolution,
		onRealtimeCallback,
		subscribeUID,
		onResetCacheNeededCallback,
	) => {
		console.log('[subscribeBars]: Method call with subscribeUID:', subscribeUID);
		subscribeOnStream(
			symbolInfo,
			resolution,
			onRealtimeCallback,
			subscribeUID,
			onResetCacheNeededCallback,
			lastBarsCache.get(symbolInfo.full_name),
		);
	},

	unsubscribeBars: (subscriberUID) => {
		console.log('[unsubscribeBars]: Method call with subscriberUID:', subscriberUID);
		unsubscribeFromStream(subscriberUID);
	},
};
