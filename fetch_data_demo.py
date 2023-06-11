import requests
from demo_config import *
import pandas as pd

if __name__ == '__main__':
    sesh = requests.Session()
    ins_df = pd.read_pickle('instruments.pkl')
    fiat = ['EUR','GBP','USD','JPY','CHF','NZD','CAD'] #Currencies we're interested in
    # Create function here so we dont have to pass Session() object
    def fetch_candles(pair,n,tf):
        url = '%s/instruments/%s/candles'%(demo_api_url,pair)
        params = dict(count = n,
                granularity = tf,
                price = 'MBA')
        resp = sesh.get(url, params = params, headers = SECURE_HEADER)
        return resp.status_code,resp.json()
    # Use fetch_candles
    code, json = fetch_candles('EUR_USD',10,'H1')
    # Create function to get candles and return as DF
    def get_candles_df(json):
        prices = ['mid','bid','ask']
        ohlc = ['o','h','l','c']
        our_data = []
        for candle in json['candles']:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = candle['time']
            new_dict['volume'] = candle['volume']
            for p in prices:
                for o in ohlc:
                    new_dict[f'{p}_{o}'] = candle[p][o]
            our_data.append(new_dict)
        return pd.DataFrame.from_dict(our_data)
    # Call get_candles_df 
    df = get_candles_df(json)
    # Create function to save data to Pickle
    def save_file(candles_df,pair,tf):
        candles_df.to_pickle(f'{pair}_{tf}_candles.pkl')
    # Create function for creating data
    def create_data(pair,tf):
        code, json = fetch_candles(pair,4000,tf)
        if code != 200:
            print(pair,'Error')
            return
        df = get_candles_df(json)
        print(f'{pair} loaded {df.shape[0]} candles from {df.time.min()} tp {df.time.max()}')
        save_file(df,pair,tf)
    # Call cretate_data to loop through pair names and build DataFrame
    for c1 in fiat:
        for c2 in fiat:
            pair = f'{c1}_{c2}'
            if pair in ins_df.name.unique():
                create_data(pair,'H1')