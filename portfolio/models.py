from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    # Lien vers l'utilisateur propriétaire
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Informations de l'action
    symbol = models.CharField(max_length=20)        # ex: AAPL
    name = models.CharField(max_length=200)         # ex: Apple Inc.
    currency = models.CharField(max_length=5, default='USD')
    
    # Informations d'achat
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=4)
    purchase_date = models.DateField()
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.symbol} - {self.quantity} actions @ {self.purchase_price}"

    @property
    def total_invested(self):
        """Montant total investi sur cette position"""
        return float(self.quantity) * float(self.purchase_price)