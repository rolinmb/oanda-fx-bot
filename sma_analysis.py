import pandas as pd
import matplotlib.pyplot as plt

def best_tf_cross(df,cur):
    df = df.loc[df['currency'] == cur] # Select rows with 'currency' == cur
    df = df[['currency','CROSS','tf','num_trades','total_gain']]
    cur_best_tf = df['tf'].iloc[0]
    cur_best_cross = df['CROSS'].iloc[0]
    cur_best_ntrades = df['num_trades'].iloc[0]
    best_cross_gain = df['total_gain'].iloc[0]
    for i,r in df.iterrows():
        if r.total_gain > best_cross_gain:
            cur_best_tf = r.tf
            cur_best_cross = r.CROSS
            cur_best_ntrades = r.num_trades
            best_cross_gain = r.total_gain
            
    msg = f'\t=> {cur} Best Crossover  -  {cur_best_cross} | {cur_best_tf} | {cur_best_ntrades} crossover events | PnL (pips) {round(best_cross_gain,2)}\n'
    print(f'{msg}\t=> {cur} All Backtested Strategies for All Timeframes:\n{df.to_string()}\n')

def cross_sum(df,cross,tfs):
    df = df.loc[df['CROSS'] == cross]
    df = df[['CROSS','currency','tf','total_gain']]
    for t in tfs: # For every timeframe detected in original DF
        new_df = df.loc[df['tf'] == t] # Select rows with 'tf' == t
        tf_cross_sum = 0.0
        for i,r in new_df.iterrows(): # Iterate through all cross results for each currency
            tf_cross_sum += r.total_gain
        print(f'\t=> {cross} Total PnL (pips) on {t} across all Currencies: {round(tf_cross_sum,2)}')   

    
    print('')


def build_plot(data,t,l):
    plt.figure(0)
    plt.title(t)
    plt.xlabel('Trade #')
    plt.ylabel('PnL (Pips)')
    plt.plot(data,label=l)
    plt.grid()
    plt.legend()
    plt.show()

# Works best of collected data and simulation is ran for 1 to 3 timeframes only
if __name__ == '__main__':
    test_res = pd.read_pickle('sma_test_results.pkl') # Load MAResult objects
    tfs = test_res['tf'].unique()
    trades = pd.read_pickle('all_trades.pkl') # Load trade events objects
    iName = test_res['iname'][0].upper() # Name of moving-average related function used
    print(f' * Total Number of trades {iName} strategy simulated across all forex pairs & timeframes: {trades.shape[0]}')
    #test_res = test_res[['pair','num_trades','total_gain','mashort','malong']]
    test_res[['pair','tf','num_trades','mashort','malong','currency','iname']]
    test_res['CROSS'] = iName+'_'+test_res.mashort.map(str)+'_'+test_res.malong.map(str) # Create new column of name of cross
    
    # Call best_tf_cross() to see best cross/timeframe for each currency
    print(f'\n * All {iName} Crossovers PnL Timeframe for all Currencies & Timeframes:')
    copy_df = test_res.copy()
    for currency in sorted(test_res['currency'].unique()):
        best_tf_cross(copy_df,currency)
    
    print(f'\n * PnL (pips) for All Crosses per Timeframe:')
    copy_df = test_res.copy()
    for c in test_res['CROSS'].unique():
        print(f'\t--- {c} Sums ---')
        cross_sum(copy_df,c,tfs)
        

    # Finding best pair/cross/timeframe by PnL
    best_cross = ''
    best_pair = ''
    best_tf = ''
    best_gain = 0.0
    best_trade = None
    # Iterate through all trades (on all timeframes for all crosses for all currencies)
    for i,r in trades.iterrows():
        if i == 0:
            best_cross = f'{r.MASHORT}_{r.MALONG}'
            best_tf = r.TF
            best_gain = r.PnL
            best_trade = r
        else:
            if r.PnL > best_gain:
                best_pair = r.PAIR
                best_tf = r.TF
                best_cross =  f'{r.MASHORT}_{r.MALONG}'
                best_gain = r.PnL
                best_trade = r
            else:
                continue
    
    print('\n *  Currency of largest PnL for single trade: %s'%best_pair)    
    print('\t=> Short//Long MA periods of largest winning trade: %s'%best_cross)
    print(f'\t=> Best Timeframe for {best_pair} {best_cross}: {best_tf}')
    print(f'\t=> Backtested PnL (Pips): {round(best_gain,2)}')
    
    '''
    sma_8_16 = sma_test_res[sma_test_res.CROSS=='MA_8_16'].copy()
    sma_8_16.sort_values(by='total_gain',ascending=False,inplace=True)
    total_p = len(sma_8_16.pair.unique())
    for cross in df_all_gains.CROSS.unique():
        df_temp = sma_test_res[sma_test_res.CROSS==cross]
        total_p = df_temp.shape[0]
        n_good = df_temp[df_temp.total_gain>0].shape[0]
        #print(f'{cross:12} {n_good:4} {(n_good/total_p)*100:4.0f}%')
    crosses = df_all_gains.CROSS.unique()
    #print(crosses)
    df_good = sma_test_res[(sma_test_res.CROSS.isin(crosses)) & (sma_test_res.total_gain)>0].copy()
    our_pairs = list(df_good.pair.value_counts()[:9].index)
    trades['CROSS'] = 'MA_'+trades.MASHORT.map(str)+'_'+trades.MALONG.map(str)
    c = 'MA_8_32'
    trades_cad_jpy_8_32 = trades[(trades.CROSS==c) & (trades.PAIR=='CAD_JPY')].copy()
    trades_cad_jpy_8_32['CUM_GAIN'] = trades_cad_jpy_8_32.PnL.cumsum()
    t = 'CAD_JPY SMA Analysis'
    l = 'CAD_JPY S'+c+' PnL'
    build_plot(trades_cad_jpy_8_32['CUM_GAIN'],t,l)
    '''