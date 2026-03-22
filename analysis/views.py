import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portfolio.fmp_service import (
    search_symbol, get_company_profile, get_quote,
    get_income_statement, get_balance_sheet, get_cash_flow,
    get_quarterly_income, get_quarterly_balance, get_quarterly_cashflow,
)
from .ratios import calculate_ratios
from .scoring import calculate_score
from .piotroski import calculate_piotroski
from .beneish import calculate_beneish
from .valuation import calculate_all_valuations, SECTOR_PER
from portfolio.models import Favorite
from .altman import calculate_altman
import json as json_module


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

def compute_ttm(quarterly_income, quarterly_cashflow, quarterly_balance):
    """
    Calcule le TTM en additionnant les 4 derniers trimestres
    pour le compte de résultats et le cash flow.
    Le bilan utilise directement le dernier trimestre.
    """
    def sum_field(data, field):
        return sum((q.get(field) or 0) for q in data)

    if not quarterly_income:
        return {}, {}, {}

    # Compte de résultats TTM = somme des 4 trimestres
    income_ttm = {
        'revenue': sum_field(quarterly_income, 'revenue'),
        'grossProfit': sum_field(quarterly_income, 'grossProfit'),
        'operatingIncome': sum_field(quarterly_income, 'operatingIncome'),
        'ebitda': sum_field(quarterly_income, 'ebitda'),
        'netIncome': sum_field(quarterly_income, 'netIncome'),
        'eps': sum_field(quarterly_income, 'eps'),
        'epsdiluted': sum_field(quarterly_income, 'epsdiluted'),
        'interestExpense': sum_field(quarterly_income, 'interestExpense'),
        'weightedAverageShsOut': quarterly_income[0].get('weightedAverageShsOut', 0),
        'date': 'TTM',
    }

    # Cash flow TTM = somme des 4 trimestres
    cashflow_ttm = {
        'operatingCashFlow': sum_field(quarterly_cashflow, 'operatingCashFlow'),
        'capitalExpenditure': sum_field(quarterly_cashflow, 'capitalExpenditure'),
        'freeCashFlow': sum_field(quarterly_cashflow, 'freeCashFlow'),
        'dividendsPaid': sum_field(quarterly_cashflow, 'dividendsPaid'),
        'commonStockRepurchased': sum_field(quarterly_cashflow, 'commonStockRepurchased'),
        'depreciationAndAmortization': sum_field(quarterly_cashflow, 'depreciationAndAmortization'),
        'netCashUsedForInvestingActivites': sum_field(quarterly_cashflow, 'netCashUsedForInvestingActivites'),
        'netCashUsedProvidedByFinancingActivities': sum_field(quarterly_cashflow, 'netCashUsedProvidedByFinancingActivities'),
        'date': 'TTM',
    }

    # Bilan TTM = dernier trimestre disponible
    balance_ttm = dict(quarterly_balance)
    balance_ttm['date'] = 'TTM'

    return income_ttm, cashflow_ttm, balance_ttm

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
    quarterly_income = get_quarterly_income(symbol)
    quarterly_cashflow = get_quarterly_cashflow(symbol)
    quarterly_balance = get_quarterly_balance(symbol)
    income_ttm, cashflow_ttm, balance_ttm = compute_ttm(
        quarterly_income, quarterly_cashflow, quarterly_balance
    )

    # ── CALCUL LOCAL DES RATIOS ───────────────────────────────
    ratios = calculate_ratios(
        profile, quote,
        income_statements, balance_sheets, cash_flows,
        income_ttm, cashflow_ttm, balance_ttm,
    )
    
    # ── CALCUL PIOTROSKI/BENEISH/ALTMAN ───────────────────────────────
    piotroski = calculate_piotroski(
    income_statements, balance_sheets, cash_flows,
    income_ttm, cashflow_ttm, balance_ttm
    )
    beneish = calculate_beneish(income_statements, balance_sheets, cash_flows)
    beneish_json = json.dumps({
        'm_score': beneish['m_score'] if beneish else None,
        'label': beneish['label'] if beneish else '',
        'warnings': beneish['warnings'] if beneish else 0,
        'details': {
            k: {
                'value': v['value'],
                'label': v['label'],
                'interpretation': v['interpretation'],
                'warning': bool(v['warning']),
            }
            for k, v in beneish['details'].items()
        } if beneish else {}
    }) if beneish else 'null'
    altman = calculate_altman(
        profile, quote,
        income_statements, balance_sheets,
        income_ttm, balance_ttm
    )
    altman_json = json_module.dumps({
        'score': altman['score'] if altman else None,
        'version': altman['version'] if altman else '',
        'label': altman['label'] if altman else '',
        'z_original': altman['z_original'] if altman else None,
        'z_prime': altman['z_prime'] if altman else None,
        'details': {
            k: {
                'label': v['label'],
                'value': v['value'],
                'interpretation': v['interpretation'],
            }
            for k, v in altman['details'].items()
        } if altman else {}
    }) if altman else 'null'

    scoring = calculate_score(ratios, piotroski, beneish, altman)

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

    # Enrichit le TTM avec les marges calculées
    income_ttm_enriched = enrich_income_statements([income_ttm])[0] if income_ttm else {}

    is_favorite = Favorite.objects.filter(
        user=request.user, symbol=symbol
    ).exists()

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
        'income_ttm': income_ttm_enriched,
        'balance_ttm': balance_ttm,
        'cashflow_ttm': cashflow_ttm,
        'chart_data': chart_data,
        'categories_display': [
            ('growth', 'Croissance'),
            ('profitability', 'Rentabilité'),
            ('valuation', 'Valorisation'),
            ('safety', 'Sécurité'),
            ('quality', 'Qualité'),
        ],
        'growth_ratios': [
            ('revenue_cagr', 'CA CAGR'),
            ('net_income_cagr', 'RN CAGR'),
            ('eps_cagr', 'BPA CAGR'),
            ('fcf_cagr', 'FCF CAGR'),
        ],
        'profitability_ratios': [
            ('roe', 'ROE'),
            ('roic', 'ROIC'),
            ('roa', 'ROA'),
            ('net_margin', 'Marge nette'),
            ('gross_margin', 'Marge brute'),
            ('fcf_margin', 'Marge FCF'),
        ],
        'valuation_ratios': [
            ('per', 'PER'),
            ('peg', 'PEG'),
            ('pb', 'P/B'),
            ('ps', 'P/S'),
            ('pcf', 'P/FCF'),
            ('ev_ebitda', 'EV/EBITDA'),
            ('ev_revenue', 'EV/Revenue'),
        ],
        'safety_ratios': [
            ('debt_to_equity', 'Dette/FP'),
            ('net_debt_ebitda', 'Dette nette/EBITDA'),
            ('interest_coverage', 'Couv. intérêts'),
            ('current_ratio', 'Ratio courant'),
            ('quick_ratio', 'Ratio rapide'),
        ],
        'piotroski': piotroski,
        'beneish': beneish,
        'beneish_json': beneish_json,
        'altman': altman,
        'altman_json': altman_json,
        'is_favorite': is_favorite,
    }
    return render(request, 'analysis/company.html', context)


