from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payments/', include('products.urls')),
    
    # Ścieżki dla django-getpaid
    path('getpaid/', include('getpaid.urls')),
]