import pandas as pd
from models import *


def _load_routes_from_excel(file_path="data/data.xlsx", l_locations="locations", l_routes="routes", l_relation="relations") -> dict[int, Route]:
    """Функция, которая парсит Excel и возвращает словарь, где ключ -- идентификатор маршрута, а значение -- сам маршрут."""
    xls = pd.ExcelFile(file_path)

    # Чтение таблиц
    locations_df = pd.read_excel(xls, l_locations)
    routes_df = pd.read_excel(xls, l_routes)
    route_locations_df = pd.read_excel(xls, l_relation)

    routes = {}

    for _, row in routes_df.iterrows():
        route = Route(
            row['id'],
            row['name'],
            row.get('description', "Нет описания."),
            row.get('map_link', "Ссылка отсутствует."),
        )
        photo_list = str(row.get('photo', "")).split(",")
        for photo in photo_list:
            photo = photo.strip()
            if photo != "":
                route.add_photo(photo)

        routes[route.id] = route

    locations = {}
    for _, location_row in locations_df.iterrows():
        location = Location(location_row['id'], location_row['name'], location_row['coords'],
                            location_row.get('description', "Нет описания."),
                            history=location_row.get('history', "Нет исторического описания."))
        photo_list = str(location_row.get('photo', "")).split(",")
        for photo in photo_list:
            photo = photo.strip()
            if photo != "":
                location.add_photo(photo)

        locations[location.id] = location

    for _, rl_row in route_locations_df.iterrows():
        route_id = rl_row['id_route']
        location_id = rl_row['id_location']
        if route_id in routes and location_id in locations:
            routes[route_id].locations.append(locations[location_id])

    return routes