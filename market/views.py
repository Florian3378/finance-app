from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portfolio.fmp_service import (
    get_market_indices, get_biggest_gainers,
    get_biggest_losers, get_most_active
)

# Noms lisibles des indices
INDEX_NAMES = {
    '^GSPC': 'S&P 500',
    '^DJI': 'Dow Jones',
    '^IXIC': 'Nasdaq',
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng',
}

@login_required
def market_view(request):
    indices_raw = get_market_indices()
    
    # Enrichit avec les noms lisibles
    indices = []
    for idx in indices_raw:
        symbol = idx.get('symbol', '')
        idx['display_name'] = INDEX_NAMES.get(symbol, symbol)
        indices.append(idx)

    context = {
        'indices': indices,
        'gainers': get_biggest_gainers(),
        'losers': get_biggest_losers(),
        'actives': get_most_active(),
    }
    return render(request, 'market/market.html', context)