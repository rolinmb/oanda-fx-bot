import pandas as pd
from dateutil.parser import *
#import plotly.graph_objects as go
import matplotlib.pyplot as plt
from instrument import *
from analysis import *
from util import *

def get_candles_data_fname(pair,tf):
    return f'{pair}_{tf}_candles.pkl'

if __name__ == '__main__':
    pair = 'GBP_JPY'
    tf = 'H1'
    ma_list = [16,64] # Periods for SMA's to use in MA Crossover Strategy
    i_pair = Instrument.get_instrument_by_name(pair)
    df = pd.read_pickle(get_candles_data_fname(pair,tf))
    non_cols = ['time','volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)
    df_ma = df[['time','mid_o','mid_h','mid_l','mid_c']].copy()
    for t in ma_list:
        df_ma[f'MA_{t}'] = sma(df_ma.mid_c,t) # Call defined SMA function from analysis.py
    df_ma.dropna(inplace=True)
    df_ma.reset_index(drop=True,inplace=True)
    def is_trade(row):
        if row.DIFF >= 0 and row.DIFF_PREV < 0: # upwwards SMA cross
            return 1
        if row.DIFF <= 0 and row.DIFF_PREV > 0: # downwards SMA cross
            return -1
        return 0
    # Define new column to detect crossing of SMA's
    #  * Subtract SMA(64) from SMA(16) & use previous difference to detect crossovers
    # => enter trade when DIFF turns positive from 0 or negative 
    # => exit trade when DIFF turns negative from 0 or positive
    df_ma['DIFF'] = df_ma.MA_16-df_ma.MA_64 
    df_ma['DIFF_PREV'] = df_ma.DIFF.shift(1)
    df_ma['IS_TRADE'] = df_ma.apply(is_trade,axis=1) # apply is_trade function to create new column of signals
    df_trades = df_ma[df_ma.IS_TRADE!=0].copy()
    df_trades['DELTA'] = (df_trades.mid_c.diff()/i_pair.pipLocation).shift(-1)
    df_trades['PnL'] = df_trades['DELTA']*df_trades['IS_TRADE']
    df_trades['time'] = [parse(x) for x in df_trades.time]
    df_trades['time_delta'] = df_trades.time.diff().shift(-1)
    df_trades['time_delta'] = [x.total_seconds()/3600 for x in df_trades.time_delta]
    print(df_trades.info())
    print(df_trades.head())
    #print('SMA 16/64 Crossover on %s Total PnL: $%s'%(pair,round(df_trades['PnL'].sum(),2)))
    '''
    # Plotly Plotting
    df_plot = df.iloc[-100:]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x = df_plot.time,
        open = df_plot.mid_o, high = df_plot.mid_h,
        low = df_plot.mid_l, close = df_plot.mid_c))
    fig.update_layout(width = 1000, height = 400,
        margin = dict(l = 10, r = 10, b = 10, t = 10),
        font = dict(size = 10, color = '#1e1e1e'),
        paper_bgcolor = '#1e1e1e',
        plot_bgcolor = '#1e1e1e')
    fig.update_xaxes(
        gridcolor = '#1f292f',
        showgrid = True,
        fixedrange = True,
        rangeslider = dict(visible = False)
    )
    fig.update_yaxes(
        gridcolor = '#1f292f',
        showgrid = True
    )
    fig.show()
    '''