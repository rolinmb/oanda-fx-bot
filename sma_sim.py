import pandas as pd
from dateutil.parser import *
from util import *
from instrument import *
from analysis import *
import time

CURRENCIES = 'GBP,EUR,USD,CAD,JPY,NZD,CHF,AUD' # Pairs to backtest on
INCREMENTS = { # Timeframes to backtest strategy over
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
    #'H12': 720,
    #'D': 1440
}

class MAResult():
    def __init__(self,df_trades,pair,params):
        self.pair = pair
        self.df_trades = df_trades
        self.params = params
    
    def result_ob(self):
        d = {
            'pair': self.pair,
            'num_trades': self.df_trades.shape[0],
            'total_gain': self.df_trades.PnL.sum(),
            'mean_gain': self.df_trades.PnL.mean(),
            'min_gain': self.df_trades.PnL.min(),
            'max_gain': self.df_trades.PnL.max()
        }
        for k,v in self.params.items():
            d[k] = v
            
        return d

def is_trade(row):
    if row.DIFF >= 0 and row.DIFF_PREV < 0:
        return 1 # Upward cross detected
    if row.DIFF <= 0 and row.DIFF_PREV > 0:
        return -1 # Downward cross detected
    return 0 # No cross detected or are equal

def get_ma_col(ma):
    return f'MA_{ma}'
    
# Determine where crossovers occured and calculate profits that would have been made
def evaluate_pair(i_pair,mashort,malong,price_data,tf,iName):
    price_data = price_data[['time','mid_c',get_ma_col(mashort),get_ma_col(malong)]].copy()
    price_data['DIFF'] = price_data[get_ma_col(mashort)]-price_data[get_ma_col(malong)]
    price_data['DIFF_PREV'] = price_data.DIFF.shift(1)
    price_data['IS_TRADE'] = price_data.apply(is_trade,axis=1)
    df_trades = price_data[price_data.IS_TRADE!=0].copy()
    df_trades['DELTA'] = (df_trades.mid_c.diff()/i_pair.pipLocation).shift(1)
    df_trades['PnL'] = df_trades['DELTA']*df_trades['IS_TRADE']
    df_trades['PAIR'] = i_pair.name
    df_trades['INAME'] = iName
    df_trades['TF'] = tf
    df_trades['MASHORT'] = mashort
    df_trades['MALONG'] = malong
    del df_trades[get_ma_col(mashort)]
    del df_trades[get_ma_col(malong)]
    df_trades['time'] = [parse(x) for x in df_trades.time]
    df_trades['time_delta'] = df_trades.time.diff().shift(-1)
    df_trades['time_delta'] = [x.total_seconds()/3600 for x in df_trades.time_delta]
    df_trades.dropna(inplace=True)
    print(f"\t\t* BACKTEST RESULTS: {i_pair.name} {mashort}:{malong} {tf}\n\t\tNo. of Trades: {df_trades.shape[0]}\n\t\tPnL: {df_trades['PnL'].sum():.0f} pips\n")
    return MAResult(df_trades = df_trades,
                    pair = i_pair,
                    params = {'mashort': mashort,
                              'malong': malong,
                              'currency': i_pair.name,
                              'iname': iName,
                              'tf': tf,}
    )
    
def get_price_data(pair,tf):
    df = pd.read_pickle(get_candles_data_fname(pair,tf))
    non_cols = ['time','volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)
    return df[['time','mid_c']]
    
def process_data(ma_short,ma_long,price_data,indicator):   
    ma_list = set(ma_short+ma_long) # Combine sets of short and long moving average periods
    for ma in ma_list:
        price_data[get_ma_col(ma)] = indicator(price_data.mid_c,ma) # create new columns with data from indicator applied 
    return price_data
    
def store_trades(res):
    all_trade_df_list = [x.df_trades for x in res]
    all_trade_df = pd.concat(all_trade_df_list)
    all_trade_df.to_pickle('all_trades.pkl')
    print(' * sma_sim.py results saved to ''all_trades.pkl''\n')
    
def process_results(res):
    res_list = [r.result_ob() for r in res]
    df = pd.DataFrame.from_dict(res_list)
    df.to_pickle('sma_test_results.pkl')
    print('\n=> Results Processed; DataFrame Shape: %s , Total Crossover Events/Trades Analyzed: %s\n'%(df.shape,df.num_trades.sum()))
    
def get_test_pairs(fiat_str,iName):
    existing = Instrument.get_instruments_dict().keys()
    pairs = fiat_str.split(',')
    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f'{p1}_{p2}'
            if p in existing:
                test_list.append(p)
    print('\nCurrency pairs used for this %s simulation: \n%s\n'%(iName,test_list))
    return test_list

def run(ma_short,ma_long,indicator=sma):
    iName = indicator.__name__.upper()
    ma_short = [8,16,32,64]
    ma_long = [32,64,96,128,256]
    test_pairs = get_test_pairs(CURRENCIES,iName)
    results = []
    for tf in INCREMENTS:
        print(f'* Backtesting All Pairs for granularity {tf}\n')
        for pair in test_pairs:
            print(f'\tRunning {iName} Backtest on {pair} {tf}:')
            i_pair = Instrument.get_instruments_dict()[pair]
            price_data = get_price_data(pair,tf)
            price_data = process_data(ma_short,ma_long,price_data,indicator) # Fetch data with indicators applied
            for _malong in ma_long:
                for _mashort in ma_short:
                    if _mashort >= _malong: #Skip over same moving averages or where short window > long window
                        continue
                    results.append(evaluate_pair(i_pair,_mashort,_malong,price_data.copy(),tf,iName))
            print(f'\t(Finished Backtest {iName} {pair} {tf})\n')
        print(f'[Finished All {iName} Backtests for granularity {tf}]\n')
        
    process_results(results)
    store_trades(results)

# Backtest strategy with desired indicator
if __name__ == '__main__':
    start = time.time()
    indicator = sma # from analysis.py
    #indicator = ema can also work?
    ma_short = [8,16,32,64]
    ma_long = [32,64,96,128,256]
    run(ma_short,ma_long,indicator)
    print('( sma_sim.py Total Execution Time: %s Seconds. )'%round(time.time()-start,2))