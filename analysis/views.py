import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portfolio.fmp_service import (
    search_symbol, get_company_profile, get_quote,
    get_income_statement, get_balance_sheet, get_cash_flow,
)
from .ratios import calculate_ratios


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
    balance_sheets = get_balance_sheet(symbol, limit=period)
    cash_flows = get_cash_flow(symbol, limit=period)

    # ── CALCUL LOCAL DES RATIOS ───────────────────────────────
    ratios = calculate_ratios(
        profile, quote,
        income_statements, balance_sheets, cash_flows
    )

    # ── DONNÉES GRAPHIQUES ────────────────────────────────────
    chart_data = {}
    if income_statements:
        rev_data = list(reversed(income_statements))
        chart_data = {
            'years': json.dumps([s.get('calendarYear', '') for s in rev_data]),
            'revenues': json.dumps([round((s.get('revenue') or 0) / 1e9, 2) for s in rev_data]),
            'net_incomes': json.dumps([round((s.get('netIncome') or 0) / 1e9, 2) for s in rev_data]),
            'gross_margins': json.dumps([round((s.get('grossProfitRatio') or 0) * 100, 2) for s in rev_data]),
            'net_margins': json.dumps([round((s.get('netIncomeRatio') or 0) * 100, 2) for s in rev_data]),
            'fcf': json.dumps([round((cf.get('freeCashFlow') or 0) / 1e9, 2) for cf in list(reversed(cash_flows))]) if cash_flows else json.dumps([]),
        }

    context = {
        'profile': profile,
        'quote': quote,
        'symbol': symbol,
        'active_tab': active_tab,
        'period': period,
        'ratios': ratios,
        'income_statements': income_statements,
        'balance_sheets': balance_sheets,
        'cash_flows': cash_flows,
        'chart_data': chart_data,
    }
    return render(request, 'analysis/company.html', context)