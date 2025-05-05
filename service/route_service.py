import models
from .parser_xlsx import _load_routes_from_excel


class Service:
    """Класс для управления маршрутами, загруженными из Excel-файла."""
    __slots__ = ["__routes"]

    def __init__(self):
        """Инициализирует объект Service, загружая маршруты из Excel-файла."""
        self.__routes = _load_routes_from_excel()

    def get_route(self, id) -> models.Route:
        """Получает маршрут по его идентификатору.

        Args:
            id: Идентификатор маршрута.

        Returns:
            models.Route: Объект маршрута, если найден, иначе None.
        """
        try:
            return self.__routes[id]
        except KeyError:
            return None

    def get_routes_shortly(self) -> dict[int, str]:
        """Возвращает краткий словарь маршрутов с их идентификаторами и названиями.

        Returns:
            dict[int, str]: Словарь, где ключ — идентификатор маршрута, значение — название маршрута.
        """
        result = {}
        for id, route in self.__routes.items():
            result[id] = route.name

        return result
