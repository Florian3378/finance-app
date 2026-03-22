def safe_div(a, b):
    try:
        return float(a) / float(b) if b and float(b) != 0 else None
    except:
        return None


def apply_margin_of_safety(price):
    """Retourne prix brut, avec MS 25% et MS 50%"""
    if price is None or price <= 0:
        return None, None, None
    return round(price, 2), round(price * 0.75, 2), round(price * 0.50, 2)


def dcf_valuation(fcf, growth_rate_1, growth_rate_2, terminal_growth, wacc, shares):
    """
    DCF classique sur 10 ans.
    Phase 1 : années 1-5 avec growth_rate_1
    Phase 2 : années 6-10 avec growth_rate_2
    Valeur terminale : Gordon Growth Model
    """
    if not fcf or not shares or fcf <= 0:
        return None, None

    try:
        g1 = growth_rate_1 / 100
        g2 = growth_rate_2 / 100
        gt = terminal_growth / 100
        w = wacc / 100

        projected_fcf = []
        cf = fcf

        # Phase 1 : 5 ans
        for i in range(1, 6):
            cf = cf * (1 + g1)
            pv = cf / ((1 + w) ** i)
            projected_fcf.append(pv)

        # Phase 2 : 5 ans
        for i in range(6, 11):
            cf = cf * (1 + g2)
            pv = cf / ((1 + w) ** i)
            projected_fcf.append(pv)

        # Valeur terminale (Gordon Growth)
        terminal_value = (cf * (1 + gt)) / (w - gt)
        pv_terminal = terminal_value / ((1 + w) ** 10)

        intrinsic_value = (sum(projected_fcf) + pv_terminal) / shares
        return round(intrinsic_value, 2), {
            'projected_fcf': [round(p, 0) for p in projected_fcf],
            'terminal_value': round(pv_terminal, 0),
            'total_equity_value': round(sum(projected_fcf) + pv_terminal, 0),
        }
    except Exception as e:
        return None, None


def owner_earnings_valuation(net_income, depreciation, capex, growth_rate, treasury_rate, shares):
    """
    Méthode Buffett — Owner Earnings DCF
    Taux d'actualisation = taux obligations Trésor 30 ans
    """
    if not net_income or not shares:
        return None

    try:
        # Owner Earnings = Net Income + D&A - Capex (maintenance)
        # On estime le capex maintenance à 70% du capex total
        maintenance_capex = abs(capex or 0) * 0.70
        owner_earnings = net_income + (depreciation or 0) - maintenance_capex

        if owner_earnings <= 0:
            return None

        g = growth_rate / 100
        r = treasury_rate / 100
        gt = 0.03  # Croissance perpétuelle fixe à 3%

        # Projection 10 ans
        total_pv = 0
        oe = owner_earnings
        for i in range(1, 11):
            oe = oe * (1 + g)
            total_pv += oe / ((1 + r) ** i)

        # Valeur terminale
        terminal = (oe * (1 + gt)) / (r - gt)
        pv_terminal = terminal / ((1 + r) ** 10)

        intrinsic = (total_pv + pv_terminal) / shares
        return round(intrinsic, 2)
    except:
        return None


def graham_number(eps, book_value_per_share):
    """
    Graham Number = √(22.5 × EPS × BVPS)
    Valeur conservative pour value stocks
    """
    try:
        if eps and eps > 0 and book_value_per_share and book_value_per_share > 0:
            return round((22.5 * eps * book_value_per_share) ** 0.5, 2)
        return None
    except:
        return None


def peter_lynch_value(eps, growth_rate):
    """
    Peter Lynch Fair Value = EPS × (taux de croissance)
    Une action est fairly valued quand PEG = 1
    """
    try:
        if eps and eps > 0 and growth_rate and growth_rate > 0:
            return round(eps * growth_rate, 2)
        return None
    except:
        return None


def multiples_valuation(eps, sector_per):
    """
    Valorisation par multiples : EPS × PER sectoriel moyen
    """
    try:
        if eps and eps > 0 and sector_per and sector_per > 0:
            return round(eps * sector_per, 2)
        return None
    except:
        return None


