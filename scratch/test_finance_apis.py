import requests
import json

def test_yahoo_finance():
    symbol = "RELIANCE.NS" # Added .NS for Indian index
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Yahoo Search ({symbol}) Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            print(f"Price: {price}")
        else:
            print(f"Resp: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_coingecko():
    coin_id = "bitcoin"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,inr"
    try:
        resp = requests.get(url, timeout=10)
        print(f"CoinGecko ({coin_id}) Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Price: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yahoo_finance()
    test_coingecko()
