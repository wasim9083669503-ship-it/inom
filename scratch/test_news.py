import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def test_news_integrated(query=None):
    # This matches the new logic in app.py and astra.py
    api_key = os.getenv('GNEWS_API_KEY') or os.getenv('NEWS_API_KEY')
    print(f"Using API Key: {'GNEWS_API_KEY' if os.getenv('GNEWS_API_KEY') else 'NEWS_API_KEY' if os.getenv('NEWS_API_KEY') else 'NONE'}")
    
    if not api_key:
        print("❌ Error: No API key found in environment!")
        return

    if query:
        url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&apiKey={api_key}&pageSize=5&language=en"
        print(f"Searching for topic: {query}")
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}&pageSize=5"
        print("Fetching top headlines (India)")

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            print(f"✅ Success! Articles found: {len(articles)}")
            for i, art in enumerate(articles[:3]):
                print(f"{i+1}. {art['title']}")
        else:
            print(f"❌ API Error: {data.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("--- Test 1: Top Headlines ---")
    test_news_integrated()
    print("\n--- Test 2: Topic Search (Technology) ---")
    test_news_integrated("technology")
