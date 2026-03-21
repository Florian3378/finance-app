from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    currency = models.CharField(max_length=5, default='USD')
    sector = models.CharField(max_length=100, blank=True, null=True)  # ← Nouveau
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Un utilisateur ne peut pas avoir deux positions sur le même symbole
        unique_together = ['user', 'symbol']

    def __str__(self):
        return f"{self.symbol} - {self.user.username}"

    @property
    def total_quantity(self):
        """Quantité totale détenue (achats - ventes)"""
        achats = sum(t.quantity for t in self.transactions.filter(transaction_type='BUY'))
        ventes = sum(t.quantity for t in self.transactions.filter(transaction_type='SELL'))
        return float(achats - ventes)

    @property
    def average_price(self):
        """Prix moyen pondéré d'achat"""
        achats = self.transactions.filter(transaction_type='BUY')
        total_quantite = sum(float(t.quantity) for t in achats)
        if total_quantite == 0:
            return 0
        total_investi = sum(float(t.quantity) * float(t.price) for t in achats)
        return total_investi / total_quantite

    @property
    def total_invested(self):
        """Montant total investi (basé sur le PRU × quantité actuelle)"""
        return self.average_price * self.total_quantity


class Transaction(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRANSACTION_TYPES = [
        (BUY, 'Achat'),
        (SELL, 'Vente'),
    ]

    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES, default=BUY)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField(null=True, blank=True)  # Optionnel
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.position.symbol} @ {self.price}"

    @property
    def total_value(self):
        return float(self.quantity) * float(self.price)