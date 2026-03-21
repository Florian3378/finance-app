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