def ddm_valuation(dps, growth_rate, wacc):
    """
    Dividend Discount Model (Gordon Growth)
    P = D1 / (r - g)
    """
    try:
        if not dps or dps <= 0:
            return None
        g = growth_rate / 100
        r = wacc / 100
        if r <= g:
            return None
        d1 = dps * (1 + g)
        return round(d1 / (r - g), 2)
    except:
        return None


def dcf_reverse(current_price, fcf, wacc, shares):
    """
    DCF inversé : quel taux de croissance le marché anticipe-t-il ?
    Résout numériquement pour trouver g tel que DCF = prix actuel
    """
    if not fcf or not shares or fcf <= 0 or not current_price:
        return None

    try:
        w = wacc / 100
        target = current_price * shares

        # Recherche par dichotomie
        low, high = -0.20, 0.50
        for _ in range(100):
            mid = (low + high) / 2
            g1 = mid
            g2 = mid * 0.6
            gt = 0.03

            cf = fcf
            total = 0
            for i in range(1, 6):
                cf *= (1 + g1)
                total += cf / ((1 + w) ** i)
            for i in range(6, 11):
                cf *= (1 + g2)
                total += cf / ((1 + w) ** i)

            terminal = (cf * (1 + gt)) / (w - gt) if w > gt else 0
            total += terminal / ((1 + w) ** 10)

            if abs(total - target) < target * 0.001:
                break
            if total < target:
                low = mid
            else:
                high = mid

        return round(mid * 100, 1)
    except:
        return None


# PER sectoriels moyens approximatifs
SECTOR_PER = {
    'Technology': 28,
    'Healthcare': 22,
    'Financial Services': 14,
    'Consumer Cyclical': 20,
    'Consumer Defensive': 22,
    'Energy': 12,
    'Industrials': 20,
    'Basic Materials': 16,
    'Real Estate': 35,
    'Utilities': 18,
    'Communication Services': 20,
    'default': 20,
}


