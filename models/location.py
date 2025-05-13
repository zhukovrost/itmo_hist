class Location:
    """Класс локации на маршруте"""

    __slots__ = [
        'id',
        'name',
        'coords',
        'description',
        'history',
        'photo'
    ]

    def __init__(self, id, name, coords, description, history):
        self.id = id
        self.name = name
        self.coords = coords
        self.description = description
        self.history = history
        self.photo = []

    def add_photo(self, photo_link: str) -> None:
        """Добавить фото в массив фоток локации."""
        self.photo.append(photo_link)

    def __repr__(self):
        return f"<\"Точка {self.id}\": {self.name}>"
