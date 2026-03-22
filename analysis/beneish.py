def calculate_beneish(income_statements, balance_sheets, cash_flows):
    """
    Calcule le Beneish M-Score.
    Nécessite au minimum 2 années de données.
    """
    if len(income_statements) < 2 or len(balance_sheets) < 2:
        return None

    def safe_div(a, b):
        try:
            return float(a) / float(b) if b and float(b) != 0 else None
        except:
            return None

    # Données courante et précédente
    inc_t = income_statements[0]
    inc_t1 = income_statements[1]
    bal_t = balance_sheets[0]
    bal_t1 = balance_sheets[1]
    cf_t = cash_flows[0] if cash_flows else {}

    # Raccourcis
    def g(d, k): return float(d.get(k, 0) or 0)

    # Variables année courante
    revenue_t = g(inc_t, 'revenue')
    revenue_t1 = g(inc_t1, 'revenue')
    gross_profit_t = g(inc_t, 'grossProfit')
    gross_profit_t1 = g(inc_t1, 'grossProfit')
    receivables_t = g(bal_t, 'netReceivables')
    receivables_t1 = g(bal_t1, 'netReceivables')
    total_assets_t = g(bal_t, 'totalAssets')
    total_assets_t1 = g(bal_t1, 'totalAssets')
    current_assets_t = g(bal_t, 'totalCurrentAssets')
    current_assets_t1 = g(bal_t1, 'totalCurrentAssets')
    ppe_t = g(bal_t, 'propertyPlantEquipmentNet')
    ppe_t1 = g(bal_t1, 'propertyPlantEquipmentNet')
    depreciation_t = g(cf_t, 'depreciationAndAmortization')
    sga_t = g(inc_t, 'sellingGeneralAndAdministrativeExpenses')
    sga_t1 = g(inc_t1, 'sellingGeneralAndAdministrativeExpenses')
    total_debt_t = g(bal_t, 'totalDebt')
    total_debt_t1 = g(bal_t1, 'totalDebt')
    total_equity_t = g(bal_t, 'totalStockholdersEquity')
    total_equity_t1 = g(bal_t1, 'totalStockholdersEquity')
    net_income_t = g(inc_t, 'netIncome')
    ocf_t = g(cf_t, 'operatingCashFlow')
    cogs_t = revenue_t - gross_profit_t
    cogs_t1 = revenue_t1 - gross_profit_t1

    details = {}

    # ── DSRI — Days Sales Receivable Index ────────────────────
    # (Receivables_t / Revenue_t) / (Receivables_t1 / Revenue_t1)
    # Hausse = gonflement des créances → revenus fictifs
    dsr_t = safe_div(receivables_t, revenue_t)
    dsr_t1 = safe_div(receivables_t1, revenue_t1)
    dsri = safe_div(dsr_t, dsr_t1)
    details['DSRI'] = {
        'value': round(dsri, 3) if dsri else None,
        'label': 'Indice créances clients',
        'interpretation': 'Hausse des créances vs revenus → possible gonflement des ventes' if dsri and dsri > 1.1 else 'Normal',
        'warning': dsri and dsri > 1.1
    }

    # ── GMI — Gross Margin Index ──────────────────────────────
    # (GrossMargin_t1) / (GrossMargin_t)
    # Hausse > 1 = dégradation des marges → pression à manipuler
    gm_t = safe_div(gross_profit_t, revenue_t)
    gm_t1 = safe_div(gross_profit_t1, revenue_t1)
    gmi = safe_div(gm_t1, gm_t)
    details['GMI'] = {
        'value': round(gmi, 3) if gmi else None,
        'label': 'Indice marge brute',
        'interpretation': 'Dégradation des marges → pression à manipuler' if gmi and gmi > 1.2 else 'Normal',
        'warning': gmi and gmi > 1.2
    }

    # ── AQI — Asset Quality Index ─────────────────────────────
    # (1 - (CurrentAssets + PPE) / TotalAssets)_t / même chose _t1
    # Hausse = augmentation des actifs non courants douteux
    aq_t = 1 - safe_div(current_assets_t + ppe_t, total_assets_t) if total_assets_t else None
    aq_t1 = 1 - safe_div(current_assets_t1 + ppe_t1, total_assets_t1) if total_assets_t1 else None
    aqi = safe_div(aq_t, aq_t1)
    details['AQI'] = {
        'value': round(aqi, 3) if aqi else None,
        'label': 'Indice qualité des actifs',
        'interpretation': 'Hausse des actifs intangibles suspects' if aqi and aqi > 1.25 else 'Normal',
        'warning': aqi and aqi > 1.25
    }

    # ── SGI — Sales Growth Index ──────────────────────────────
    # Revenue_t / Revenue_t1
    # Forte croissance = pression à maintenir les résultats
    sgi = safe_div(revenue_t, revenue_t1)
    details['SGI'] = {
        'value': round(sgi, 3) if sgi else None,
        'label': 'Indice croissance des ventes',
        'interpretation': 'Forte croissance → pression sur les résultats' if sgi and sgi > 1.6 else 'Normal',
        'warning': sgi and sgi > 1.6
    }

    # ── DEPI — Depreciation Index ─────────────────────────────
    # (Depreciation_t1 / (PPE_t1 + Depreciation_t1)) /
    # (Depreciation_t  / (PPE_t  + Depreciation_t ))
    # Hausse = ralentissement des amortissements → actifs surévalués
    if depreciation_t and ppe_t:
        cf_t1 = cash_flows[1] if len(cash_flows) > 1 else {}
        depreciation_t1 = g(cf_t1, 'depreciationAndAmortization')
        dep_rate_t = safe_div(depreciation_t, ppe_t + depreciation_t)
        dep_rate_t1 = safe_div(depreciation_t1, ppe_t1 + depreciation_t1) if depreciation_t1 else None
        depi = safe_div(dep_rate_t1, dep_rate_t)
    else:
        depi = None
    details['DEPI'] = {
        'value': round(depi, 3) if depi else None,
        'label': 'Indice dépréciation',
        'interpretation': 'Ralentissement des amortissements → actifs surévalués' if depi and depi > 1.1 else 'Normal',
        'warning': depi and depi > 1.1
    }

    # ── SGAI — SGA Expense Index ──────────────────────────────
    # (SGA_t / Revenue_t) / (SGA_t1 / Revenue_t1)
    # Hausse = inefficacité commerciale croissante
    sga_ratio_t = safe_div(sga_t, revenue_t)
    sga_ratio_t1 = safe_div(sga_t1, revenue_t1)
    sgai = safe_div(sga_ratio_t, sga_ratio_t1)
    details['SGAI'] = {
        'value': round(sgai, 3) if sgai else None,
        'label': 'Indice frais généraux',
        'interpretation': 'Hausse des frais généraux vs ventes' if sgai and sgai > 1.1 else 'Normal',
        'warning': sgai and sgai > 1.1
    }

    # ── TATA — Total Accruals to Total Assets ─────────────────
    # (NetIncome - OperatingCashFlow) / TotalAssets
    # Valeur élevée = bénéfices non soutenus par le cash
    tata = safe_div(net_income_t - ocf_t, total_assets_t)
    details['TATA'] = {
        'value': round(tata, 3) if tata else None,
        'label': 'Accruals / Actifs totaux',
        'interpretation': 'Bénéfices non soutenus par le cash' if tata and tata > 0.031 else 'Normal',
        'warning': tata and tata > 0.031
    }

    # ── LVGI — Leverage Index ─────────────────────────────────
    # (TotalDebt_t / TotalAssets_t) / (TotalDebt_t1 / TotalAssets_t1)
    # Hausse = endettement croissant → pression à manipuler
    lev_t = safe_div(total_debt_t, total_assets_t)
    lev_t1 = safe_div(total_debt_t1, total_assets_t1)
    lvgi = safe_div(lev_t, lev_t1)
    details['LVGI'] = {
        'value': round(lvgi, 3) if lvgi else None,
        'label': 'Indice levier financier',
        'interpretation': 'Endettement en hausse → pression sur les résultats' if lvgi and lvgi > 1.1 else 'Normal',
        'warning': lvgi and lvgi > 1.1
    }

    # ── CALCUL DU M-SCORE ─────────────────────────────────────
    components = {
        'DSRI': (dsri or 0, 0.920),
        'GMI': (gmi or 0, 0.528),
        'AQI': (aqi or 0, 0.404),
        'SGI': (sgi or 0, 0.892),
        'DEPI': (depi or 0, 0.115),
        'SGAI': (sgai or 0, -0.172),
        'TATA': (tata or 0, 4.679),
        'LVGI': (lvgi or 0, -0.327),
    }

    m_score = -4.84 + sum(val * weight for val, weight in components.values())
    m_score = round(m_score, 2)

    # Interprétation
    if m_score > -1.78:
        label = 'Risque de manipulation élevé'
        color = 'danger'
        emoji = '🔴'
    elif m_score > -2.22:
        label = 'Zone grise'
        color = 'warning'
        emoji = '🟡'
    else:
        label = 'Probablement sain'
        color = 'success'
        emoji = '🟢'

    # Nombre d'alertes
    warnings = sum(1 for d in details.values() if d.get('warning'))

    return {
        'm_score': m_score,
        'label': label,
        'color': color,
        'emoji': emoji,
        'warnings': warnings,
        'details': details,
    }