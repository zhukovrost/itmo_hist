from .parser_xlsx import _load_routes_from_excel


class Service:
    __slots__ = ["__routes"]

    def __init__(self):
        self.__routes = _load_routes_from_excel()

    def get_route(self, id):
        try:
            return self.__routes[id]
        except KeyError:
            return None

    def get_routes_shortly(self):
        result = {}
        for id, route in self.__routes.items():
            result[id] = route.name

        return result