def calculate_all_valuations(profile, quote, ratios, income_statements,
                              balance_sheets, cash_flows,
                              income_ttm, balance_ttm, cashflow_ttm,
                              params):
    """
    Calcule toutes les valorisations avec les paramètres utilisateur.
    params = {
        'growth_rate_1': float,   # % croissance phase 1
        'growth_rate_2': float,   # % croissance phase 2
        'terminal_growth': float, # % croissance perpétuelle
        'wacc': float,            # % taux actualisation
        'treasury_rate': float,   # % taux Trésor 30 ans
    }
    """
    results = {}

    # Données de base
    price = quote.get('price', 0) or 0
    inc = income_ttm if income_ttm and income_ttm.get('revenue') else (income_statements[0] if income_statements else {})
    bal = balance_ttm if balance_ttm and balance_ttm.get('totalAssets') else (balance_sheets[0] if balance_sheets else {})
    cf = cashflow_ttm if cashflow_ttm and cashflow_ttm.get('operatingCashFlow') else (cash_flows[0] if cash_flows else {})

    shares = inc.get('weightedAverageShsOut', 0) or 0
    net_income = inc.get('netIncome', 0) or 0
    eps = (net_income / shares) if shares else 0
    fcf = cf.get('freeCashFlow', 0) or 0
    depreciation = cf.get('depreciationAndAmortization', 0) or 0
    capex = cf.get('capitalExpenditure', 0) or 0
    total_equity = bal.get('totalStockholdersEquity', 0) or 0
    book_value_per_share = safe_div(total_equity, shares)
    dividends_paid = abs(cf.get('dividendsPaid', 0) or 0)
    dps = safe_div(dividends_paid, shares)
    sector = profile.get('sector', 'default')
    sector_per = SECTOR_PER.get(sector, SECTOR_PER['default'])

    g1 = params['growth_rate_1']
    g2 = params['growth_rate_2']
    gt = params['terminal_growth']
    wacc = params['wacc']
    treasury = params['treasury_rate']

    # ── DCF CLASSIQUE ─────────────────────────────────────────
    dcf_price, dcf_detail = dcf_valuation(fcf, g1, g2, gt, wacc, shares)
    iv, ms25, ms50 = apply_margin_of_safety(dcf_price)
    results['dcf'] = {
        'name': 'DCF Classique',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': dcf_detail,
        'reliability': 'Haute',
        'reliability_score': 4,
        'note': f"FCF projeté sur 10 ans, WACC {wacc}%",
        'applicable': fcf > 0,
    }

    # ── OWNER EARNINGS (BUFFETT) ──────────────────────────────
    oe_price = owner_earnings_valuation(net_income, depreciation, capex, g1, treasury, shares)
    iv, ms25, ms50 = apply_margin_of_safety(oe_price)
    results['buffett'] = {
        'name': 'Owner Earnings (Buffett)',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': None,
        'reliability': 'Haute',
        'reliability_score': 4,
        'note': f"Owner Earnings actualisés au taux Trésor {treasury}%",
        'applicable': net_income > 0,
    }

    # ── GRAHAM NUMBER ─────────────────────────────────────────
    graham = graham_number(eps, book_value_per_share)
    iv, ms25, ms50 = apply_margin_of_safety(graham)
    results['graham'] = {
        'name': 'Graham Number',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': None,
        'reliability': 'Moyenne',
        'reliability_score': 2,
        'note': f"√(22.5 × BPA × VCP) — conservateur",
        'applicable': eps > 0 and book_value_per_share and book_value_per_share > 0,
    }

    # ── PETER LYNCH ───────────────────────────────────────────
    lynch = peter_lynch_value(eps, g1)
    iv, ms25, ms50 = apply_margin_of_safety(lynch)
    results['lynch'] = {
        'name': 'Peter Lynch',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': None,
        'reliability': 'Moyenne',
        'reliability_score': 2,
        'note': f"BPA × taux de croissance ({g1}%)",
        'applicable': eps > 0,
    }

    # ── MULTIPLES COMPARABLES ─────────────────────────────────
    multiples = multiples_valuation(eps, sector_per)
    iv, ms25, ms50 = apply_margin_of_safety(multiples)
    results['multiples'] = {
        'name': f'Multiples ({sector})',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': None,
        'reliability': 'Moyenne',
        'reliability_score': 3,
        'note': f"BPA × PER sectoriel moyen ({sector_per}x)",
        'applicable': eps > 0,
    }

    # ── DDM ───────────────────────────────────────────────────
    ddm = ddm_valuation(dps, g1, wacc) if dps else None
    iv, ms25, ms50 = apply_margin_of_safety(ddm)
    results['ddm'] = {
        'name': 'DDM (Dividendes)',
        'intrinsic': iv,
        'ms25': ms25,
        'ms50': ms50,
        'detail': None,
        'reliability': 'Haute' if dps else 'N/A',
        'reliability_score': 3 if dps else 0,
        'note': "Gordon Growth Model" if dps else "Pas de dividende versé",
        'applicable': bool(dps and dps > 0),
    }

    # ── DCF INVERSÉ ───────────────────────────────────────────
    implied_growth = dcf_reverse(price, fcf, wacc, shares)
    results['reverse_dcf'] = {
        'name': 'DCF Inversé',
        'implied_growth': implied_growth,
        'note': f"Le marché anticipe {implied_growth}% de croissance annuelle" if implied_growth else "Non calculable",
        'applicable': fcf > 0,
    }

    # ── FOURCHETTE CONSENSUELLE ───────────────────────────────
    valid_prices = [
        r['intrinsic'] for k, r in results.items()
        if k != 'reverse_dcf' and r.get('intrinsic') and r.get('applicable')
    ]

    if valid_prices:
        results['consensus'] = {
            'low': min(valid_prices),
            'median': sorted(valid_prices)[len(valid_prices) // 2],
            'high': max(valid_prices),
            'current': price,
            'upside_median': round((sorted(valid_prices)[len(valid_prices) // 2] / price - 1) * 100, 1) if price else None,
        }
    else:
        results['consensus'] = None

    return results