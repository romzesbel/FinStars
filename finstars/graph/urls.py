from django.urls import path
from .views import market_planet_chart

urlpatterns = [
    path('', market_planet_chart, name='market_planet_chart'),
]
