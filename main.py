from service import Service


def main():
    # TODO: логика тг бота
    # Пример использования Service
    s = Service()
    print(s.get_route(1))
    print(s.get_route(2).description)
    print(s.get_routes_shortly())


if __name__ == '__main__':
    main()
