import pandas as pd
import datetime as dt
import time
from instrument import *
from util import *
from oanda_api import *
# Pairs to fetch
PAIR_LIST = 'GBP,EUR,USD,CAD,JPY,NZD,CHF,AUD' # Pairs to fetch data for
INCREMENTS = { # Timeframes to collect COHLC data for
    #'M1': 1,
    #'M2': 2,
    #'M5': 5,
    #'M10': 10,
    #'M15': 15,
    #'M30': 30,
    #'H1': 60,
    #'H2': 120,
    #'H3': 180,
    'H4': 240,
    'H6': 360,
    'H8': 480#,
    #'H12': 720
    #'D': 1440   
}

def get_candles_df(json_data):
    prices = ['mid','bid','ask']
    ohlc = ['o','h','l','c']
    our_data = []
    for candle in json_data['candles']:
        if candle['complete'] ==  False:
            continue
        new_dict = {}
        new_dict['time'] = candle['time']
        new_dict['volume'] = candle['volume']
        for price in prices:
            for o in ohlc:
                new_dict[f'{price}_{o}'] = candle[price][o]
        our_data.append(new_dict)
    return pd.DataFrame.from_dict(our_data)

def build_file(pair,tf,api,start_date,end_date):
    fout = get_candles_data_fname(pair,tf)
    print('Building %s'%fout)
    candle_count = 2000 # API Candlestick Endpoint Query Max is 4000-5000 data rows
    time_step = INCREMENTS[tf]*candle_count # Timestep gets very small with more candles and lower timeframes (longer execution)
    end_date = get_utc_dt_from_str(end_date) # OHLC Query End Date
    date_from = get_utc_dt_from_str(start_date)# OHLC Query Start Date
    candle_dfs = []
    date_to = date_from
    while date_to < end_date:
        date_to = date_from + dt.timedelta(minutes=time_step)
        if date_to > end_date:
            date_to = end_date
        # Call fetch_candles from OANDA API class
        code, json_data = api.fetch_candles(pair,
            tf = tf,
            date_from = date_from,
            date_to = date_to)
        if code == 200 and len(json_data['candles']) > 0:
            candle_dfs.append(get_candles_df(json_data))
        elif code != 200:
            print('ERROR:',pair,tf,date_from,date_to)
            break
        date_from = date_to
    # Create final DataFrame to save to pickle   
    final_df = pd.concat(candle_dfs)
    final_df.drop_duplicates(subset='time',inplace=True)
    final_df.sort_values(by='time',inplace=True)
    final_df.to_pickle(get_candles_data_fname(pair,tf))
    print(' *  Candlestick/OHLC data saved to %s'%fout)
    print(f'\t=>{pair}\n\t=>{tf}\n\t=>{final_df.iloc[0].time}\n\t=>{final_df.iloc[-1].time}\n')

def run_collection(start_date,end_date):
    api = OandaAPI()
    for g in INCREMENTS.keys():
        for i in Instrument.get_pairs_from_str(PAIR_LIST):
            build_file(i,g,api,start_date,end_date)
            
        print(f'--- Processed all tickers for timeframe {g} ---\n')

if __name__ == '__main__':
    start = time.time()
    start_date = '2021-01-01 00:00:00'
    end_date = '2022-08-08 00:00:00'
    run_collection(start_date,end_date)
    print('( collect_data.py Total Execution Time: %s Seconds. )'%round(time.time()-start,2))