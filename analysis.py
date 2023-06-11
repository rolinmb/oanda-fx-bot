import pandas as pd
from demo_trade_config import *

def sma(data,t):
    return data.rolling(window=t).mean()

def ema(data,t):
    return data.ewm(span=t,adjust=False).mean()

def dema(data,t):
    e = ema(data,t)
    de = ema(e,t)
    return (2.0*e)-de
    
def roc(data,t):
    rates = []
    for i in range(t-1,data.size):
        rate = (data.iloc[i]-data.iloc[i-t])/data.iloc[i-t]
        rates.append(rate)
    return pd.Series(rates,index=data.index.values[t-1:])

class Analysis():
    def __init__(self,settings,api,pair,tf,indicator=sma,log=None):
        self.settings = settings
        self.log = log
        self.api = api
        self.pair = pair
        self.tf = tf
        self.ti = indicator
        
    def log_message(self,msg):
        if self.log is not None:
            self.log.logger.debug(msg)
        
    def fetch_candles(self,row_count,candle_time):
        status_code, df = self.api.fetch_candles(self.pair,n=row_count,tf=self.tf)
        if df is None:
            self.log_message(f'analysis.py: fetch_candles() Error fetching candles for pair: {self.pair} {candle_time}, df None')
            return None
        elif df.iloc[-1].time != candle_time:
            self.log_message(f'analysis.py fetch_candles() Error fetching candles for pair: {self.pair} {candle_time} vs {df.iloc[-1].time}')
            return None
        else:
            return df
    # Strategy implemented here    
    def process_candles(self,df):
        sMa = self.settings['short_ma']
        lMa = self.settings['long_ma']
        df.reset_index(drop=True,inplace=True)
        df['PAIR'] = self.pair
        df['SPREAD'] = df.ask_c - df.bid_c
        short_prev = 'PREV_SHORT'
        long_prev = 'LONG_PREV'
        short_col = f'MA_{sMa}'
        long_col = f'MA_{lMa}'
        df[short_col] = self.ti(df.mid_c,sMa)
        df[long_col] = self.ti(df.mid_c,lMa) 
        df[short_prev] = df[short_col].shift(1)
        df[long_prev] = df[long_col].shift(1)
        df['D_PREV'] = df[short_prev] - df[long_prev]
        df['D_NOW'] = df[short_col] - df[long_col]
        last = df.iloc[-1]
        result = NO_TRADE
        if last.D_NOW < 0 and last.D_PREV > 0:
            print('\t\t{DECISION: %s => SELL SIGNAL}'%self.pair)
            result = SELL
        elif last.D_NOW > 0 and last.D_PREV < 0:
            print('\t\t{DECISION: %s => BUY SIGNAL}'%self.pair)
            result = BUY
        else:
            print('\t\t{DECISION: %s => NO TRADE}'%self.pair)
            
        log_cols = ['time','volume','mid_c',
                    'SPREAD','PAIR',short_col,long_col,
                    short_prev,long_prev ,'D_PREV','D_NOW']   
        self.log_message(f'analysis.py: process_candles() Processed_df\n{df[log_cols].tail(2)}')
        self.log_message(f'analysis.py: process_candles() Trade Decision: {result}\n')
        return result
        
        
    def make_decision(self,candle_time):
        max_rows = self.settings['long_ma'] + 2
        self.log_message('')
        self.log_message(f'analysis.py: make_decision() pair: {self.pair} max_rows: {max_rows}')
        df = self.fetch_candles(max_rows,candle_time)
        if df is not None:
            return self.process_candles(df)
        
        return NO_TRADE

if __name__ == '__main__':
    pass