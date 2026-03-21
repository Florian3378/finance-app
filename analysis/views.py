import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portfolio.fmp_service import (
    search_symbol, get_company_profile, get_quote,
    get_income_statement, get_balance_sheet, get_cash_flow,
)
from .ratios import calculate_ratios
from .scoring import calculate_score


def enrich_income_statements(statements):
    """Ajoute les marges calculées à chaque année"""
    enriched = []
    for s in statements:
        revenue = s.get('revenue') or 0
        s['gross_margin'] = round(s.get('grossProfit', 0) / revenue * 100, 2) if revenue else None
        s['operating_margin'] = round(s.get('operatingIncome', 0) / revenue * 100, 2) if revenue else None
        s['net_margin'] = round(s.get('netIncome', 0) / revenue * 100, 2) if revenue else None
        s['ebitda_margin'] = round(s.get('ebitda', 0) / revenue * 100, 2) if revenue else None
        enriched.append(s)
    return enriched


@login_required
def search_view(request):
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
    symbol = symbol.upper()
    active_tab = request.GET.get('tab', 'profile')
    period = int(request.GET.get('period', 5))
    if period not in [5, 10]:
        period = 5

    # ── UN SEUL BLOC D'APPELS API (tout mis en cache) ────────
    profile = get_company_profile(symbol) or {}
    quote = get_quote(symbol) or {}
    income_statements = get_income_statement(symbol, limit=period)
    income_statements = enrich_income_statements(income_statements)
    balance_sheets = get_balance_sheet(symbol, limit=period)
    cash_flows = get_cash_flow(symbol, limit=period)

    # ── CALCUL LOCAL DES RATIOS ───────────────────────────────
    ratios = calculate_ratios(
        profile, quote,
        income_statements, balance_sheets, cash_flows
    )
    scoring = calculate_score(ratios)

    # ── DONNÉES GRAPHIQUES ────────────────────────────────────
    chart_data = {}
    if income_statements:
        rev_data = list(reversed(income_statements))
        chart_data = {
            'years': json.dumps([s.get('date', '')[:4] for s in rev_data]),
            'revenues': json.dumps([round((s.get('revenue') or 0) / 1e9, 2) for s in rev_data]),
            'net_incomes': json.dumps([round((s.get('netIncome') or 0) / 1e9, 2) for s in rev_data]),
            'gross_margins': json.dumps([
                round(s.get('grossProfit', 0) / s.get('revenue', 1) * 100, 2)
                if s.get('revenue') else 0
                for s in rev_data
            ]),
            'net_margins': json.dumps([
                round(s.get('netIncome', 0) / s.get('revenue', 1) * 100, 2)
                if s.get('revenue') else 0
                for s in rev_data
            ]),
            'operating_margins': json.dumps([
                round(s.get('operatingIncome', 0) / s.get('revenue', 1) * 100, 2)
                if s.get('revenue') else 0
                for s in rev_data
            ]),
            'fcf': json.dumps([round((cf.get('freeCashFlow') or 0) / 1e9, 2) for cf in list(reversed(cash_flows))]) if cash_flows else json.dumps([]),
        }

    context = {
        'profile': profile,
        'quote': quote,
        'symbol': symbol,
        'active_tab': active_tab,
        'period': period,
        'ratios': ratios,
        'scoring': scoring,
        'income_statements': income_statements,
        'balance_sheets': balance_sheets,
        'cash_flows': cash_flows,
        'chart_data': chart_data,
    }
    return render(request, 'analysis/company.html', context)