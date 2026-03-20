from django import forms
from .models import Position

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['symbol', 'name', 'quantity', 'purchase_price', 'purchase_date', 'currency']
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: AAPL',
                'style': 'text-transform: uppercase'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Apple Inc.',
                #'readonly': 'readonly'  # Rempli automatiquement
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 10',
                'step': '0.0001'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 150.00',
                'step': '0.0001'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'currency': forms.Select(
                choices=[('USD','USD'), ('EUR','EUR'), ('GBP','GBP')],
                attrs={'class': 'form-select'}
            ),
        }
        labels = {
            'symbol': 'Symbole',
            'name': "Nom de l'entreprise",
            'quantity': 'Quantité',
            'purchase_price': "Prix d'achat unitaire",
            'purchase_date': "Date d'achat",
            'currency': 'Devise',
        }