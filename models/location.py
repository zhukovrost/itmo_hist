class Location:
    __slots__ = [
        'id',
        'name',
        'coords',
        'description',
        'history',
        'photo'
    ]

    def __init__(self, id, name, coords, description, history, photo=None):
        self.id = id
        self.name = name
        self.coords = coords
        self.description = description
        self.history = history
        self.photo = photo

    def __repr__(self):
        return f"<\"Точка {self.id}\": {self.name}>"
