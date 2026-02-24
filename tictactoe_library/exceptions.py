class TicTacToeError(Exception):
    """Базовое исключение для игры 'Крестики-нолики'."""
    pass

class InvalidConfigurationError(TicTacToeError):
    """Базовый класс для ошибок настройки игры (в __init__)."""
    pass

class BoardSizeTypeError(InvalidConfigurationError):
    """Вызывается, если размер поля передан не целым числом."""
    def __init__(self, value):
        super().__init__(f'Тип значения {type(value).__name__} не подходит. '
                         f'Размер поля должен быть целым числом (int).')

class BoardSizeValueError(InvalidConfigurationError):
    """Вызывается, если размер поля вне допустимого диапазона (2-9)."""
    def __init__(self, value):
        super().__init__(f"Значение {value} недопустимо. Размер поля должен быть от 2 до 9.")

class CellOccupiedError(TicTacToeError):
    """Вызывается, когда игрок пытается сходить в уже занятую клетку."""
    def __init__(self, position, player):
        super().__init__(f'Ячейка №{position} уже занята игроком {player}')

class InvalidPositionError(TicTacToeError):
    def __init__(self, position, limit):
        super().__init__(f'Введённое значение {position} вне диапазона игрового поля,'
                        f' введите значнение от 1 до {limit} включительно')

class InvalidInputError(TicTacToeError):
    def __init__(self, user_input):
        super().__init__(f'Некорректный ввод: "{user_input}". '
                        f'Пожалуйста, введите цифру/число.')

