def score_ratio(name, value):
    if value is None:
        return None, 'N/A', 'secondary'

    rules = {
        # Valorisation
        'per': [
            (0, 10, 55, 'Bas', 'warning'),
            (10, 20, 100, 'Attractif', 'success'),
            (20, 30, 75, 'Correct', 'primary'),
            (30, 40, 45, 'Élevé', 'warning'),
            (40, float('inf'), 15, 'Très élevé', 'danger'),
        ],
        'peg': [
            (float('-inf'), 0, 20, 'Négatif', 'danger'),
            (0, 1, 100, 'Attractif', 'success'),
            (1, 2, 70, 'Correct', 'primary'),
            (2, 3, 35, 'Élevé', 'warning'),
            (3, float('inf'), 10, 'Très élevé', 'danger'),
        ],
        'pb': [
            (float('-inf'), 0, 10, 'Négatif', 'danger'),
            (0, 1, 90, 'Très attractif', 'success'),
            (1, 3, 75, 'Attractif', 'success'),
            (3, 6, 50, 'Correct', 'warning'),
            (6, float('inf'), 20, 'Élevé', 'danger'),
        ],
        'ps': [
            (0, 1, 100, 'Très attractif', 'success'),
            (1, 3, 75, 'Attractif', 'primary'),
            (3, 6, 45, 'Correct', 'warning'),
            (6, float('inf'), 15, 'Élevé', 'danger'),
        ],
        'ev_ebitda': [
            (0, 8, 100, 'Attractif', 'success'),
            (8, 15, 70, 'Correct', 'primary'),
            (15, 25, 40, 'Élevé', 'warning'),
            (25, float('inf'), 10, 'Très élevé', 'danger'),
        ],
        'ev_revenue': [
            (0, 2, 100, 'Attractif', 'success'),
            (2, 5, 70, 'Correct', 'primary'),
            (5, 10, 40, 'Élevé', 'warning'),
            (10, float('inf'), 10, 'Très élevé', 'danger'),
        ],
        # Rentabilité
        'roe': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 10, 25, 'Faible', 'danger'),
            (10, 15, 50, 'Correct', 'warning'),
            (15, 20, 75, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'roa': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 35, 'Faible', 'danger'),
            (5, 10, 60, 'Correct', 'warning'),
            (10, 15, 85, 'Bon', 'primary'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
        'roic': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 8, 25, 'Faible', 'danger'),
            (8, 12, 55, 'Correct', 'warning'),
            (12, 20, 80, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'gross_margin': [
            (float('-inf'), 20, 15, 'Faible', 'danger'),
            (20, 40, 45, 'Correct', 'warning'),
            (40, 60, 80, 'Bon', 'primary'),
            (60, float('inf'), 100, 'Excellent', 'success'),
        ],
        'net_margin': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 25, 'Faible', 'danger'),
            (5, 10, 50, 'Correct', 'warning'),
            (10, 20, 80, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'fcf_margin': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 30, 'Faible', 'danger'),
            (5, 15, 60, 'Correct', 'warning'),
            (15, 25, 85, 'Bon', 'primary'),
            (25, float('inf'), 100, 'Excellent', 'success'),
        ],
        # Sécurité
        'current_ratio': [
            (float('-inf'), 1, 10, 'Dangereux', 'danger'),
            (1, 1.5, 45, 'Limite', 'warning'),
            (1.5, 3, 100, 'Bon', 'success'),
            (3, float('inf'), 65, 'Excédentaire', 'primary'),
        ],
        'quick_ratio': [
            (float('-inf'), 0.5, 5, 'Dangereux', 'danger'),
            (0.5, 1, 40, 'Limite', 'warning'),
            (1, 2, 90, 'Bon', 'success'),
            (2, float('inf'), 70, 'Excédentaire', 'primary'),
        ],
        'debt_to_equity': [
            (float('-inf'), 0, 100, 'Sans dette', 'success'),
            (0, 0.5, 90, 'Excellent', 'success'),
            (0.5, 1, 70, 'Bon', 'primary'),
            (1, 2, 40, 'Correct', 'warning'),
            (2, float('inf'), 10, 'Élevé', 'danger'),
        ],
        'interest_coverage': [
            (float('-inf'), 1.5, 5, 'Dangereux', 'danger'),
            (1.5, 3, 30, 'Faible', 'warning'),
            (3, 6, 60, 'Correct', 'primary'),
            (6, 10, 85, 'Bon', 'success'),
            (10, float('inf'), 100, 'Excellent', 'success'),
        ],
        'net_debt_ebitda': [
            (float('-inf'), 0, 100, 'Tréso nette', 'success'),
            (0, 1, 85, 'Excellent', 'success'),
            (1, 2, 65, 'Bon', 'primary'),
            (2, 3.5, 40, 'Correct', 'warning'),
            (3.5, float('inf'), 10, 'Élevé', 'danger'),
        ],
        # Croissance
        'revenue_cagr': [
            (float('-inf'), 0, 0, 'Déclin', 'danger'),
            (0, 3, 25, 'Faible', 'warning'),
            (3, 7, 55, 'Correct', 'primary'),
            (7, 15, 80, 'Bon', 'success'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
        'net_income_cagr': [
            (float('-inf'), 0, 0, 'Déclin', 'danger'),
            (0, 3, 25, 'Faible', 'warning'),
            (3, 8, 55, 'Correct', 'primary'),
            (8, 15, 80, 'Bon', 'success'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
        'eps_cagr': [
            (float('-inf'), 0, 0, 'Déclin', 'danger'),
            (0, 3, 25, 'Faible', 'warning'),
            (3, 8, 55, 'Correct', 'primary'),
            (8, 15, 80, 'Bon', 'success'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
        'fcf_cagr': [
            (float('-inf'), 0, 0, 'Déclin', 'danger'),
            (0, 3, 25, 'Faible', 'warning'),
            (3, 8, 55, 'Correct', 'primary'),
            (8, 15, 80, 'Bon', 'success'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
    }

    rule_list = rules.get(name, [])
    for low, high, score, label, color in rule_list:
        if low <= value < high:
            return score, label, color
    return 50, 'Correct', 'warning'


def calculate_score(ratios, piotroski=None, beneish=None, altman=None):    # ── CROISSANCE ────────────────────────────────────────────
    growth_weights = {
        'revenue_cagr': 30,
        'net_income_cagr': 25,
        'eps_cagr': 25,
        'fcf_cagr': 20,
    }

    # ── RENTABILITÉ ───────────────────────────────────────────
    profitability_weights = {
        'roe': 20,
        'roic': 20,
        'net_margin': 20,
        'gross_margin': 15,
        'fcf_margin': 15,
        'roa': 10,
    }

    # ── VALORISATION ──────────────────────────────────────────
    valuation_weights = {
        'per': 25,
        'peg': 20,
        'ev_ebitda': 20,
        'pb': 15,
        'ps': 10,
        'pcf': 10,
        'ev_revenue': 0,
    }

    # ── SÉCURITÉ ──────────────────────────────────────────────
    safety_weights = {
        'debt_to_equity': 30,
        'interest_coverage': 25,
        'net_debt_ebitda': 25,
        'current_ratio': 15,
        'quick_ratio': 5,
    }

    # ── QUALITÉ ───────────────────────────────────────────────
    def quality_score(ratios, piotroski=None, beneish=None, altman=None):
        score = 0
        total = 0

        # Consistance bénéfices (20pts)
        profitable = ratios.get('profitable_years', 0)
        total_years = ratios.get('total_years', 1)
        if total_years > 0:
            score += (profitable / total_years) * 100 * 20
            total += 20

        # Consistance FCF (20pts)
        positive_fcf = ratios.get('positive_fcf_years', 0)
        if total_years > 0:
            score += (positive_fcf / total_years) * 100 * 20
            total += 20

        # Rachat d'actions (10pts)
        buyback = ratios.get('shares_buyback')
        if buyback is not None:
            score += (100 if buyback else 20) * 10
            total += 10

        # Marge consistante (10pts)
        consistency = ratios.get('margin_consistency')
        if consistency is not None:
            score += (100 if consistency else 30) * 10
            total += 10

        # Dividende croissant (5pts)
        div_cagr = ratios.get('dividend_cagr')
        if div_cagr is not None:
            s, _, _ = score_ratio('revenue_cagr', div_cagr)
            if s:
                score += s * 5
                total += 5

        # ── PIOTROSKI (20pts) ─────────────────────────────────────
        if piotroski:
            piotroski_score = (piotroski['total'] / 9) * 100
            score += piotroski_score * 20
            total += 20

        # ── BENEISH (10pts) ───────────────────────────────────────
        if beneish:
            if beneish['color'] == 'success':
                beneish_score = 90
            elif beneish['color'] == 'warning':
                beneish_score = 45
            else:
                beneish_score = 5
            score += beneish_score * 10
            total += 10

        # ── ALTMAN (15pts) ────────────────────────────────────────
        if altman:
            if altman['color'] == 'success':
                altman_score = 90
            elif altman['color'] == 'warning':
                altman_score = 45
            else:
                altman_score = 5
            score += altman_score * 15
            total += 15

        return round(score / total) if total > 0 else 50

    def weighted_category_score(weights, ratios):
        total_weight = 0
        weighted = 0
        scored = {}
        for name, weight in weights.items():
            value = ratios.get(name)
            s, label, color = score_ratio(name, value)
            scored[name] = {'value': value, 'score': s, 'label': label, 'color': color}
            if s is not None and value is not None:
                weighted += s * weight
                total_weight += weight
        final = round(weighted / total_weight) if total_weight > 0 else 0
        return final, scored

    growth_score, growth_rated = weighted_category_score(growth_weights, ratios)
    profitability_score, profitability_rated = weighted_category_score(profitability_weights, ratios)
    valuation_score, valuation_rated = weighted_category_score(valuation_weights, ratios)
    safety_score, safety_rated = weighted_category_score(safety_weights, ratios)
    quality_sc = quality_score(ratios, piotroski, beneish, altman)
    
    # Score global pondéré
    global_score = round(
        growth_score * 0.20 +
        profitability_score * 0.25 +
        valuation_score * 0.20 +
        safety_score * 0.20 +
        quality_sc * 0.15
    )

    def label_color(score):
        if score >= 80: return '🟢 Excellent', 'success'
        if score >= 65: return '🔵 Bon', 'primary'
        if score >= 50: return '🟡 Correct', 'warning'
        return '🔴 Faible', 'danger'

    global_label, global_color = label_color(global_score)

    # Points forts et faibles
    strengths, weaknesses = [], []
    checks = [
        ('revenue_cagr', 'Croissance du CA solide sur la période', 'Croissance du CA faible ou négative', 65),
        ('net_income_cagr', 'Croissance des bénéfices robuste', 'Croissance des bénéfices insuffisante', 65),
        ('roe', 'ROE élevé — rentabilité des fonds propres excellente', 'ROE faible', 70),
        ('roic', 'ROIC élevé — capital bien alloué', 'ROIC insuffisant', 70),
        ('net_margin', 'Marge nette solide', 'Marge nette faible', 60),
        ('fcf_margin', 'Génération de Free Cash Flow excellente', 'FCF insuffisant', 65),
        ('debt_to_equity', 'Bilan sain — endettement maîtrisé', 'Endettement élevé', 65),
        ('interest_coverage', 'Couverture des intérêts confortable', 'Couverture des intérêts insuffisante', 55),
        ('per', 'Valorisation attractive', 'Valorisation élevée', 70),
        ('ev_ebitda', 'EV/EBITDA attractif', 'EV/EBITDA élevé', 65),
    ]

    all_scored = {**growth_rated, **profitability_rated, **valuation_rated, **safety_rated}
    for ratio_name, strength_msg, weakness_msg, threshold in checks:
        data = all_scored.get(ratio_name, {})
        score = data.get('score')
        if score is None:
            continue
        if score >= threshold:
            strengths.append(strength_msg)
        elif score < 35:
            weaknesses.append(weakness_msg)

    # Qualité — points spéciaux
    if ratios.get('profitable_years', 0) == ratios.get('total_years', 1):
        strengths.append('Bénéfices positifs chaque année sur la période')
    if ratios.get('positive_fcf_years', 0) == ratios.get('total_years', 1):
        strengths.append('Free Cash Flow positif chaque année sur la période')
    if ratios.get('shares_buyback'):
        strengths.append('Rachat d\'actions — réduction du nombre de titres')
    elif ratios.get('shares_buyback') is False:
        weaknesses.append('Dilution des actionnaires — augmentation du nombre d\'actions')

    return {
        'global_score': global_score,
        'global_label': global_label,
        'global_color': global_color,
        'categories': {
            'growth': {'score': growth_score, 'label': label_color(growth_score)[0], 'color': label_color(growth_score)[1], 'rated': growth_rated},
            'profitability': {'score': profitability_score, 'label': label_color(profitability_score)[0], 'color': label_color(profitability_score)[1], 'rated': profitability_rated},
            'valuation': {'score': valuation_score, 'label': label_color(valuation_score)[0], 'color': label_color(valuation_score)[1], 'rated': valuation_rated},
            'safety': {'score': safety_score, 'label': label_color(safety_score)[0], 'color': label_color(safety_score)[1], 'rated': safety_rated},
            'quality': {'score': quality_sc, 'label': label_color(quality_sc)[0], 'color': label_color(quality_sc)[1], 'rated': {}},
        },
        'strengths': strengths,
        'weaknesses': weaknesses,
    }