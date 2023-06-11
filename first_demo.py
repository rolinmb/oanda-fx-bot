import requests
from demo_config import *
import pandas as pd

if __name__ == '__main__':
    sesh = requests.Session()
    # Showing how to fetch candlestick data
    instrument = 'EUR_USD' # Which financial instrument
    count = 10 # Number of candlesticks
    granularity = 'H1' # Timeframe
    candles_url = f'{demo_api_url}/instruments/{instrument}/candles'
    params = dict(count = count,
                  granularity = granularity, 
                  price = 'MBA')
    resp = sesh.get(candles_url,params=params,headers=SECURE_HEADER)
    data = resp.json()
    cndls = data['candles']
    '''
    print(len(data['candles']))
    for cndl in data['candles']:
        print(cndl)
    '''
    prices = ['mid','bid','ask']
    ohlc = ['o','h','l','c']
    '''
    print(data['candles'][0]['bid']['o'])
    for p in prices:
        for o in ohlc:
            print(f'{p}_{o}')
    '''
    # Fetch Available Instruments (Account Data) Example
    acct_url = f'{demo_api_url}/accounts/{v20_acct_id}/instruments'
    resp = sesh.get(acct_url,params=None,headers=SECURE_HEADER)
    data = resp.json()
    instruments = data['instruments']
    #print('Number of available instruments: %s'%len(instruments))
    # Formatting data from account available instruments endpoint
    inst_datapoints = []
    for item in instruments:
        new = dict(name = item['name'], type = item['type'], displayName = item['displayName'],
                   pipLocation = item['pipLocation'], marginRate = item['marginRate']) 
        inst_datapoints.append(new)
    # Save list of instruments to DataFrame (and pickle file)
    #instrument_df = pd.DataFrame.from_dict(inst_datapoints)
    #instrument_df.to_pickle('instruments.pkl')
    inst_df = pd.read_pickle('instruments.pkl')
    print(inst_df)
    # Fetch Candle Data Example
    our_data = []
    for candle in cndls:
        if candle['complete'] == False:
            continue
        new_dict = {}
        new_dict['time'] = candle['time']
        new_dict['volume'] = candle['volume']
        for p in prices:
            for o in ohlc:
                new_dict[f'{p}_{o}'] = candle[p][o] 
        our_data.append(new_dict)
    #print(our_data)
    #candles_df = pd.DataFrame.from_dict(our_data)
    cndls_out = '%s_%s.pkl'%(instrument,granularity)
    #candles_df.to_pickle(cndls_out)
    test_df = pd.read_pickle(cndls_out)
    print(test_df)