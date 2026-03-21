import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portfolio.fmp_service import (
    search_symbol, get_company_profile, get_quote,
    get_income_statement, get_balance_sheet, get_cash_flow,
    get_key_metrics, get_ratios, get_ratios_ttm, get_key_metrics_ttm
)

@login_required
def search_view(request):
    """Barre de recherche d'actions"""
    query = request.GET.get('q', '')
    results = []
    if query:
        results = search_symbol(query)
    return render(request, 'analysis/search.html', {
        'query': query,
        'results': results
    })

@login_required
def company_view(request, symbol):
    """Page principale d'analyse d'une entreprise"""
    symbol = symbol.upper()
    active_tab = request.GET.get('tab', 'profile')

    # Données de base toujours chargées
    profile = get_company_profile(symbol) or {}
    quote = get_quote(symbol) or {}

    # Ratios TTM (toujours chargés pour l'onglet profil)
    ratios_ttm = get_ratios_ttm(symbol)
    metrics_ttm = get_key_metrics_ttm(symbol)

    # Données chargées selon l'onglet actif
    income_statements = []
    balance_sheets = []
    cash_flows = []
    chart_data = {}

    if active_tab in ['income', 'profile']:
        income_statements = get_income_statement(symbol)

    if active_tab == 'balance':
        balance_sheets = get_balance_sheet(symbol)

    if active_tab == 'cashflow':
        cash_flows = get_cash_flow(symbol)

    # Données pour les graphiques (onglet profil)
    if income_statements:
        years = [s.get('calendarYear', '') for s in reversed(income_statements)]
        revenues = [s.get('revenue', 0) / 1e9 for s in reversed(income_statements)]
        net_incomes = [s.get('netIncome', 0) / 1e9 for s in reversed(income_statements)]
        gross_margins = [
            round(s.get('grossProfitRatio', 0) * 100, 2)
            for s in reversed(income_statements)
        ]
        net_margins = [
            round(s.get('netIncomeRatio', 0) * 100, 2)
            for s in reversed(income_statements)
        ]
        chart_data = {
            'years': json.dumps(years),
            'revenues': json.dumps(revenues),
            'net_incomes': json.dumps(net_incomes),
            'gross_margins': json.dumps(gross_margins),
            'net_margins': json.dumps(net_margins),
        }

    # Calcul des ratios clés affichés
    ratios = {
        'per': ratios_ttm.get('priceEarningsRatioTTM') or metrics_ttm.get('peRatioTTM'),
        'peg': ratios_ttm.get('priceEarningsToGrowthRatioTTM') or metrics_ttm.get('pegRatioTTM'),
        'roe': ratios_ttm.get('returnOnEquityTTM'),
        'roa': ratios_ttm.get('returnOnAssetsTTM'),
        'roic': metrics_ttm.get('roicTTM'),
        'gross_margin': ratios_ttm.get('grossProfitMarginTTM'),
        'net_margin': ratios_ttm.get('netProfitMarginTTM'),
        'debt_to_equity': ratios_ttm.get('debtEquityRatioTTM'),
        'current_ratio': ratios_ttm.get('currentRatioTTM'),
        'pb': ratios_ttm.get('priceToBookRatioTTM'),
        'ps': ratios_ttm.get('priceToSalesRatioTTM'),
        'ev_ebitda': metrics_ttm.get('evToEbitdaTTM'),
        'dividend_yield': ratios_ttm.get('dividendYieldTTM'),
        'payout_ratio': ratios_ttm.get('payoutRatioTTM'),
    }

    context = {
        'profile': profile,
        'quote': quote,
        'symbol': symbol,
        'active_tab': active_tab,
        'ratios': ratios,
        'income_statements': income_statements,
        'balance_sheets': balance_sheets,
        'cash_flows': cash_flows,
        'chart_data': chart_data,
    }
    return render(request, 'analysis/company.html', context)