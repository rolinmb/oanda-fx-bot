import pandas as pd

def create_csv(results):
    results = results[['pair','num_trades','total_gain','mashort','malong']].copy()
    results['CROSS'] = 'MA_'+results.mashort.map(str)+'_'+results.malong.map(str)
    results.sort_values(by=['pair','total_gain'],ascending=[True,False],inplace=True)
    for p in results.pair.unique():
        print('Creating CSV file for pair %s:'%p)
        temp_df = results[results.pair==[p]]
        temp_df.to_csv('%s'%p)

if __name__ == '__main__':
    df = pd.read_pickle('sma_test_results.pkl')
    create_csv(df)