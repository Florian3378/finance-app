from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def in_millions(value):
    """Convertit une valeur en millions avec séparateur et suffixe M"""
    try:
        v = float(value)
        m = v / 1_000_000
        if abs(m) >= 1000:
            return f"{m:,.0f} M$".replace(',', ' ')
        elif abs(m) >= 100:
            return f"{m:,.1f} M$".replace(',', ' ')
        else:
            return f"{m:,.2f} M$".replace(',', ' ')
    except (TypeError, ValueError):
        return "—"