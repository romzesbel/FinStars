import psycopg2
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

# Используйте DjangoDash вместо обычного Dash
app = DjangoDash('search_dash')  # Имя должно совпадать с именем, указанным в шаблоне

# Лейаут и коллбеки
app.layout = html.Div([
    html.H1("Поиск периодов по планетам"),
    dcc.Dropdown(
        id='planet-condition-dropdown',
        options=[{'label': 'Planet 1', 'value': 'P1'}, {'label': 'Planet 2', 'value': 'P2'}],
        value=[],
        multi=True
    ),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    [Input('planet-condition-dropdown', 'value')]
)
def update_output(selected_planets):
    if selected_planets:
        return f'Вы выбрали: {", ".join(selected_planets)}'
    return "Выберите планету"



# Подключение к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        dbname="planetary_market_data",
        user="user",  # Замените на реальное имя пользователя
        password="",  # Замените на пароль пользователя
        host="localhost"
    )
    return conn


# Обозначения планет
PLANET_LIST = [
    {'label': 'SATURN (Sa)', 'value': 'Sa'},
    {'label': 'JUPITER (Gu)', 'value': 'Gu'},
    {'label': 'MARS (Ma)', 'value': 'Ma'},
    {'label': 'VENUS (Sk)', 'value': 'Sk'},
    {'label': 'MERCURY (Bu)', 'value': 'Bu'},
    {'label': 'SUN (Su)', 'value': 'Su'},
    {'label': 'MOON (Ch)', 'value': 'Ch'},
    {'label': 'MEAN_NODE (Ra)', 'value': 'Ra'}
]

# Знаки зодиака
ZODIAC_SIGNS = [
    {'label': 'Овен (1)', 'value': '1'},
    {'label': 'Телец (2)', 'value': '2'},
    {'label': 'Близнецы (3)', 'value': '3'},
    {'label': 'Рак (4)', 'value': '4'},
    {'label': 'Лев (5)', 'value': '5'},
    {'label': 'Дева (6)', 'value': '6'},
    {'label': 'Весы (7)', 'value': '7'},
    {'label': 'Скорпион (8)', 'value': '8'},
    {'label': 'Стрелец (9)', 'value': '9'},
    {'label': 'Козерог (10)', 'value': '10'},
    {'label': 'Водолей (11)', 'value': '11'},
    {'label': 'Рыбы (12)', 'value': '12'}
]

# Лейаут приложения Dash
app.layout = html.Div([
    html.H1("Поиск периодов по планетам"),

    html.Div([
        html.Label("Выберите планеты и их условия:"),
        dcc.Dropdown(
            id='planet-condition-dropdown',
            options=PLANET_LIST,
            value=[], multi=True
        ),
    ]),

    html.Div(id='planet-condition-inputs'),

    html.Button('Найти периоды', id='search-button', n_clicks=0),

    html.Div(id='output-periods')
])


# Генерация полей для условий по каждой планете
@app.callback(
    Output('planet-condition-inputs', 'children'),
    [Input('planet-condition-dropdown', 'value')]
)
def generate_planet_conditions(selected_planets):
    if not selected_planets:
        return []

    inputs = []
    for planet in selected_planets:
        inputs.append(html.Hr())
        inputs.append(html.Div(f"Условия для {planet}:"))
        inputs.append(html.Div([
            html.Label("Выберите знак зодиака:"),
            dcc.Dropdown(
                id={'type': 'zodiac-dropdown', 'index': planet},
                options=ZODIAC_SIGNS,
                value=None
            ),
        ]))
        inputs.append(html.Div([
            html.Label("Указать ретроградность (выберите, если требуется):"),
            dcc.Checklist(
                id={'type': 'retrograde-checklist', 'index': planet},
                options=[{'label': 'Ретроградный', 'value': 'R'}],
                value=[]
            )
        ]))

    return inputs




def search_periods(n_clicks, zodiac_values, retrograde_values, selected_planets):
    if n_clicks == 0:
        return ""

    if not selected_planets:
        return "Пожалуйста, выберите планеты и их условия."

    conn = get_db_connection()
    cursor = conn.cursor()

    planets_data = {}

    # Создаем условия для каждой выбранной планеты
    for i, planet in enumerate(selected_planets):
        selected_zodiac = zodiac_values[i]
        retrograde = retrograde_values[i]

        query = f"SELECT date, zodiac_sign, retrograde FROM planetary_positions WHERE planet = '{planet}' AND zodiac_sign = '{selected_zodiac}'"

        if 'R' in retrograde:
            query += " AND retrograde = '(R)'"
        else:
            query += " AND (retrograde != '(R)' OR retrograde IS NULL)"

        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            planets_data[planet] = result

    conn.close()

    # Формируем вывод
    output = []
    for planet, data in planets_data.items():
        for start, sign, retrograde in data:
            output.append(html.P(f"{planet} в знаке {sign}: {start}"))

    return output
