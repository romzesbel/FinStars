from datetime import datetime
import yfinance as yf
import requests
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.shortcuts import render

# Функция для получения текущей даты и начала года
def get_default_dates():
    # Начальная дата: 1 января текущего года
    start_date = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
    # Конечная дата: текущая дата
    end_date = datetime.now().strftime('%Y-%m-%d')
    return start_date, end_date

# Получаем данные по S&P 500 за заданный период
def get_sp500_data(start_date, end_date):
    sp500 = yf.Ticker("^GSPC")
    hist = sp500.history(start=start_date, end=end_date)
    return hist['Close']

# Исправленная функция получения данных о погоде через Open-Meteo
def get_open_meteo_weather(start_date, end_date, lat=7.8804, lon=98.3923):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max&timezone=Asia/Bangkok'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        daily_temps = data['daily']['temperature_2m_max']
        dates = data['daily']['time']
        return dates, daily_temps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return [], []


# Получаем данные по осадкам через Open-Meteo
def get_precipitation_data(start_date, end_date, lat=7.8804, lon=98.3923):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Asia/Bangkok'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        daily_precipitation = data['daily']['precipitation_sum']
        dates = data['daily']['time']

        # Заменяем None на 0 в данных об осадках
        daily_precipitation = [precip if precip is not None else 0 for precip in daily_precipitation]

        return dates, daily_precipitation
    except requests.exceptions.RequestException as e:
        print(f"Error fetching precipitation data: {e}")
        return [], []


def plot_combined_graphs(request):
    # Получаем дефолтные даты (начало года и текущая дата)
    default_start_date, default_end_date = get_default_dates()

    # Получаем даты из GET-запроса или используем значения по умолчанию
    start_date = request.GET.get('start_date', default_start_date)
    end_date = request.GET.get('end_date', default_end_date)

    try:
        # Проверка на корректность формата дат
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return render(request, 'weather/weather.html', {
            'error': 'Некорректный формат даты.',
            'combined_div': None,
            'start_date': start_date,
            'end_date': end_date
        })

    # Получаем данные по S&P 500 за заданный период
    sp500_data = get_sp500_data(start_date, end_date)

    # Получаем данные по погоде (температура) за заданный период
    weather_dates, weather_temps = get_open_meteo_weather(start_date=start_date, end_date=end_date)

    # Получаем данные по осадкам за заданный период
    precipitation_dates, precipitation_data = get_precipitation_data(start_date=start_date, end_date=end_date)

    # Проверяем, что данные по температуре и осадкам успешно получены
    if not weather_dates or not weather_temps or not precipitation_dates or not precipitation_data:
        return render(request, 'weather/weather.html', {
            'error': 'Не удалось получить данные о погоде или осадках.',
            'combined_div': None,
            'start_date': start_date,
            'end_date': end_date
        })

    # Создаем фигуру с увеличенной высотой и уменьшенными промежутками
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03)

    # Линия S&P 500
    fig.add_trace(go.Scatter(x=sp500_data.index, y=sp500_data.values, name="S&P 500"), row=1, col=1)
    fig.update_yaxes(title_text="S&P 500 Value", row=1, col=1)

    # Линия температуры
    fig.add_trace(go.Scatter(x=weather_dates, y=weather_temps, name="Temperature Phuket"), row=2, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)

    # Линия осадков с инверсией оси Y (чтобы осадки уходили вниз)
    fig.add_trace(go.Scatter(x=precipitation_dates, y=precipitation_data, name="Precipitation Phuket"), row=3, col=1)
    fig.update_yaxes(range=[max(precipitation_data), 0], title_text="Precipitation (mm)", row=3, col=1)

    # Обновляем ось X
    fig.update_xaxes(title_text="Date", row=3, col=1)

    # Устанавливаем общую высоту для фигуры
    fig.update_layout(height=900)

    # Преобразуем график в HTML для Django
    combined_div = fig.to_html(full_html=False)

    # Отправляем объединенный график на страницу
    return render(request, 'weather/weather.html', {
        'combined_div': combined_div,
        'start_date': start_date,
        'end_date': end_date
    })

