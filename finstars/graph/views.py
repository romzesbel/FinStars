import psycopg2
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.shortcuts import render
import plotly.offline as pyo
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


# Подключение к БД
def get_db_connection():
    conn = psycopg2.connect(
        dbname="planetary_market_data",
        user="user",
        password="",
        host="localhost"
    )
    return conn


# Функция для получения данных по планетам с hovertext и подписями
def plot_planets(start_date, end_date, fig):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, planet, zodiac_sign, degrees_in_sign, retrograde
        FROM planetary_positions
        WHERE date BETWEEN %s AND %s
        AND planet IN ('Sa', 'Gu', 'Ma', 'Sk', 'Bu', 'Ra')
        ORDER BY date;
    ''', (start_date, end_date))

    planet_data = cursor.fetchall()
    planets_grouped = {}

    ZODIAC_COLORS = {
        '1': 'red', '2': 'green', '3': 'yellow', '4': 'blue',
        '5': 'orange', '6': 'brown', '7': 'pink', '8': 'purple',
        '9': 'cyan', '10': 'gray', '11': 'lightblue', '12': 'violet'
    }

    PLANET_Y_POSITIONS = {
        'Sa': 1, 'Ra': 2, 'Ma': 3, 'Gu': 4, 'Bu': 5, 'Sk': 6
    }

    # Группировка данных по планетам
    for row in planet_data:
        date, planet, sign, degrees_in_sign, retrograde = row
        if planet not in planets_grouped:
            planets_grouped[planet] = []
        planets_grouped[planet].append({
            'date': date,
            'sign': sign,
            'degrees_in_sign': degrees_in_sign,
            'retrograde': retrograde
        })

    # Функция для добавления линии и подписи
    def add_trace_to_fig(segment_dates, planet, previous_sign, previous_retrograde, hover_texts):
        line_style = dict(color=ZODIAC_COLORS[previous_sign], width=3)
        if previous_retrograde:
            line_style['dash'] = 'dash'

        fig.add_trace(go.Scatter(
            x=segment_dates,
            y=[PLANET_Y_POSITIONS[planet]] * len(segment_dates),
            mode='lines',
            line=line_style,
            hoverinfo='text',
            hovertext=hover_texts
        ))

        mid_index = len(segment_dates) // 2
        retrograde_marker = "(R)" if previous_retrograde else ""
        fig.add_trace(go.Scatter(
            x=[segment_dates[mid_index]],
            y=[PLANET_Y_POSITIONS[planet] + 0.1],  # Над отрезком
            mode='text',
            text=[f"{planet} {previous_sign} {retrograde_marker}"],
            showlegend=False
        ))

    # Обработка каждой планеты
    for planet, positions in planets_grouped.items():
        previous_sign = None
        previous_retrograde = None
        segment_dates = []
        hover_texts = []

        for i, pos in enumerate(positions):
            current_sign = pos['sign']
            current_degrees = pos['degrees_in_sign']
            is_retrograde = pos['retrograde'] == "(R)"
            retrograde_marker = "(R)" if is_retrograde else ""

            # Форматирование градусов
            formatted_degrees = f"{current_degrees:.2f}"
            hover_text = f"{pos['date'].strftime('%d-%m-%Y')}, {planet} {current_sign} {retrograde_marker}, {formatted_degrees}"

            # Проверка смены знака или ретроградности
            if previous_sign is None or current_sign != previous_sign or is_retrograde != previous_retrograde:
                if segment_dates:
                    add_trace_to_fig(segment_dates, planet, previous_sign, previous_retrograde, hover_texts)

                # Начинаем новый сегмент, исключая дату, с которой начинается новый знак
                segment_dates = [pos['date']]
                hover_texts = [hover_text]
                previous_sign = current_sign
                previous_retrograde = is_retrograde
            else:
                segment_dates.append(pos['date'])
                hover_texts.append(hover_text)

        if segment_dates:
            add_trace_to_fig(segment_dates, planet, previous_sign, previous_retrograde, hover_texts)

    conn.close()

# Функция для получения данных фондового рынка
def plot_financial_data(start_date, end_date, fig):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, close_price
        FROM market_data
        WHERE date BETWEEN %s AND %s AND close_price != 0;
    ''', (start_date, end_date))

    financial_data = cursor.fetchall()
    if financial_data:
        dates, close_prices = zip(*financial_data)
        fig.add_trace(go.Scatter(
            x=dates,
            y=close_prices,
            mode='lines',
            name='S&P 500',
            line=dict(color='blue'),
            yaxis="y2"
        ))

    conn.close()

def market_planet_chart(request):
    # Логируем полученные GET-параметры
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', '2024-12-31')

    print(f"Received request with start_date: {start_date} and end_date: {end_date}")  # Логируем входящие данные

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.3, 0.7]
    )

    # Построение графиков
    plot_planets(start_date, end_date, fig)
    plot_financial_data(start_date, end_date, fig)

    fig.update_layout(
        height=800,
        title="Планеты и S&P 500",
        showlegend=False,
        yaxis=dict(
            title="Планеты",
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5, 6],
            ticktext=['Saturn', 'Rahu', 'Mars', 'Jupiter', 'Mercury', 'Venus'],
            fixedrange=True
        ),
        yaxis2=dict(
            title="S&P 500 Closing Price",
            showgrid=True
        ),
        xaxis2=dict(
            title="Дата",
            showgrid=True,
            tickformat="%Y-%m-%d"
        )
    )

    graph_html = pyo.plot(fig, output_type="div")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("Returning updated graph HTML.")  # Логируем ответ сервера
        return HttpResponse(graph_html)

    return render(request, 'graph/market_planet_chart.html', {'graph_html': graph_html})



