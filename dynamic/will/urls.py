from django.urls import path
from .views import generate_qr,upi_settings

urlpatterns = [
    path('', generate_qr, name='generate_qr'),
    path("settings/", upi_settings, name="upi_settings"),
]
