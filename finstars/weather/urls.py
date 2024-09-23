from django.urls import path
from .views import plot_combined_graphs

urlpatterns = [
    path('', plot_combined_graphs, name='combined_graphs'),
]
