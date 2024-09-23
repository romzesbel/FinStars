import yfinance as yf
import requests
import plotly.graph_objs as go
from django.shortcuts import render


# Получаем данные по S&P 500 за период с 2023-01-01 по 2024-01-01
def get_sp500_data(start_date='2000-01-01', end_date='2024-01-01'):
    sp500 = yf.Ticker("^GSPC")
    hist = sp500.history(start=start_date, end=end_date)
    return hist['Close']


# Получаем данные по погоде через Open-Meteo
def get_open_meteo_weather(lat=7.8804, lon=98.3923, start_date='2000-01-01', end_date='2024-01-01'):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max&timezone=Asia/Bangkok'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка успешности запроса
        data = response.json()

        # Получаем даты и температуры
        daily_temps = data['daily']['temperature_2m_max']
        dates = data['daily']['time']

        return dates, daily_temps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return [], []


# Получаем данные по среднесуточным осадкам через Open-Meteo
def get_precipitation_data(lat=7.8804, lon=98.3923, start_date='2000-01-01', end_date='2024-01-01'):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Asia/Bangkok'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка успешности запроса
        data = response.json()

        # Получаем даты и осадки
        daily_precipitation = data['daily']['precipitation_sum']
        dates = data['daily']['time']

        return dates, daily_precipitation
    except requests.exceptions.RequestException as e:
        print(f"Error fetching precipitation data: {e}")
        return [], []

# Построение графиков на одной странице
def plot_combined_graphs(request):
    # Получаем данные по S&P 500 за период с 2023-01-01 по 2024-01-01
    sp500_data = get_sp500_data(start_date='2023-01-01', end_date='2024-01-01')

    # Получаем данные по погоде за тот же период (температура)
    weather_dates, weather_temps = get_open_meteo_weather(start_date='2023-01-01', end_date='2024-01-01')

    # Получаем данные по осадкам за тот же период
    precipitation_dates, precipitation_data = get_precipitation_data(start_date='2023-01-01', end_date='2024-01-01')

    # Проверяем, что данные по температуре и осадкам успешно получены
    if not weather_dates or not weather_temps or not precipitation_dates or not precipitation_data:
        return render(request, 'weather/weather.html', {
            'error': 'Не удалось получить данные о погоде или осадках.',
            'sp500_div': None,
            'weather_div': None,
            'precipitation_div': None
        })

    # Построение графика S&P 500
    sp500_fig = go.Figure()
    sp500_fig.add_trace(go.Scatter(x=sp500_data.index, y=sp500_data.values, name="S&P 500"))
    sp500_fig.update_xaxes(title_text="Date")
    sp500_fig.update_yaxes(title_text="S&P 500 Value")
    sp500_div = sp500_fig.to_html(full_html=False)

    # Построение графика температуры
    weather_fig = go.Figure()
    weather_fig.add_trace(go.Scatter(x=weather_dates, y=weather_temps, name="Temperature Phuket"))
    weather_fig.update_xaxes(title_text="Date")
    weather_fig.update_yaxes(title_text="Temperature (°C)")
    weather_div = weather_fig.to_html(full_html=False)

    # Построение графика осадков с инверсией оси Y
    precipitation_fig = go.Figure()
    precipitation_fig.add_trace(go.Scatter(x=precipitation_dates, y=precipitation_data, name="Precipitation Phuket"))

    # Инвертируем ось Y так, чтобы осадки шли вниз
    precipitation_fig.update_yaxes(range=[max(precipitation_data), 0], title_text="Precipitation (mm)")
    precipitation_fig.update_xaxes(title_text="Date")
    precipitation_div = precipitation_fig.to_html(full_html=False)

    # Отправляем все три графика на страницу
    return render(request, 'weather/weather.html', {
        'sp500_div': sp500_div,
        'weather_div': weather_div,
        'precipitation_div': precipitation_div
    })

