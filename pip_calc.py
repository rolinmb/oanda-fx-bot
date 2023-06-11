from oanda_api import *

TEST_LIST = ['EUR_USD','GBP_JPY','AUD_NZD','SGD_CHF']

class PipCalculator():
    def __init__(self,api,pairs_list):
        self.api = api
        self.pairs_list = pairs_list
        ok, instruments_raw = api.fetch_instruments(pairs_list)
        self.marginRates = { x['name'] : float(x['marginRate']) for x in instruments_raw['instruments']}
        ok, self.prices = api.fetch_prices(pairs_list)
        
    def get_trade_margin_for_units(self,units,pair):    
        rate = self.marginRates[pair]
        price = self.prices[pair]
        trade_margin = price.mid * rate * price.mid_conv * units
        return trade_margin
        
    def get_units_for_margin(self,margin,pair):
        rate = self.marginRates[pair]
        price = self.prices[pair]
        units = margin / (price.mid * rate * price.mid_conv)
        return int(units)
        
if __name__ == '__main__':
    api = OandaAPI()
    r = PipCalculator(api,TEST_LIST)
    print('Pair , Margin ($) Req for 10,000 units (0.1 lots) , Units Req for $2000 Margin')
    for p in TEST_LIST:
        print(p,
              round(r.get_trade_margin_for_units(10000,p),2),
              r.get_units_for_margin(2000,p))