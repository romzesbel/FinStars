
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('search/', include('search.urls')),  # Добавляем этот маршрут
    path('dash_app/', include('dash_app.urls')),
    path('search/', include('search.urls')),  # Добавляем путь к нашему приложению
    path('graph/', include('graph.urls')),  # Подключаем маршруты из приложения market_data
    path('weather/', include('weather.urls')),
]

