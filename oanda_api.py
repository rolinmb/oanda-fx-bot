import requests
import pandas as pd
from dateutil.parser import parse
from demo_trade_config import *
from util import *
from trader import *
from oanda_price import *
import sys
import json

class OandaAPI():
    def __init__(self):
        self.session = requests.Session()
    
    def make_request(self,url,params={},added_headers=None,verb='get',data=None,code_ok=200):
        headers = SECURE_HEADER
        if added_headers is not None:
            for k in added_headers.keys():
                headers[k] = added_headers[k]
        
        try:
            response = None
            if verb == 'post':
                response = self.session.post(url,params=params,headers=headers,data=data)
            elif verb == 'put':
                response = self.session.put(url,params=params,headers=headers,data=data)
            else:
                response = self.session.get(url,params=params,headers=headers,data=data)
            
            status_code = response.status_code
            if status_code == code_ok:
                json_data = response.json()
                return status_code, json_data
            else:
                return status_code, None
            
        except:
            print('ERROR')
            return 400, None
    
    def fetch_instruments(self,pair_list=None):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/instruments'
        params = None
        if pair_list is not None:
            params = dict(
                instruments = ','.join(pair_list))
            
        status_code, data = self.make_request(url)
        return status_code, data
        
    def get_instruments_df(self):
        status_code, data = self.fetch_instruments()
        if status_code == 200:
            df = pd.DataFrame.from_dict(data['instruments'])
            return df[['name','type','displayName','pipLocation','marginRate']]
        else:
            return None
            
    def save_instruments(self):
        df = self.get_instruments_df()
        if df is not None:
            df.to_pickle(get_instruments_data_fname())
    '''
    # Used in later examples and bot.py simulation
    def fetch_candles(self,pair,n=10,tf='H1'):
        url = f'{demo_api_url}/instruments/{pair}/candles'
        params = dict(granularity = tf,
                      price = 'MBA')
        params['count'] = n
        status_code, data = self.make_request(url,params=params)
        if status_code != 200:
            return status_code, None
            
        return status_code, OandaAPI.candles_to_df(data['candles'])
    '''
    def last_complete_candle(self,pair,tf='H1'):
        code, df = self.fetch_candles(pair,tf=tf)
        if df is None or df.shape[0] == 0:
            print(' * ERROR: oanda_api.py: last_complete_candle() Candlestick data is empty')
            return None
        return df.iloc[-1].time
    
    def close_trade(self,trade_id):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/trades/{trade_id}/close'
        # Make PUT request to close order with trade_id
        status_code, json_data = self.make_request(url,verb='put',code_ok=200)
        if status_code != 200:
            return False
            
        print(f' * Trade Close Confirmed [Trade ID # {trade_id}]\n{json_data}\n')    
        return True
    
    def set_sl_tp(self,price,order_type,trade_id):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/orders'
        data = {
            'order': {
                'timeInForce': 'GTC',
                'price': str(price),
                'type': order_type,
                'tradeID': str(trade_id)
            }
        }
        # Make POST request using make_request function to set SL or TP with API
        status_code, json_data = self.make_request(url,verb='post',data=json.dumps(data),code_ok=201)
        if status_code != 201:
            return False
        return True
    
    def place_trade(self,pair,units,take_profit=None,stop_loss=None):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/orders'
        data = {
            'order': {
                'units': units, # Units = Lot Size (100,000 = 1.0 lot, 1000 = 0.01 lots)
                'instrument': pair,
                'timeInForce': 'FOK', # Fill or Kill
                'type' : 'MARKET',
                'positionFill': 'DEFAULT'
            }
        }
        # Make POST request using make_request.. function to place trade with API
        status_code, json_data = self.make_request(url,verb='post',data=json.dumps(data),code_ok=201)
        if status_code != 201:
            return None
       
        trade_id = None 
        ok = True
        if 'orderFillTransaction' in json_data and 'tradeOpened' in json_data['orderFillTransaction']:
            trade_id = int(json_data['orderFillTransaction']['tradeOpened']['tradeID'])
            print(f' * Trade Placement Confirmed [Trade ID # {trade_id}]\n{json_data}\n')
            if take_profit is not None:
                if(self.set_sl_tp(take_profit,'TAKE_PROFIT',trade_id) == False): # Separate API call to set TP
                    ok = False
            if stop_loss is not None:
                if(self.set_sl_tp(stop_loss,'STOP_LOSS',trade_id) == False): # Separate API call to set SL
                    ok = False
        
        return trade_id, ok
     
    def open_trades(self):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/openTrades'
        status_code, data = self.make_request(url)
        if status_code != 200:
            return [], False
        if 'trades' not in data:
            return [], True
        
        trades = [Trader.TradeFromAPI(x) for x in data['trades']]
        return trades, True
    
    def fetch_prices(self,pair_list):
        url = f'{demo_api_url}/accounts/{v20_acct_id}/pricing'
        params = dict(
            instruments = ','.join(pair_list))
        
        status_code, data = self.make_request(url,params=params)
        if status_code != 200:
            return status_code, None
            
        prices = { x['instrument']: OandaPrice.PriceFromAPI(x) for x in data['prices'] }
        return status_code, prices
     
    @classmethod    
    def candles_to_df(cls,json_data):
        prices = ['mid','bid','ask']
        ohlc = ['o','h','l','c']
        our_data = []
        for candle in json_data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = candle['time']
            new_dict['volume'] = candle['volume']
            for price in prices:
                for o in ohlc:
                    new_dict[f'{price}_{o}'] = float(candle[price][o])
            our_data.append(new_dict)
        df = pd.DataFrame.from_dict(our_data)
        df['time'] = [parse(x) for x in df.time]
        return df
        
    # Used in earlier examples like collect_data.py and sma_sim.py
    def fetch_candles(self,pair,n=None,tf='H1',date_from=None,date_to=None): # Maximum 5000 candles/API call
        url = f'{demo_api_url}/instruments/{pair}/candles'
        params = dict(count = n,
                      granularity = tf,
                      price = 'MBA')
        
        if date_from is not None and date_to is not None:
            params['to'] = int(date_to.timestamp())
            params['from'] = int(date_from.timestamp())
        elif n is not None:
            params['count'] = n
        else: # If no count entered, default to 300 candles to return
            params['count'] = 300
            
        resp = self.session.get(url,params=params,headers=SECURE_HEADER)
        
        if resp.status_code != 200:
            return resp.status_code, None
            
        return resp.status_code, resp.json()
    
if __name__ == '__main__':
    '''
    #api = OandaAPI()
    #ode, prices = api.fetch_prices(['EUR_USD','SGD_CHF'])
    #print(prices)
    '''