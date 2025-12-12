from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_subscription = models.BooleanField(default=False)
    # Wymagane przez dj-stripe do powiązania planu
    stripe_plan_id = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Szkic'),
        ('awaiting_payment', 'Oczekuje na płatność'),
        ('paid', 'Opłacone'),
        ('canceled', 'Anulowane'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default='PLN')  # Wymagane przez getpaid
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_amount(self):
        """Metoda wymagana przez django-getpaid - zwraca kwotę płatności"""
        return self.total_amount
    
    def get_currency(self):
        """Metoda wymagana przez django-getpaid - zwraca walutę"""
        return self.currency
    
    def get_buyer_info(self):
        """Opcjonalna metoda dostarczająca informacje o kupującym"""
        return {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
    
    def is_ready_for_payment(self):
        """Sprawdza czy zamówienie jest gotowe do płatności"""
        return self.status == 'awaiting_payment'

    def __str__(self):
        return f"Zamówienie {self.pk} ({self.status})"

# Wymagane do uruchomienia nasłuchu sygnałów
from . import signals