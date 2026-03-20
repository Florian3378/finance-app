from django import forms
from .models import Transaction, Position

class TransactionForm(forms.Form):
    symbol = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: AAPL',
            'style': 'text-transform: uppercase'
        }),
        label='Symbole'
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Apple Inc.',
        }),
        label="Nom de l'entreprise"
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type'
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=4,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 10',
            'step': '0.0001'
        }),
        label='Quantité'
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=4,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 150.00',
            'step': '0.0001'
        }),
        label="Prix unitaire"
    )
    date = forms.DateField(
        required=False,  # Optionnel
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date (optionnel)"
    )
    currency = forms.ChoiceField(
        choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Devise'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Note optionnelle...'
        }),
        label='Notes (optionnel)'
    )