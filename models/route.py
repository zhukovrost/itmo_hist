class Route:
    """Класс маршрута"""
    __slots__ = [
        'id',
        'name',
        'description',
        'map_link',
        'locations',
        'photo'
    ]

    def __init__(self, id, name, description, map_link):
        self.id = id
        self.name = name
        self.description = description
        self.map_link = map_link
        self.locations = [] # Тут должны быть экземпляры класса models.Location
        self.photo = []

    def add_photo(self, photo_link: str) -> None:
        """Добавить фото в массив фоток маршрута."""
        self.photo.append(photo_link)

    def __repr__(self):
        return f"<\"Маршрут {self.id}\": {self.name}>"
