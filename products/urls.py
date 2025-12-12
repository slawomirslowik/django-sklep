from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'payment'

urlpatterns = [
    # Lista produktów
    path('', views.product_list, name='product_list'),
    
    # Tworzenie zamówienia
    path('order/<int:product_pk>/', views.create_order, name='create_order'),
    
    # Inicjowanie płatności
    path('pay/<int:order_pk>/', views.initiate_payment, name='initiate'),

    # Strony statusów płatności
    path('success/', views.payment_success, name='success'),
    path('failure/', views.payment_failure, name='failure'),
    
    # Rejestracja i logowanie
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='products/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='products/logout.html'), name='logout'),
]