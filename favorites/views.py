from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from portfolio.models import Favorite
from portfolio.fmp_service import get_quote, get_multiple_quotes, get_company_profile

@login_required
def favorites_list_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    
    favorites_data = []
    if favorites:
        symbols = [f.symbol for f in favorites]
        quotes = get_multiple_quotes(symbols)
        
        for fav in favorites:
            quote = quotes.get(fav.symbol, {})
            price = quote.get('price', 0)
            change_pct = quote.get('changesPercentage', 0)
            cap_label, cap_color = fav.cap_category
            
            favorites_data.append({
                'favorite': fav,
                'price': price,
                'change_pct': change_pct,
                'cap_label': cap_label,
                'cap_color': cap_color,
            })

    return render(request, 'favorites/favorites.html', {
        'favorites_data': favorites_data,
    })


@login_required
def toggle_favorite(request, symbol):
    """Ajoute ou retire un favori — appelé depuis la page analyse"""
    symbol = symbol.upper()
    existing = Favorite.objects.filter(user=request.user, symbol=symbol).first()

    if existing:
        existing.delete()
        is_favorite = False
        messages.success(request, f'{symbol} retiré des favoris.')
    else:
        # Récupère les infos depuis FMP
        profile = get_company_profile(symbol) or {}
        Favorite.objects.create(
            user=request.user,
            symbol=symbol,
            name=profile.get('companyName', symbol),
            sector=profile.get('sector'),
            country=profile.get('country'),
            market_cap=profile.get('marketCap'),
            currency=profile.get('currency', 'USD'),
        )
        is_favorite = True
        messages.success(request, f'{symbol} ajouté aux favoris ⭐')

    # Si requête AJAX retourne JSON, sinon redirige
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    return redirect('company', symbol=symbol)


@login_required
def delete_favorite(request, symbol):
    """Supprime un favori depuis la page favoris"""
    fav = get_object_or_404(Favorite, user=request.user, symbol=symbol.upper())
    if request.method == 'POST':
        fav.delete()
        messages.success(request, f'{symbol} retiré des favoris.')
    return redirect('favorites')