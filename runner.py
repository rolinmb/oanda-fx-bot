from oanda_api import *

if __name__ == '__main__':
    api = OandaAPI()
    trade_id = None
    while True:
        msg = 'Enter Command [''T'' to trade; ''C'' to close trade (ID: %s); ''Q'' to exit program]:\n'%trade_id
        command = input(msg).upper()
        if command == 'T':
            print('Placing trade...')
            trade_id, ok = api.place_trade('EUR_USD',1000) # Long EUR/USD 0.01 lot size
        if command == 'C':
            if trade_id is not None:
                print('Closing Trade ID %s...'%trade_id)
                closed = api.close_trade(trade_id)
                if closed:
                    trade_id = None
                else:
                    print(' * Trade ID %s was not closed'%trade_id)
                    continue
            else:
                print(' * Most recent trade already closed')
        if command == 'Q':
            print(' * Exiting')
            break   