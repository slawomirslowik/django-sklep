from django.db.models.signals import post_save
from django.dispatch import receiver
from getpaid.models import Payment
from .models import Order

# Obsługa sygnałów django-getpaid 2.3.0

@receiver(post_save, sender=Payment)
def handle_payment_update(sender, instance, created, **kwargs):
    """Wywoływane gdy Payment jest tworzony lub aktualizowany"""
    payment = instance
    
    if not payment.order:
        return
    
    order = payment.order
    
    # Gdy płatność jest tworzona
    if created:
        print(f"[GETPAID] Nowa płatność {payment.id} dla zamówienia {order.pk}")
        if order.status == 'draft':
            order.status = 'awaiting_payment'
            order.save()
    
    # Sprawdzenie statusu płatności
    from getpaid import PaymentStatus
    
    if payment.status == PaymentStatus.PAID:
        if order.status != 'paid':
            order.status = 'paid'
            order.save()
            print(f"[GETPAID] Zamówienie {order.pk} opłacone pomyślnie!")
    
    elif payment.status == PaymentStatus.FAILED:
        if order.status != 'canceled':
            order.status = 'canceled'
            order.save()
            print(f"[GETPAID] Płatność dla zamówienia {order.pk} nie powiodła się.")