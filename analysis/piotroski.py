def calculate_piotroski(income_statements, balance_sheets, cash_flows, income_ttm=None, balance_ttm=None, cashflow_ttm=None):
    """
    Calcule le Piotroski F-Score (0-9).
    Utilise TTM pour l'année courante et la dernière année annuelle comme comparatif.
    """
    
    details = {}
    
    # Données courantes (TTM si dispo, sinon dernière année)
    inc_curr = income_ttm if income_ttm and income_ttm.get('revenue') else (income_statements[0] if income_statements else {})
    bal_curr = balance_ttm if balance_ttm and balance_ttm.get('totalAssets') else (balance_sheets[0] if balance_sheets else {})
    cf_curr = cashflow_ttm if cashflow_ttm and cashflow_ttm.get('operatingCashFlow') else (cash_flows[0] if cash_flows else {})
    
    # Données année précédente
    inc_prev = income_statements[0] if income_ttm and income_statements else (income_statements[1] if len(income_statements) > 1 else {})
    bal_prev = balance_sheets[0] if balance_ttm and balance_sheets else (balance_sheets[1] if len(balance_sheets) > 1 else {})

    def safe_div(a, b):
        try:
            return float(a) / float(b) if b and float(b) != 0 else None
        except:
            return None

    # ── RENTABILITÉ ───────────────────────────────────────────

    # F1 — ROA > 0
    net_income_curr = inc_curr.get('netIncome', 0) or 0
    total_assets_curr = bal_curr.get('totalAssets', 0) or 0
    roa_curr = safe_div(net_income_curr, total_assets_curr)
    f1 = 1 if roa_curr and roa_curr > 0 else 0
    details['f1'] = {
        'score': f1,
        'label': 'ROA positif',
        'detail': f"ROA = {round(roa_curr * 100, 2)}%" if roa_curr else "ROA non calculable",
        'pass': f1 == 1
    }

    # F2 — Operating Cash Flow > 0
    ocf_curr = cf_curr.get('operatingCashFlow', 0) or 0
    f2 = 1 if ocf_curr > 0 else 0
    details['f2'] = {
        'score': f2,
        'label': 'Cash flow opérationnel positif',
        'detail': f"OCF = {round(ocf_curr / 1e9, 2)} Mrd$",
        'pass': f2 == 1
    }

    # F3 — ROA en hausse
    net_income_prev = inc_prev.get('netIncome', 0) or 0
    total_assets_prev = bal_prev.get('totalAssets', 0) or 0
    roa_prev = safe_div(net_income_prev, total_assets_prev)
    f3 = 1 if (roa_curr and roa_prev and roa_curr > roa_prev) else 0
    details['f3'] = {
        'score': f3,
        'label': 'ROA en amélioration',
        'detail': f"ROA actuel {round(roa_curr*100,2) if roa_curr else '—'}% vs {round(roa_prev*100,2) if roa_prev else '—'}% l'an passé",
        'pass': f3 == 1
    }

    # F4 — Accruals : OCF/Assets > ROA (qualité des bénéfices)
    ocf_ratio = safe_div(ocf_curr, total_assets_curr)
    f4 = 1 if (ocf_ratio and roa_curr and ocf_ratio > roa_curr) else 0
    details['f4'] = {
        'score': f4,
        'label': 'Qualité des bénéfices (OCF > ROA)',
        'detail': f"OCF/Actifs = {round(ocf_ratio*100,2) if ocf_ratio else '—'}% vs ROA = {round(roa_curr*100,2) if roa_curr else '—'}%",
        'pass': f4 == 1
    }

    # ── LEVIER & LIQUIDITÉ ────────────────────────────────────

    # F5 — Ratio dette LT en baisse
    lt_debt_curr = bal_curr.get('longTermDebt', 0) or 0
    lt_debt_prev = bal_prev.get('longTermDebt', 0) or 0
    assets_prev = bal_prev.get('totalAssets', 1) or 1
    leverage_curr = safe_div(lt_debt_curr, total_assets_curr)
    leverage_prev = safe_div(lt_debt_prev, assets_prev)
    f5 = 1 if (leverage_curr is not None and leverage_prev is not None and leverage_curr <= leverage_prev) else 0
    details['f5'] = {
        'score': f5,
        'label': 'Levier financier en baisse',
        'detail': f"Dette LT/Actifs : {round(leverage_curr*100,2) if leverage_curr else '—'}% vs {round(leverage_prev*100,2) if leverage_prev else '—'}%",
        'pass': f5 == 1
    }

    # F6 — Ratio courant en hausse
    curr_assets_curr = bal_curr.get('totalCurrentAssets', 0) or 0
    curr_liab_curr = bal_curr.get('totalCurrentLiabilities', 0) or 0
    curr_assets_prev = bal_prev.get('totalCurrentAssets', 0) or 0
    curr_liab_prev = bal_prev.get('totalCurrentLiabilities', 0) or 0
    current_ratio_curr = safe_div(curr_assets_curr, curr_liab_curr)
    current_ratio_prev = safe_div(curr_assets_prev, curr_liab_prev)
    f6 = 1 if (current_ratio_curr and current_ratio_prev and current_ratio_curr >= current_ratio_prev) else 0
    details['f6'] = {
        'score': f6,
        'label': 'Liquidité en amélioration',
        'detail': f"Ratio courant : {round(current_ratio_curr,2) if current_ratio_curr else '—'} vs {round(current_ratio_prev,2) if current_ratio_prev else '—'}",
        'pass': f6 == 1
    }

    # F7 — Pas de dilution (nombre d'actions stable ou en baisse)
    shares_curr = inc_curr.get('weightedAverageShsOut', 0) or 0
    shares_prev = inc_prev.get('weightedAverageShsOut', 0) or 0
    f7 = 1 if (shares_curr and shares_prev and shares_curr <= shares_prev) else 0
    details['f7'] = {
        'score': f7,
        'label': 'Pas de dilution actionnariale',
        'detail': f"Actions : {round(shares_curr/1e9,2) if shares_curr else '—'} Mrd vs {round(shares_prev/1e9,2) if shares_prev else '—'} Mrd",
        'pass': f7 == 1
    }

    # ── EFFICACITÉ OPÉRATIONNELLE ──────────────────────────────

    # F8 — Marge brute en hausse
    revenue_curr = inc_curr.get('revenue', 0) or 0
    gross_curr = inc_curr.get('grossProfit', 0) or 0
    revenue_prev = inc_prev.get('revenue', 0) or 0
    gross_prev = inc_prev.get('grossProfit', 0) or 0
    gm_curr = safe_div(gross_curr, revenue_curr)
    gm_prev = safe_div(gross_prev, revenue_prev)
    f8 = 1 if (gm_curr and gm_prev and gm_curr >= gm_prev) else 0
    details['f8'] = {
        'score': f8,
        'label': 'Marge brute en amélioration',
        'detail': f"Marge brute : {round(gm_curr*100,2) if gm_curr else '—'}% vs {round(gm_prev*100,2) if gm_prev else '—'}%",
        'pass': f8 == 1
    }

    # F9 — Rotation des actifs en hausse (Revenue/Assets)
    asset_turn_curr = safe_div(revenue_curr, total_assets_curr)
    asset_turn_prev = safe_div(revenue_prev, assets_prev)
    f9 = 1 if (asset_turn_curr and asset_turn_prev and asset_turn_curr >= asset_turn_prev) else 0
    details['f9'] = {
        'score': f9,
        'label': 'Rotation des actifs en hausse',
        'detail': f"Rotation : {round(asset_turn_curr,2) if asset_turn_curr else '—'} vs {round(asset_turn_prev,2) if asset_turn_prev else '—'}",
        'pass': f9 == 1
    }

    # ── SCORE TOTAL ───────────────────────────────────────────
    total = f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9

    if total >= 7:
        label = 'Entreprise solide'
        color = 'success'
        emoji = '🟢'
    elif total >= 4:
        label = 'Qualité moyenne'
        color = 'warning'
        emoji = '🟡'
    else:
        label = 'Entreprise fragile'
        color = 'danger'
        emoji = '🔴'

    return {
        'total': total,
        'max': 9,
        'label': label,
        'color': color,
        'emoji': emoji,
        'details': details,
        'groups': {
            'Rentabilité': ['f1', 'f2', 'f3', 'f4'],
            'Levier & Liquidité': ['f5', 'f6', 'f7'],
            'Efficacité': ['f8', 'f9'],
        }
    }