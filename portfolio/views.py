from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Position, Transaction
from .forms import TransactionForm
from .fmp_service import get_multiple_quotes, get_quote
from .fmp_service import get_multiple_quotes, get_quote, get_company_profile
import json

@login_required
def dashboard_view(request):
    positions = Position.objects.filter(user=request.user)

    portfolio_data = []
    total_invested = 0
    total_current_value = 0

    if positions:
        symbols = [p.symbol for p in positions]
        quotes = get_multiple_quotes(symbols)

        for position in positions:
            # Ignore les positions dont la quantité est à 0 (tout vendu)
            if position.total_quantity <= 0:
                continue

            quote = quotes.get(position.symbol, {})
            current_price = quote.get('price', 0)
            current_value = position.total_quantity * current_price
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

    # Données pour le graphique
    chart_labels = [item['position'].symbol for item in portfolio_data]
    chart_values = [round(item['current_value'], 2) for item in portfolio_data]
    chart_colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#858796', '#5a5c69', '#2e59d9', '#17a673', '#2c9faf'
    ]

    # Répartition par secteur
    sector_data = {}
    for item in portfolio_data:
        sector = item['position'].sector or 'Non classifié'
        if sector not in sector_data:
            sector_data[sector] = 0
        sector_data[sector] += item['current_value']

    sector_labels = list(sector_data.keys())
    sector_values = [round(v, 2) for v in sector_data.values()]
    sector_colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#858796', '#5a5c69', '#2e59d9', '#17a673', '#2c9faf'
    ]

    context = {
        'portfolio_data': portfolio_data,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'chart_colors': json.dumps(chart_colors[:len(chart_labels)]),
        'sector_labels': json.dumps(sector_labels),        # ← Nouveau
        'sector_values': json.dumps(sector_values),        # ← Nouveau
        'sector_colors': json.dumps(sector_colors[:len(sector_labels)]),  # ← Nouveau
    }
    return render(request, 'portfolio/dashboard.html', context)


@login_required
def add_transaction_view(request):
    form = TransactionForm()

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].upper()
            name = form.cleaned_data['name']
            transaction_type = form.cleaned_data['transaction_type']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            date = form.cleaned_data.get('date')
            currency = form.cleaned_data['currency']
            notes = form.cleaned_data.get('notes', '')

            # Récupère ou crée la position
            position, created = Position.objects.get_or_create(
                user=request.user,
                symbol=symbol,
                defaults={'name': name, 'currency': currency}
            )

            # Si nouvelle position, récupère le secteur automatiquement
            if created:
                profile = get_company_profile(symbol)
                if profile:
                    position.sector = profile.get('sector', None)
                    position.save()

            # Vérifie qu'on ne vend pas plus qu'on ne possède
            if transaction_type == 'SELL' and quantity > position.total_quantity:
                form.add_error('quantity', f"Tu ne peux pas vendre plus que tu ne possèdes ({position.total_quantity} actions).")
            else:
                Transaction.objects.create(
                    position=position,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=price,
                    date=date,
                    notes=notes
                )
                action = "achetées" if transaction_type == 'BUY' else "vendues"
                messages.success(request, f'{quantity} actions {symbol} {action} à {price} ✅')
                return redirect('dashboard')

    return render(request, 'portfolio/add_transaction.html', {'form': form})


@login_required
def position_detail_view(request, pk):
    position = get_object_or_404(Position, pk=pk, user=request.user)
    transactions = position.transactions.all()
    quote = get_quote(position.symbol)
    current_price = quote.get('price', 0) if quote else 0
    current_value = position.total_quantity * current_price
    gain_loss = current_value - position.total_invested
    gain_loss_pct = (gain_loss / position.total_invested * 100) if position.total_invested > 0 else 0

    context = {
        'position': position,
        'transactions': transactions,
        'current_price': current_price,
        'current_value': current_value,
        'gain_loss': gain_loss,
        'gain_loss_pct': gain_loss_pct,
    }
    return render(request, 'portfolio/position_detail.html', context)


@login_required
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, position__user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction supprimée.')
    return redirect('dashboard')


@login_required
def clear_history_view(request, pk):
    position = get_object_or_404(Position, pk=pk, user=request.user)
    if request.method == 'POST':
        # Sauvegarde la situation actuelle
        quantity = position.total_quantity
        avg_price = position.average_price

        if quantity <= 0:
            messages.error(request, "Aucune position active à conserver.")
            return redirect('position_detail', pk=pk)

        # Supprime toutes les transactions existantes
        position.transactions.all().delete()

        # Crée une seule transaction de synthèse
        Transaction.objects.create(
            position=position,
            transaction_type='BUY',
            quantity=quantity,
            price=avg_price,
            date=None,
            notes="Position de synthèse (historique effacé)"
        )
        messages.success(request, f'Historique effacé. Position conservée : {quantity} actions à {avg_price:.2f}€ en moyenne.')
    return redirect('position_detail', pk=pk)