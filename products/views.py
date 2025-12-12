from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from getpaid.models import Payment
from .models import Order, Product
from .forms import UserRegisterForm

# --- Płatności Jednorazowe (django-getpaid 2.3.0) ---
@login_required
def initiate_payment(request, order_pk):
    """Inicjuje płatność za pomocą django-getpaid"""
    order = get_object_or_404(Order, pk=order_pk, user=request.user)

    if order.status == 'paid':
        return redirect('payment:success')

    # Ustawienie statusu na oczekiwanie na płatność
    if order.status == 'draft':
        order.status = 'awaiting_payment'
        order.save()

    # Tworzymy Payment bezpośrednio
    payment = Payment.objects.create(
        order=order,
        amount_required=order.get_total_amount(),
        currency=order.get_currency(),
        description=f"Zamówienie #{order.pk} - {order.product.name}",
        backend='getpaid_payu.processor.PayuProcessor'
    )

    # Przygotowanie transakcji i przekierowanie
    try:
        result = payment.prepare_transaction(request=request)
        return result
    except Exception as e:
        print(f"Błąd podczas inicjowania płatności: {e}")
        return redirect('payment:failure')


@login_required
def create_order(request, product_pk):
    """Tworzy zamówienie dla produktu"""
    product = get_object_or_404(Product, pk=product_pk)
    
    # Utwórz zamówienie
    order = Order.objects.create(
        user=request.user,
        product=product,
        total_amount=product.price,
        status='draft'
    )
    
    # Przekieruj do inicjacji płatności
    return redirect('payment:initiate', order_pk=order.pk)


# --- Widoki statusów płatności ---
def payment_success(request):
    """Widok wyświetlany po udanej płatności"""
    return render(request, 'products/status.html', {
        'message': 'Płatność pomyślna! Dziękujemy za zakup.',
        'type': 'success'
    })

def payment_failure(request):
    """Widok wyświetlany po nieudanej płatności"""
    return render(request, 'products/status.html', {
        'message': 'Płatność anulowana lub nieudana. Spróbuj ponownie.',
        'type': 'failure'
    })

def product_list(request):
    """Lista dostępnych produktów"""
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


# --- Rejestracja i autoryzacja ---
def register(request):
    """Widok rejestracji nowego użytkownika"""
    if request.user.is_authenticated:
        return redirect('payment:product_list')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto utworzone dla {username}! Możesz się teraz zalogować.')
            # Automatyczne logowanie po rejestracji
            login(request, user)
            return redirect('payment:product_list')
    else:
        form = UserRegisterForm()
    
    return render(request, 'products/register.html', {'form': form})