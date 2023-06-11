oanda_demo_key = 'DUMMY_DEMO_KEY'
v20_acct_id = 'DUMMY_ACCT_ID'
v20_mt4_acct_login = 'DUMMY_LOGIN'
demo_api_url = 'https://api-fxpractice.oanda.com/v3'
SECURE_HEADER = {
    'Authorization': f'Bearer {oanda_demo_key}',
    'Content-Type': 'application/json'
}

BUY = 1
SELL = -1
NO_TRADE = 0