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
        return cached
    try:
        print(f"[API CALL] {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cache.set(cache_key, data, timeout)
            return data
        else:
            print(f"[API ERROR] {response.status_code} - {response.text[:100]}")
            return None
    except Exception as e:
        print(f"[API EXCEPTION] {e}")
        return None


def get_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"quote_{symbol}", timeout=60 * 5)  # Cache 5 min pour les prix
    if data and len(data) > 0:
        return data[0]
    return None


def search_symbol(query):
    url = f"{BASE_URL}/search-name?query={query}&limit=10&apikey={API_KEY}"
    data = _get(url, f"search_{query}", timeout=60 * 60)  # Cache 1h
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

def get_income_statement_ttm(symbol):
    """Compte de résultats TTM"""
    url = f"{BASE_URL}/income-statement-ttm?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"income_ttm_{symbol}")
    return data[0] if data else {}

def get_balance_sheet_ttm(symbol):
    """Bilan TTM"""
    url = f"{BASE_URL}/balance-sheet-statement-ttm?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"balance_ttm_{symbol}")
    return data[0] if data else {}

def get_cash_flow_ttm(symbol):
    """Cash flow TTM"""
    url = f"{BASE_URL}/cash-flow-statement-ttm?symbol={symbol}&apikey={API_KEY}"
    data = _get(url, f"cashflow_ttm_{symbol}")
    return data[0] if data else {}