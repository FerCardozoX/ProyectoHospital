from django.urls import path
from .views import *

urlpatterns = [
    path('getpacientes/',getPacientes , name='getPacientes'),
]
