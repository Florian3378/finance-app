def calculate_altman(profile, quote, income_statements, balance_sheets,
                     income_ttm=None, balance_ttm=None):
    """
    Calcule le Altman Z-Score en deux versions :
    - Original (Z) : entreprises manufacturières
    - Z' (Z-prime) : entreprises non manufacturières / services

    Sélection automatique selon le secteur.
    """
    if not income_statements or not balance_sheets:
        return None

    def safe_div(a, b):
        try:
            return float(a) / float(b) if b and float(b) != 0 else None
        except:
            return None

    # Données courantes
    inc = income_ttm if income_ttm and income_ttm.get('revenue') else income_statements[0]
    bal = balance_ttm if balance_ttm and balance_ttm.get('totalAssets') else balance_sheets[0]

    # Variables du bilan
    total_assets = float(bal.get('totalAssets', 0) or 0)
    current_assets = float(bal.get('totalCurrentAssets', 0) or 0)
    current_liabilities = float(bal.get('totalCurrentLiabilities', 0) or 0)
    retained_earnings = float(bal.get('retainedEarnings', 0) or 0)
    total_liabilities = float(bal.get('totalLiabilities', 0) or 0)
    total_equity = float(bal.get('totalStockholdersEquity', 0) or 0)

    # Variables du compte de résultats
    revenue = float(inc.get('revenue', 0) or 0)
    ebit = float(inc.get('operatingIncome', 0) or 0)

    # Capitalisation boursière
    market_cap = float(profile.get('marketCap', 0) or 0)
    if not market_cap:
        price = float(quote.get('price', 0) or 0)
        shares = float(inc.get('weightedAverageShsOut', 0) or 0)
        market_cap = price * shares

    if total_assets == 0:
        return None

    # ── RATIOS COMMUNS ────────────────────────────────────────
    working_capital = current_assets - current_liabilities

    # X1 = Fonds de roulement / Total Actif
    x1 = safe_div(working_capital, total_assets)

    # X2 = Bénéfices non distribués / Total Actif
    x2 = safe_div(retained_earnings, total_assets)

    # X3 = EBIT / Total Actif
    x3 = safe_div(ebit, total_assets)

    # X4 original = Market Cap / Total Passif
    x4_original = safe_div(market_cap, total_liabilities)

    # X4 Z-prime = Fonds propres (book value) / Total Passif
    x4_prime = safe_div(total_equity, total_liabilities)

    # X5 = Chiffre d'affaires / Total Actif
    x5 = safe_div(revenue, total_assets)

    # Vérifie qu'on a les données minimales
    if any(v is None for v in [x1, x2, x3, x5]):
        return None

    # ── VERSION ORIGINALE (manufacturing) ─────────────────────
    z_original = None
    if x4_original is not None:
        z_original = (
            1.2 * x1 +
            1.4 * x2 +
            3.3 * x3 +
            0.6 * x4_original +
            1.0 * x5
        )
        z_original = round(z_original, 2)

    # ── VERSION Z-PRIME (non-manufacturing) ───────────────────
    z_prime = None
    if x4_prime is not None:
        z_prime = (
            6.56 * x1 +
            3.26 * x2 +
            6.72 * x3 +
            1.05 * x4_prime
        )
        z_prime = round(z_prime, 2)

    # ── SÉLECTION AUTOMATIQUE ─────────────────────────────────
    manufacturing_sectors = [
        'Industrials', 'Basic Materials', 'Energy',
        'Consumer Cyclical', 'Consumer Defensive'
    ]
    sector = profile.get('sector', '')
    is_manufacturing = sector in manufacturing_sectors

    if is_manufacturing and z_original is not None:
        active_score = z_original
        active_version = 'Original (Manufacturing)'
        safe_zone = 2.99
        distress_zone = 1.81
    else:
        active_score = z_prime
        active_version = "Z' (Non-Manufacturing)"
        safe_zone = 2.60
        distress_zone = 1.10

    if active_score is None:
        return None

    # Interprétation
    if active_score > safe_zone:
        label = 'Zone sûre'
        color = 'success'
        emoji = '🟢'
        risk = 'Faible'
    elif active_score > distress_zone:
        label = 'Zone grise'
        color = 'warning'
        emoji = '🟡'
        risk = 'Modéré'
    else:
        label = 'Zone de détresse'
        color = 'danger'
        emoji = '🔴'
        risk = 'Élevé'

    # Détail des composantes
    details = {
        'X1': {
            'label': 'Fonds de roulement / Actif total',
            'value': round(x1, 3) if x1 else None,
            'interpretation': 'Liquidité court terme' + (' ✅' if x1 and x1 > 0 else ' ⚠️')
        },
        'X2': {
            'label': 'Bénéfices non distribués / Actif total',
            'value': round(x2, 3) if x2 else None,
            'interpretation': 'Rentabilité cumulée' + (' ✅' if x2 and x2 > 0.1 else ' ⚠️')
        },
        'X3': {
            'label': 'EBIT / Actif total',
            'value': round(x3, 3) if x3 else None,
            'interpretation': 'Rentabilité opérationnelle' + (' ✅' if x3 and x3 > 0.05 else ' ⚠️')
        },
        'X4': {
            'label': 'Market Cap / Total Passif' if is_manufacturing else 'Fonds propres / Total Passif',
            'value': round(x4_original if is_manufacturing else x4_prime, 3) if (x4_original or x4_prime) else None,
            'interpretation': 'Solvabilité' + (' ✅' if (x4_original or x4_prime) and (x4_original or x4_prime) > 0.5 else ' ⚠️')
        },
        'X5': {
            'label': "Chiffre d'affaires / Actif total",
            'value': round(x5, 3) if x5 else None,
            'interpretation': 'Efficacité des actifs' + (' ✅' if x5 and x5 > 0.5 else ' ⚠️')
        },
    }

    # Retire X5 pour la version Z-prime (non utilisé)
    if not is_manufacturing:
        details.pop('X5', None)

    return {
        'score': active_score,
        'version': active_version,
        'label': label,
        'color': color,
        'emoji': emoji,
        'risk': risk,
        'safe_zone': safe_zone,
        'distress_zone': distress_zone,
        'z_original': z_original,
        'z_prime': z_prime,
        'sector': sector,
        'is_manufacturing': is_manufacturing,
        'details': details,
    }