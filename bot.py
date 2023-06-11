import pprint
import time
from settings import *
from log_wrapper import *
from timing import *
from oanda_api import *
from analysis import *
from trade_manager import *

TEST_TF = 'M2'
SLEEP = 10.0

class TradingBot():
    def __init__(self):
        self.log = LogWrapper('TradingBot')
        self.a_log = LogWrapper('AnalysisBot')
        self.t_log = LogWrapper('Trade')
        self.trade_pairs = Settings.get_pairs()
        self.settings = Settings.load_settings()
        self.api = OandaAPI()
        self.trade_manager = TradeManager(self.api,self.settings,self.t_log)
        self.timings = { p: Timing(self.api.last_complete_candle(p,TEST_TF)) for p in self.trade_pairs }
        self.log_message(f'Bot.py: __init__() started with\n{pprint.pformat(self.settings)}')
        self.log_message(f'Bot.py: __init__() Timings\n{pprint.pformat(self.timings)}')
    
    def go_sleep(self,n):
        print(f' => Sleeping for {n} seconds...')
        time.sleep(n)
    
    def log_message(self,msg):
        self.log.logger.debug(msg)
    
    def update_timings(self):
        print(' * Called update_timings():')
        for pair in self.trade_pairs:
            cur = self.api.last_complete_candle(pair,TEST_TF)
            self.timings[pair].ready = False
            if cur is None:
                print('\t (%s no new %s candle yet, chance of lapse in data)'%(pair,TEST_TF))
            else:
                if cur > self.timings[pair].last_candle:
                    print(f'\t- New {pair} {TEST_TF} candle updated; {cur}')
                    self.timings[pair].ready = True
                    self.timings[pair].last_candle = cur
                    self.log_message(f'bot.py: update_timings() {pair} new candle {cur}')
                else:
                    print('\t (%s no new %s candle yet)'%(pair,TEST_TF))
    
    def process_pairs(self,cycle,indicator):
        trades_to_make = []
        print(' * Called process_pairs():')
        for pair in self.trade_pairs:
            if self.timings[pair].ready:
                print(f'\t- Ready to trade {pair}')
                self.log_message(f'bot.py: process_pairs() Ready to trade {pair}')
                a = Analysis(self.settings[pair],self.api,pair,TEST_TF,indicator=indicator,log=self.a_log)
                result = a.make_decision(self.timings[pair].last_candle)
                units = result*self.settings[pair]['units']
                if units != 0:
                    self.log_message(f'bot.py: process_pairs() Bot Identified a trade of {units} here')
                    trades_to_make.append({'pair': pair,'units': units})
        
        if len(trades_to_make) > 0:
            print(f'\nTrades Detected on Timing Cycle {cycle}:\n{trades_to_make}\n')
            self.log_message(f'bot.py: process_pairs() Trades Detected on Timing Cycle {cycle}:\n * {trades_to_make}')
            self.trade_manager.place_trades(trades_to_make)
            
    def run(self,indicator,updates):
        cycle = 1
        max_updates = updates + 1
        while cycle < max_updates:
            print(f'Timing Cycle {cycle}:')
            self.log_message(f'bot.py: run() Timing Cycle {cycle}')
            self.update_timings()
            self.process_pairs(cycle,indicator)
            if cycle < max_updates-1:
                self.go_sleep(SLEEP)    
            cycle += 1
        print('\nEXITING:')
        
if __name__ == '__main__':
    start = time.time()
    bot = TradingBot()
    indicator = sma
    bot.run(indicator,150)
    print('( bot.py Total Execution Time: %s Seconds. )'%round(time.time()-start,2))