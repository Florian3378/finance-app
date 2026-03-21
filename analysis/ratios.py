def safe_div(a, b):
    """Division sécurisée — retourne None si b est 0 ou None"""
    try:
        if b and b != 0:
            return a / b
        return None
    except:
        return None

def pct(value):
    """Convertit un ratio en pourcentage"""
    if value is not None:
        return round(value * 100, 2)
    return None

def fmt(value, decimals=2):
    """Arrondit proprement"""
    if value is not None:
        return round(value, decimals)
    return None


def calculate_ratios(profile, quote, income_statements, balance_sheets, cash_flows):
    """
    Calcule tous les ratios depuis les états financiers.
    Utilise les données TTM (dernière année) pour les ratios courants.
    """
    ratios = {}

    # Données les plus récentes
    inc = income_statements[0] if income_statements else {}
    bal = balance_sheets[0] if balance_sheets else {}
    cf = cash_flows[0] if cash_flows else {}

    price = quote.get('price', 0)
    shares = inc.get('weightedAverageShsOut', 0)
    market_cap = profile.get('mktCap', 0) or (price * shares if price and shares else 0)

    # Compte de résultats
    revenue = inc.get('revenue', 0)
    gross_profit = inc.get('grossProfit', 0)
    ebitda = inc.get('ebitda', 0)
    operating_income = inc.get('operatingIncome', 0)
    net_income = inc.get('netIncome', 0)
    eps = inc.get('eps', 0)
    interest_expense = inc.get('interestExpense', 0)

    # Bilan
    total_assets = bal.get('totalAssets', 0)
    total_equity = bal.get('totalStockholdersEquity', 0)
    total_debt = bal.get('totalDebt', 0) or (
        (bal.get('longTermDebt', 0) or 0) + (bal.get('shortTermDebt', 0) or 0)
    )
    current_assets = bal.get('totalCurrentAssets', 0)
    current_liabilities = bal.get('totalCurrentLiabilities', 0)
    cash = bal.get('cashAndCashEquivalents', 0)
    inventory = bal.get('inventory', 0)
    total_liabilities = bal.get('totalLiabilities', 0)

    # Cash Flow
    operating_cf = cf.get('operatingCashFlow', 0)
    capex = cf.get('capitalExpenditure', 0)
    free_cf = cf.get('freeCashFlow', 0) or (
        (operating_cf or 0) + (capex or 0)
    )
    dividends = cf.get('dividendsPaid', 0)

    # ── VALORISATION ──────────────────────────────────────────
    ratios['per'] = fmt(safe_div(price, eps)) if eps and eps > 0 else None
    ratios['pb'] = fmt(safe_div(market_cap, total_equity)) if total_equity else None
    ratios['ps'] = fmt(safe_div(market_cap, revenue)) if revenue else None
    ratios['pcf'] = fmt(safe_div(market_cap, free_cf)) if free_cf and free_cf > 0 else None

    # EV = Market Cap + Dette - Cash
    ev = (market_cap or 0) + (total_debt or 0) - (cash or 0)
    ratios['ev'] = fmt(ev / 1e9) if ev else None
    ratios['ev_ebitda'] = fmt(safe_div(ev, ebitda)) if ebitda and ebitda > 0 else None
    ratios['ev_revenue'] = fmt(safe_div(ev, revenue)) if revenue else None

    # PEG — nécessite croissance EPS sur 2 ans
    if len(income_statements) >= 2:
        eps_current = income_statements[0].get('eps', 0)
        eps_prev = income_statements[1].get('eps', 0)
        if eps_prev and eps_prev > 0 and eps_current:
            eps_growth = ((eps_current - eps_prev) / abs(eps_prev)) * 100
            if eps_growth > 0 and ratios.get('per'):
                ratios['peg'] = fmt(ratios['per'] / eps_growth)
            else:
                ratios['peg'] = None
        else:
            ratios['peg'] = None
    else:
        ratios['peg'] = None

    # ── RENTABILITÉ ───────────────────────────────────────────
    ratios['gross_margin'] = pct(safe_div(gross_profit, revenue))
    ratios['operating_margin'] = pct(safe_div(operating_income, revenue))
    ratios['net_margin'] = pct(safe_div(net_income, revenue))
    ratios['ebitda_margin'] = pct(safe_div(ebitda, revenue))
    ratios['fcf_margin'] = pct(safe_div(free_cf, revenue))

    ratios['roe'] = pct(safe_div(net_income, total_equity))
    ratios['roa'] = pct(safe_div(net_income, total_assets))

    # ROCE = EBIT / Capital Employé
    capital_employed = (total_assets or 0) - (current_liabilities or 0)
    ratios['roce'] = pct(safe_div(operating_income, capital_employed)) if capital_employed else None

    # ROIC = Net Operating Profit / Invested Capital
    invested_capital = (total_equity or 0) + (total_debt or 0) - (cash or 0)
    nopat = (operating_income or 0) * 0.75  # Approximation après impôts 25%
    ratios['roic'] = pct(safe_div(nopat, invested_capital)) if invested_capital else None

    # ── LIQUIDITÉ & SOLVABILITÉ ───────────────────────────────
    ratios['current_ratio'] = fmt(safe_div(current_assets, current_liabilities))
    ratios['quick_ratio'] = fmt(
        safe_div((current_assets or 0) - (inventory or 0), current_liabilities)
    )
    ratios['debt_to_equity'] = fmt(safe_div(total_debt, total_equity))
    ratios['debt_to_assets'] = fmt(safe_div(total_debt, total_assets))
    ratios['interest_coverage'] = fmt(
        safe_div(operating_income, interest_expense)
    ) if interest_expense else None
    ratios['net_debt'] = fmt(((total_debt or 0) - (cash or 0)) / 1e9)

    # ── DIVIDENDES ────────────────────────────────────────────
    dps = abs(dividends / shares) if dividends and shares else 0
    ratios['dividend_yield'] = pct(safe_div(dps, price)) if dps and price else None
    ratios['payout_ratio'] = pct(safe_div(abs(dividends), net_income)) if dividends and net_income else None

    # ── CROISSANCE (sur la période disponible) ────────────────
    if len(income_statements) >= 2:
        rev_curr = income_statements[0].get('revenue', 0)
        rev_prev = income_statements[1].get('revenue', 0)
        ratios['revenue_growth'] = pct(safe_div(rev_curr - rev_prev, abs(rev_prev))) if rev_prev else None

        ni_curr = income_statements[0].get('netIncome', 0)
        ni_prev = income_statements[1].get('netIncome', 0)
        ratios['net_income_growth'] = pct(safe_div(ni_curr - ni_prev, abs(ni_prev))) if ni_prev else None
    else:
        ratios['revenue_growth'] = None
        ratios['net_income_growth'] = None

    return ratios