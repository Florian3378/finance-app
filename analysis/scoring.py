def score_ratio(name, value):
    """
    Retourne (score, label, color) pour un ratio donné.
    score : 0 à 100
    label : 'Excellent' / 'Bon' / 'Correct' / 'Faible' / 'Mauvais'
    color : 'success' / 'primary' / 'warning' / 'danger'
    """
    if value is None:
        return None, 'N/A', 'secondary'

    rules = {
        'per': [
            (0, 10, 60, 'Très bas (sous-évalué ?)', 'warning'),
            (10, 20, 100, 'Excellent', 'success'),
            (20, 30, 80, 'Bon', 'primary'),
            (30, 40, 50, 'Correct', 'warning'),
            (40, float('inf'), 20, 'Élevé', 'danger'),
        ],
        'peg': [
            (0, 1, 100, 'Excellent', 'success'),
            (1, 2, 75, 'Bon', 'primary'),
            (2, 3, 40, 'Correct', 'warning'),
            (3, float('inf'), 10, 'Élevé', 'danger'),
        ],
        'roe': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 10, 30, 'Faible', 'danger'),
            (10, 15, 55, 'Correct', 'warning'),
            (15, 20, 75, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'roa': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 40, 'Faible', 'danger'),
            (5, 10, 65, 'Correct', 'warning'),
            (10, 15, 85, 'Bon', 'primary'),
            (15, float('inf'), 100, 'Excellent', 'success'),
        ],
        'roic': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 8, 30, 'Faible', 'danger'),
            (8, 12, 60, 'Correct', 'warning'),
            (12, 20, 85, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'gross_margin': [
            (float('-inf'), 20, 20, 'Faible', 'danger'),
            (20, 40, 50, 'Correct', 'warning'),
            (40, 60, 80, 'Bon', 'primary'),
            (60, float('inf'), 100, 'Excellent', 'success'),
        ],
        'net_margin': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 30, 'Faible', 'danger'),
            (5, 10, 55, 'Correct', 'warning'),
            (10, 20, 80, 'Bon', 'primary'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'current_ratio': [
            (float('-inf'), 1, 10, 'Dangereux', 'danger'),
            (1, 1.5, 50, 'Limite', 'warning'),
            (1.5, 3, 100, 'Bon', 'success'),
            (3, float('inf'), 70, 'Excédentaire', 'primary'),
        ],
        'debt_to_equity': [
            (float('-inf'), 0, 100, 'Aucune dette', 'success'),
            (0, 0.5, 90, 'Excellent', 'success'),
            (0.5, 1, 70, 'Bon', 'primary'),
            (1, 2, 45, 'Correct', 'warning'),
            (2, float('inf'), 15, 'Élevé', 'danger'),
        ],
        'revenue_growth': [
            (float('-inf'), 0, 0, 'Déclin', 'danger'),
            (0, 5, 40, 'Faible', 'warning'),
            (5, 10, 65, 'Correct', 'primary'),
            (10, 20, 85, 'Bon', 'success'),
            (20, float('inf'), 100, 'Excellent', 'success'),
        ],
        'fcf_margin': [
            (float('-inf'), 0, 0, 'Négatif', 'danger'),
            (0, 5, 40, 'Faible', 'warning'),
            (5, 15, 70, 'Correct', 'primary'),
            (15, 25, 90, 'Bon', 'success'),
            (25, float('inf'), 100, 'Excellent', 'success'),
        ],
    }

    rule_list = rules.get(name, [])
    for low, high, score, label, color in rule_list:
        if low <= value < high:
            return score, label, color

    return 50, 'Correct', 'warning'


def calculate_score(ratios):
    """
    Calcule un score global sur 100 et génère les points forts/faibles.
    """
    # Poids de chaque ratio dans le score final
    weights = {
        'roe': 15,
        'roic': 15,
        'net_margin': 12,
        'gross_margin': 8,
        'fcf_margin': 10,
        'revenue_growth': 10,
        'debt_to_equity': 10,
        'current_ratio': 8,
        'per': 7,
        'roa': 5,
    }

    scored_ratios = {}
    total_weight = 0
    weighted_score = 0

    for ratio_name, weight in weights.items():
        value = ratios.get(ratio_name)
        score, label, color = score_ratio(ratio_name, value)
        scored_ratios[ratio_name] = {
            'value': value,
            'score': score,
            'label': label,
            'color': color,
        }
        if score is not None and value is not None:
            weighted_score += score * weight
            total_weight += weight

    global_score = round(weighted_score / total_weight) if total_weight > 0 else 0

    # Label global
    if global_score >= 80:
        global_label = 'Excellente qualité'
        global_color = 'success'
        global_emoji = '🟢'
    elif global_score >= 65:
        global_label = 'Bonne qualité'
        global_color = 'primary'
        global_emoji = '🔵'
    elif global_score >= 50:
        global_label = 'Qualité correcte'
        global_color = 'warning'
        global_emoji = '🟡'
    else:
        global_label = 'Qualité faible'
        global_color = 'danger'
        global_emoji = '🔴'

    # Points forts et faibles
    strengths = []
    weaknesses = []

    checks = [
        ('roe', 'ROE excellent (rentabilité des fonds propres)', 'ROE faible', 75),
        ('roic', 'ROIC élevé (capital bien alloué)', 'ROIC insuffisant', 70),
        ('net_margin', 'Marge nette solide', 'Marge nette faible', 60),
        ('gross_margin', 'Marge brute élevée', 'Marge brute faible', 60),
        ('fcf_margin', 'Génération de cash flow solide', 'Free Cash Flow insuffisant', 60),
        ('revenue_growth', 'Croissance du chiffre d\'affaires', 'Croissance faible ou négative', 55),
        ('debt_to_equity', 'Niveau d\'endettement maîtrisé', 'Endettement élevé', 65),
        ('current_ratio', 'Bonne liquidité court terme', 'Liquidité court terme insuffisante', 60),
        ('per', 'Valorisation attractive', 'Valorisation élevée', 65),
    ]

    for ratio_name, strength_msg, weakness_msg, threshold in checks:
        data = scored_ratios.get(ratio_name, {})
        score = data.get('score')
        if score is None:
            continue
        if score >= threshold:
            strengths.append(strength_msg)
        elif score < 40:
            weaknesses.append(weakness_msg)

    return {
        'global_score': global_score,
        'global_label': global_label,
        'global_color': global_color,
        'global_emoji': global_emoji,
        'scored_ratios': scored_ratios,
        'strengths': strengths,
        'weaknesses': weaknesses,
    }