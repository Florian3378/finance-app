import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.cache import cache

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

API_KEY = os.getenv('FMP_API_KEY')
BASE_URL = 'https://financialmodelingprep.com/stable'


def _get(url, cache_key, timeout=60 * 60 * 24):
    """Appel API générique avec cache automatique"""
    cached = cache.get(cache_key)
    if cached is not None:
        print(f"[CACHE HIT] {cache_key}")
        return cached if cached != '__ERROR__' else None
    try:
        print(f"[API CALL] {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cache.set(cache_key, data, timeout)
            return data
        else:
            print(f"[API ERROR] {response.status_code} - {response.text[:100]}")
            cache.set(cache_key, '__ERROR__', 60 * 60)
            return None
    except Exception as e:
        print(f"[API EXCEPTION] {e}")
        return None


def get_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"quote_{symbol}", timeout=60 * 5)
    if data and len(data) > 0:
        return data[0]
    return None


def search_symbol(query):
    url = f"https://financialmodelingprep.com/stable/search-name?query={query}&limit=10&apikey={API_KEY}"
    data = _get(url, f"search_{query}", timeout=60 * 60)
    return data or []


def get_company_profile(symbol):
    url = f"{BASE_URL}/profile?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"profile_{symbol}")
    if data and len(data) > 0:
        return data[0]
    return None


def get_income_statement(symbol, limit=5):
    url = f"{BASE_URL}/income-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    return _get(url, f"income_{symbol}_{limit}") or []


def get_balance_sheet(symbol, limit=5):
    url = f"{BASE_URL}/balance-sheet-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    return _get(url, f"balance_{symbol}_{limit}") or []


def get_cash_flow(symbol, limit=5):
    url = f"{BASE_URL}/cash-flow-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    return _get(url, f"cashflow_{symbol}_{limit}") or []


def get_multiple_quotes(symbols):
    """Récupère les prix de plusieurs actions"""
    quotes = {}
    for symbol in symbols:
        quote = get_quote(symbol)
        if quote:
            quotes[symbol] = quote
    return quotes


def get_quarterly_income(symbol, limit=4):
    """4 derniers trimestres du compte de résultats"""
    url = f"{BASE_URL}/income-statement?symbol={symbol}&period=quarter&limit={limit}&apikey={API_KEY}"
    return _get(url, f"income_q_{symbol}_{limit}") or []


def get_quarterly_balance(symbol):
    """Dernier bilan trimestriel"""
    url = f"{BASE_URL}/balance-sheet-statement?symbol={symbol}&period=quarter&limit=1&apikey={API_KEY}"
    data = _get(url, f"balance_q_{symbol}")
    return data[0] if data else {}


def get_quarterly_cashflow(symbol, limit=4):
    """4 derniers trimestres du cash flow"""
    url = f"{BASE_URL}/cash-flow-statement?symbol={symbol}&period=quarter&limit={limit}&apikey={API_KEY}"
    return _get(url, f"cashflow_q_{symbol}_{limit}") or []


def get_market_indices():
    """Récupère les principaux indices boursiers"""
    symbols = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^GDAXI', '^FCHI', '^N225']
    results = []
    for symbol in symbols:
        url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
        data = _get(url, f"index_{symbol}", timeout=60 * 60 * 12)
        if data and len(data) > 0:
            results.append(data[0])
    return results


def get_biggest_gainers():
    """Top hausses du jour"""
    url = f"{BASE_URL}/biggest-gainers?apikey={API_KEY}"
    data = _get(url, "biggest_gainers", timeout=60 * 60 * 12)
    return data[:10] if data else []


def get_biggest_losers():
    """Top baisses du jour"""
    url = f"{BASE_URL}/biggest-losers?apikey={API_KEY}"
    data = _get(url, "biggest_losers", timeout=60 * 60 * 12)
    return data[:10] if data else []


def get_most_active():
    """Actions les plus échangées"""
    url = f"{BASE_URL}/most-actives?apikey={API_KEY}"
    data = _get(url, "most_actives", timeout=60 * 60 * 12)
    return data[:10] if data else []