@login_required
def valuation_view(request, symbol):
    symbol = symbol.upper()

    # Récupération des données (avec cache)
    profile = get_company_profile(symbol) or {}
    quote = get_quote(symbol) or {}
    income_statements = get_income_statement(symbol, limit=5)
    income_statements = enrich_income_statements(income_statements)
    balance_sheets = get_balance_sheet(symbol, limit=5)
    cash_flows = get_cash_flow(symbol, limit=5)
    quarterly_income = get_quarterly_income(symbol)
    quarterly_cashflow = get_quarterly_cashflow(symbol)
    quarterly_balance = get_quarterly_balance(symbol)
    income_ttm, cashflow_ttm, balance_ttm = compute_ttm(
        quarterly_income, quarterly_cashflow, quarterly_balance
    )
    ratios = calculate_ratios(
        profile, quote, income_statements, balance_sheets, cash_flows,
        income_ttm, cashflow_ttm, balance_ttm
    )

    # Paramètres par défaut basés sur le CAGR historique
    default_growth = ratios.get('fcf_cagr') or ratios.get('revenue_cagr') or 5.0
    default_growth = min(max(default_growth, 0), 30)  # Clamp 0-30%

    params = {
        'growth_rate_1': float(request.GET.get('g1', round(default_growth, 1))),
        'growth_rate_2': float(request.GET.get('g2', round(default_growth * 0.6, 1))),
        'terminal_growth': float(request.GET.get('gt', 3.0)),
        'wacc': float(request.GET.get('wacc', 9.0)),
        'treasury_rate': float(request.GET.get('tr', 4.5)),
    }

    valuations = calculate_all_valuations(
        profile, quote, ratios,
        income_statements, balance_sheets, cash_flows,
        income_ttm, balance_ttm, cashflow_ttm,
        params
    )

    context = {
        'symbol': symbol,
        'profile': profile,
        'quote': quote,
        'params': params,
        'valuations': valuations,
        'default_growth': default_growth,
    }
    return render(request, 'analysis/valuation.html', context)