class TradeManager():
    def __init__(self,api,settings,log=None):
        self.api = api
        self.log = log
        self.settings = settings
        
    def log_message(self,msg):
        if self.log is not None:
            self.log.logger.debug(msg)
    
    def close_trades(self,pairs_to_close):
        open_trades, ok = self.api.open_trades()
        if not ok:
            self.log_message('trade_manager.py: close_trades() Error fetching open trades!')
            return
        
        to_close = [x.trade_id for x in open_trades if x.instrument in pairs_to_close]
        self.log_message(f'trade_manager.py: close_trades() Checking Pairs to Close: {pairs_to_close}')
        self.log_message(f'trade_manager.py: close_trades() Open Trades: {open_trades}')
        self.log_message(f'trade_manager.py: close_trades() IDs of Trades to Close: {to_close}')
        for t in to_close:
            ok =  self.api.close_trade(t)
            if not ok:
                self.log_message(f'trade_manager.py: close_trades() Trade ID {t} FAILED TO CLOSE')
            else:
                self.log_message(f'trade_manager.py: close_trades() Successfully Closed Trade ID {t}')
    
    def create_trades(self,trades_to_make):
        for t in trades_to_make:
            trade_id = self.api.place_trade(t['pair'],t['units'])
            if trade_id is not None:
                self.log_message(f'trade_manager.py: create_trades() Opened Trade ID: {trade_id}\n{t}')
            else:
                self.log_message(f'trade_manager.py: create_trades() FAILED TO OPEN {t}')
    
    def place_trades(self,trades_to_make):
        self.log_message(f'trade_manager.py.py: place_trades() New Trade Signals: {trades_to_make}')
        pairs = [x['pair'] for x in trades_to_make]
        self.close_trades(pairs)
        self.create_trades(trades_to_make)
        
if __name__ == '__main__':
    pass