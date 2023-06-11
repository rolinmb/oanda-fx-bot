from dateutil.parser import parse

class Trader():
    def __init__(self,oanda_ob):
        self.unrealizedPNL = float(oanda_ob['unrealizedPL'])
        self.currentUnits = int(oanda_ob['currentUnits'])
        self.trade_id = int(oanda_ob['id'])
        self.openTime = parse(oanda_ob['openTime'])
        self.instrument = oanda_ob['instrument']
        
    def __repr__(self):    
        return str(vars(self))
    
    @classmethod
    def TradeFromAPI(cls,api_object):
        return Trader(api_object)
    
if __name__ == '__main__':
    pass