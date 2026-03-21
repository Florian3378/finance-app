import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

API_KEY = os.getenv('FMP_API_KEY')
BASE_URL = 'https://financialmodelingprep.com/stable'

def get_quote(symbol):
    """Récupère le prix actuel d'une action"""
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"Erreur FMP get_quote({symbol}): {e}")
        return None

def search_symbol(query):
    """Recherche une action par nom ou symbole"""
    url = f"{BASE_URL}/search-name?query={query}&limit=10&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP search({query}): {e}")
        return []

def get_multiple_quotes(symbols):
    """Récupère les prix de plusieurs actions - un appel par symbole"""
    quotes = {}
    for symbol in symbols:
        quote = get_quote(symbol)
        if quote:
            quotes[symbol] = quote
    return quotes

def get_company_profile(symbol):
    """Récupère le profil complet d'une entreprise (secteur, industrie, description...)"""
    url = f"{BASE_URL}/profile?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"Erreur FMP get_company_profile({symbol}): {e}")
        return None
    
def get_income_statement(symbol, limit=10):
    """Compte de résultats annuel"""
    url = f"{BASE_URL}/income-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP income_statement({symbol}): {e}")
        return []

def get_balance_sheet(symbol, limit=10):
    """Bilan comptable annuel"""
    url = f"{BASE_URL}/balance-sheet-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP balance_sheet({symbol}): {e}")
        return []

def get_cash_flow(symbol, limit=10):
    """Flux de trésorerie annuel"""
    url = f"{BASE_URL}/cash-flow-statement?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP cash_flow({symbol}): {e}")
        return []

def get_key_metrics(symbol, limit=10):
    """Métriques clés (PER, PEG, ROE, ROA...)"""
    url = f"{BASE_URL}/key-metrics?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP key_metrics({symbol}): {e}")
        return []

def get_ratios(symbol, limit=10):
    """Ratios financiers"""
    url = f"{BASE_URL}/ratios?symbol={symbol}&limit={limit}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erreur FMP ratios({symbol}): {e}")
        return []

def get_ratios_ttm(symbol):
    """Ratios TTM (Trailing Twelve Months) — les plus récents"""
    url = f"{BASE_URL}/ratios-ttm?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data else {}
    except Exception as e:
        print(f"Erreur FMP ratios_ttm({symbol}): {e}")
        return {}

def get_key_metrics_ttm(symbol):
    """Métriques TTM"""
    url = f"{BASE_URL}/key-metrics-ttm?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data else {}
    except Exception as e:
        print(f"Erreur FMP key_metrics_ttm({symbol}): {e}")
        return {}