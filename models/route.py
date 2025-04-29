class Route:
    __slots__ = [
        'id',
        'name',
        'description',
        'map_link',
        'locations',
        'photo'
    ]

    def __init__(self, id, name, description, map_link, photo=None):
        self.id = id
        self.name = name
        self.description = description
        self.map_link = map_link
        self.locations = []
        self.photo = photo

    def __repr__(self):
        return f"<\"Маршрут {self.id}\": {self.name}>"
