oanda_demo_key = '19584e7c34d3de74dde33805fff9b3c8-abfb8016ab3a666922c30fe2b0bd2319'
v20_acct_id = '101-001-10633723-002'
v20_mt4_acct_login = '5362258'
demo_api_url = 'https://api-fxpractice.oanda.com/v3'
SECURE_HEADER = {
    'Authorization': f'Bearer {oanda_demo_key}',
    'Content-Type': 'application/json'
}

BUY = 1
SELL = -1
NO_TRADE = 0