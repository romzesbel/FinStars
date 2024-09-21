from django.shortcuts import render
from django.db import connection
from datetime import datetime

PLANET_LIST = [
    {'label': 'SATURN (Sa)', 'value': 'Sa'},
    {'label': 'JUPITER (Gu)', 'value': 'Gu'},
    {'label': 'MARS (Ma)', 'value': 'Ma'},
    {'label': 'VENUS (Sk)', 'value': 'Sk'},
    {'label': 'MERCURY (Bu)', 'value': 'Bu'},
    {'label': 'RAHU (Ra)', 'value': 'Ra'},
]

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


def get_intersecting_periods(periods_list):
    if not periods_list:
        return []

    # Начнем с первого списка периодов и будем искать пересечения с каждым следующим
    common_periods = periods_list[0]

    for periods in periods_list[1:]:
        common_periods = find_intersections(common_periods, periods)

    return common_periods


def find_intersections(periods1, periods2):
    """Функция для нахождения пересекающихся периодов между двумя списками периодов"""
    intersections = []

    for start1, end1 in periods1:
        for start2, end2 in periods2:
            start_intersection = max(start1, start2)
            end_intersection = min(end1, end2)
            if start_intersection <= end_intersection:
                intersections.append((start_intersection, end_intersection))

    return intersections


def search_periods(request):
    periods = []
    selected_conditions = []  # Для хранения условий поиска

    # Получаем условия для каждой планеты
    for planet in PLANET_LIST:
        zodiac_sign = request.GET.get(f'zodiac_{planet["value"]}')
        retrograde = request.GET.get(f'retrograde_{planet["value"]}', '')  # Если не выбран, то пусто

        if zodiac_sign:
            selected_conditions.append({
                'planet': planet['value'],
                'zodiac_sign': zodiac_sign,
                'retrograde': retrograde
            })

    if selected_conditions:
        periods_list = []

        with connection.cursor() as cursor:
            for condition in selected_conditions:
                query = '''
                    SELECT date, planet, zodiac_sign, retrograde
                    FROM planetary_positions
                    WHERE planet = %s AND zodiac_sign = %s {}
                    ORDER BY date;
                '''
                retrograde_clause = "AND retrograde = '(R)'" if condition[
                                                                    'retrograde'] == 'R' else "AND (retrograde != '(R)' OR retrograde IS NULL)"
                query = query.format(retrograde_clause)

                cursor.execute(query, [condition['planet'], condition['zodiac_sign']])
                raw_periods = cursor.fetchall()

                # Преобразуем результаты в формат [(start_date, end_date), ...]
                planet_periods = []
                if raw_periods:
                    start_date = raw_periods[0][0]
                    prev_date = start_date

                    for row in raw_periods:
                        current_date = row[0]
                        if (current_date - prev_date).days > 1:
                            # Завершаем предыдущий период
                            planet_periods.append((start_date, prev_date))
                            start_date = current_date
                        prev_date = current_date

                    # Добавляем последний период
                    planet_periods.append((start_date, prev_date))

                periods_list.append(planet_periods)

        # Найти пересекающиеся периоды
        periods = get_intersecting_periods(periods_list)

    return render(request, 'search/periods.html', {
        'planets': PLANET_LIST,
        'zodiac_signs': ZODIAC_SIGNS,
        'periods': periods
    })
