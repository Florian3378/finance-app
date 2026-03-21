def safe_div(a, b):
    try:
        if b and b != 0:
            return a / b
        return None
    except:
        return None

def pct(value, decimals=2):
    if value is not None:
        return round(value * 100, decimals)
    return None

def fmt(value, decimals=2):
    if value is not None:
        return round(value, decimals)
    return None

def cagr(start, end, years):
    """Calcule le taux de croissance annualisé"""
    try:
        if start and end and years > 0 and start > 0:
            return round(((end / start) ** (1 / years) - 1) * 100, 2)
        return None
    except:
        return None


def calculate_ratios(profile, quote, income_statements, balance_sheets,
                     cash_flows, income_ttm=None, balance_ttm=None, cash_flow_ttm=None):

    ratios = {}
    income_ttm = income_ttm or {}
    balance_ttm = balance_ttm or {}
    cash_flow_ttm = cash_flow_ttm or {}

    # Utilise TTM si dispo, sinon dernière année
    inc = income_ttm if income_ttm else (income_statements[0] if income_statements else {})
    bal = balance_ttm if balance_ttm else (balance_sheets[0] if balance_sheets else {})
    cf = cash_flow_ttm if cash_flow_ttm else (cash_flows[0] if cash_flows else {})

    price = quote.get('price', 0) or 0
    shares = inc.get('weightedAverageShsOut') or (income_statements[0].get('weightedAverageShsOut', 0) if income_statements else 0)
    market_cap = profile.get('mktCap', 0) or (price * shares if price and shares else 0)

    # ── COMPTE DE RÉSULTATS ───────────────────────────────────
    revenue = inc.get('revenue', 0) or 0
    gross_profit = inc.get('grossProfit', 0) or 0
    ebitda = inc.get('ebitda', 0) or 0
    operating_income = inc.get('operatingIncome', 0) or 0
    net_income = inc.get('netIncome', 0) or 0
    eps = inc.get('epsdiluted') or inc.get('eps', 0) or 0
    interest_expense = abs(inc.get('interestExpense', 0) or 0)

    # ── BILAN ─────────────────────────────────────────────────
    total_assets = bal.get('totalAssets', 0) or 0
    total_equity = bal.get('totalStockholdersEquity', 0) or 0
    total_debt = bal.get('totalDebt', 0) or (
        (bal.get('longTermDebt', 0) or 0) + (bal.get('shortTermDebt', 0) or 0)
    )
    current_assets = bal.get('totalCurrentAssets', 0) or 0
    current_liabilities = bal.get('totalCurrentLiabilities', 0) or 0
    cash = bal.get('cashAndCashEquivalents', 0) or 0
    inventory = bal.get('inventory', 0) or 0
    total_liabilities = bal.get('totalLiabilities', 0) or 0

    # ── CASH FLOW ─────────────────────────────────────────────
    operating_cf = cf.get('operatingCashFlow', 0) or 0
    capex = cf.get('capitalExpenditure', 0) or 0
    free_cf = cf.get('freeCashFlow', 0) or (operating_cf + capex)
    dividends = cf.get('dividendsPaid', 0) or 0

    # ── VALORISATION ──────────────────────────────────────────
    ratios['per'] = fmt(safe_div(price, eps)) if eps and eps > 0 else None
    ratios['pb'] = fmt(safe_div(market_cap, total_equity)) if total_equity else None
    ratios['ps'] = fmt(safe_div(market_cap, revenue)) if revenue else None
    ratios['pcf'] = fmt(safe_div(market_cap, free_cf)) if free_cf and free_cf > 0 else None
    ev = (market_cap or 0) + (total_debt or 0) - (cash or 0)
    ratios['ev'] = fmt(ev / 1e9) if ev else None
    ratios['ev_ebitda'] = fmt(safe_div(ev, ebitda)) if ebitda and ebitda > 0 else None
    ratios['ev_revenue'] = fmt(safe_div(ev, revenue)) if revenue else None

    # PEG
    if len(income_statements) >= 2:
        eps_curr = income_statements[0].get('epsdiluted') or income_statements[0].get('eps', 0)
        eps_prev = income_statements[1].get('epsdiluted') or income_statements[1].get('eps', 0)
        if eps_prev and eps_prev > 0 and eps_curr:
            eps_growth = ((eps_curr - eps_prev) / abs(eps_prev)) * 100
            ratios['peg'] = fmt(ratios['per'] / eps_growth) if eps_growth > 0 and ratios.get('per') else None
        else:
            ratios['peg'] = None
    else:
        ratios['peg'] = None

    # ── RENTABILITÉ ───────────────────────────────────────────
    ratios['gross_margin'] = fmt(safe_div(gross_profit, revenue) * 100) if revenue else None
    ratios['operating_margin'] = fmt(safe_div(operating_income, revenue) * 100) if revenue else None
    ratios['net_margin'] = fmt(safe_div(net_income, revenue) * 100) if revenue else None
    ratios['ebitda_margin'] = fmt(safe_div(ebitda, revenue) * 100) if revenue else None
    ratios['fcf_margin'] = fmt(safe_div(free_cf, revenue) * 100) if revenue else None
    ratios['roe'] = fmt(safe_div(net_income, total_equity) * 100) if total_equity else None
    ratios['roa'] = fmt(safe_div(net_income, total_assets) * 100) if total_assets else None
    capital_employed = total_assets - current_liabilities
    ratios['roce'] = fmt(safe_div(operating_income, capital_employed) * 100) if capital_employed else None
    invested_capital = total_equity + total_debt - cash
    nopat = operating_income * 0.75
    ratios['roic'] = fmt(safe_div(nopat, invested_capital) * 100) if invested_capital else None

    # ── SÉCURITÉ ──────────────────────────────────────────────
    ratios['current_ratio'] = fmt(safe_div(current_assets, current_liabilities))
    ratios['quick_ratio'] = fmt(safe_div(current_assets - inventory, current_liabilities))
    ratios['debt_to_equity'] = fmt(safe_div(total_debt, total_equity))
    ratios['debt_to_assets'] = fmt(safe_div(total_debt, total_assets))
    ratios['interest_coverage'] = fmt(safe_div(operating_income, interest_expense)) if interest_expense else None
    ratios['net_debt'] = fmt((total_debt - cash) / 1e9)
    ratios['net_debt_ebitda'] = fmt(safe_div(total_debt - cash, ebitda)) if ebitda else None

    # ── CROISSANCE CAGR ───────────────────────────────────────
    n = len(income_statements)
    if n >= 2:
        # CA
        rev_start = income_statements[-1].get('revenue', 0)
        rev_end = income_statements[0].get('revenue', 0)
        ratios['revenue_cagr'] = cagr(rev_start, rev_end, n - 1)

        # Bénéfice net
        ni_start = income_statements[-1].get('netIncome', 0)
        ni_end = income_statements[0].get('netIncome', 0)
        ratios['net_income_cagr'] = cagr(abs(ni_start), abs(ni_end), n - 1) if ni_start and ni_start > 0 else None

        # BPA
        eps_start = income_statements[-1].get('epsdiluted') or income_statements[-1].get('eps', 0)
        eps_end = income_statements[0].get('epsdiluted') or income_statements[0].get('eps', 0)
        ratios['eps_cagr'] = cagr(abs(eps_start), abs(eps_end), n - 1) if eps_start and eps_start > 0 else None

        # Croissance YoY (TTM vs dernière année)
        ratios['revenue_growth_yoy'] = fmt(safe_div(revenue - rev_end, abs(rev_end)) * 100) if rev_end and revenue else None
        ratios['net_income_growth_yoy'] = fmt(safe_div(net_income - ni_end, abs(ni_end)) * 100) if ni_end and net_income else None

    else:
        ratios['revenue_cagr'] = None
        ratios['net_income_cagr'] = None
        ratios['eps_cagr'] = None
        ratios['revenue_growth_yoy'] = None
        ratios['net_income_growth_yoy'] = None

    # FCF CAGR
    if n >= 2 and cash_flows:
        fcf_start = cash_flows[-1].get('freeCashFlow', 0)
        fcf_end = cash_flows[0].get('freeCashFlow', 0)
        ratios['fcf_cagr'] = cagr(abs(fcf_start), abs(fcf_end), n - 1) if fcf_start and fcf_start > 0 else None
    else:
        ratios['fcf_cagr'] = None

    # ── QUALITÉ ───────────────────────────────────────────────
    # Consistance bénéfices
    profitable_years = sum(
        1 for s in income_statements if (s.get('netIncome') or 0) > 0
    )
    ratios['profitable_years'] = profitable_years
    ratios['total_years'] = len(income_statements)

    # Consistance FCF
    positive_fcf_years = sum(
        1 for s in cash_flows if (s.get('freeCashFlow') or 0) > 0
    )
    ratios['positive_fcf_years'] = positive_fcf_years

    # Rachat d'actions (diminution du nombre d'actions)
    if n >= 2:
        shares_start = income_statements[-1].get('weightedAverageShsOut', 0)
        shares_end = income_statements[0].get('weightedAverageShsOut', 0)
        if shares_start and shares_end:
            ratios['shares_buyback'] = shares_end < shares_start
            ratios['shares_change_pct'] = fmt(safe_div(shares_end - shares_start, shares_start) * 100)
        else:
            ratios['shares_buyback'] = None
            ratios['shares_change_pct'] = None
    else:
        ratios['shares_buyback'] = None
        ratios['shares_change_pct'] = None

    # Dividendes
    dps = abs(dividends / shares) if dividends and shares else 0
    ratios['dividend_yield'] = fmt(safe_div(dps, price) * 100) if dps and price else None
    ratios['payout_ratio'] = fmt(safe_div(abs(dividends), net_income) * 100) if dividends and net_income else None

    # Croissance dividende
    if len(cash_flows) >= 2:
        div_start = abs(cash_flows[-1].get('dividendsPaid', 0) or 0)
        div_end = abs(cash_flows[0].get('dividendsPaid', 0) or 0)
        ratios['dividend_cagr'] = cagr(div_start, div_end, len(cash_flows) - 1) if div_start > 0 else None
    else:
        ratios['dividend_cagr'] = None

    # ── MARGES HISTORIQUES (consistance) ──────────────────────
    if income_statements:
        net_margins_hist = [
            safe_div(s.get('netIncome', 0), s.get('revenue', 1))
            for s in income_statements
            if s.get('revenue')
        ]
        net_margins_hist = [m for m in net_margins_hist if m is not None]
        if net_margins_hist:
            ratios['avg_net_margin'] = fmt(sum(net_margins_hist) / len(net_margins_hist) * 100)
            ratios['margin_consistency'] = all(m > 0 for m in net_margins_hist)
        else:
            ratios['avg_net_margin'] = None
            ratios['margin_consistency'] = None

    return ratios