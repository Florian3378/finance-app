from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Position
from .forms import PositionForm
from .fmp_service import get_multiple_quotes

@login_required
def dashboard_view(request):
    positions = Position.objects.filter(user=request.user)
    
    portfolio_data = []
    total_invested = 0
    total_current_value = 0

    if positions:
        # Un seul appel API pour toutes les positions
        symbols = [p.symbol for p in positions]
        print("Symboles recherchés:", symbols)  # DEBUG
        quotes = get_multiple_quotes(symbols)
        print("Quotes reçues:", quotes)  # DEBUG

        for position in positions:
            quote = quotes.get(position.symbol, {})
            current_price = quote.get('price', 0)
            current_value = float(position.quantity) * current_price
            invested = position.total_invested
            gain_loss = current_value - invested
            gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0

            total_invested += invested
            total_current_value += current_value

            portfolio_data.append({
                'position': position,
                'current_price': current_price,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct,
            })

    total_gain_loss = total_current_value - total_invested
    total_gain_loss_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0

    context = {
        'portfolio_data': portfolio_data,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
    }
    return render(request, 'portfolio/dashboard.html', context)

@login_required
def add_position_view(request):
    form = PositionForm()
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.user = request.user
            position.symbol = position.symbol.upper()
            position.save()
            messages.success(request, f'{position.symbol} ajouté au portefeuille ✅')
            return redirect('dashboard')
    return render(request, 'portfolio/add_position.html', {'form': form})

@login_required
def delete_position_view(request, pk):
    position = get_object_or_404(Position, pk=pk, user=request.user)
    if request.method == 'POST':
        symbol = position.symbol
        position.delete()
        messages.success(request, f'{symbol} supprimé du portefeuille.')
    return redirect('dashboard')