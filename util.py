import datetime as dt
from dateutil.parser import *

def get_candles_data_fname(pair,tf):
    return f'{pair}_{tf}_candles.pkl'
    
def get_instruments_data_fname():
    return 'instruments.pkl'    
    
def time_utc():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    
def get_utc_dt_from_str(date_str):
    d = parse(date_str)
    return d.replace(tzinfo=dt.timezone.utc)
    
if __name__ == '__main__':
    pass