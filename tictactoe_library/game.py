"""
Модуль игры 'Крестики-Нолики' (TicTacToe).

Реализует консольную версию игры с настраиваемым размером поля,
системой ведения логов, расширенной аналитикой сыгранных матчей
и адаптивным ботом (ИИ).
"""
from datetime import datetime

from random import choice
from colorama import Fore, Style
from .exceptions import *
# .
class TicTacToe:
    """
    Основной класс логики игры TicTacToe.

    Поддерживает режимы PVP (игрок против игрока) и против бота.
    Включает в себя визуализацию поля, проверку победителя и систему истории.
    """
    CELL_WIDTH = 5  # ширина ячеек по ГОСТу

    def __init__(self, board_size: int = 3, mode = None):
        """
        Инициализация игры.
        board_size: определяет сторону квадрата(игрового поля) (например, 3x3).
        Здесь мы сразу генерируем все выигрышные комбинации, чтобы не вычислять их во время игры.
        """
        if not isinstance(board_size, int):
            raise BoardSizeTypeError(board_size)
        if not (2 <= board_size <= 9):
            raise BoardSizeValueError(board_size)

        self.board_size = board_size
        self.board_limit = board_size * board_size
        self.board = [[' ' for _ in range(self.board_size)]
                      for _ in range(self.board_size)]

        self.reset_player = False
        self.mode = mode
        self.win_combinations = self._generate_win_combinations()
        self.winning_coords = []
        self.current_player = 'X'
        self.change_bot_play = 'player'
        self.is_play_bot = None if mode is None else mode
        self.winner_count = 0
        self.position = None

    def __str__(self):
        """Возвращает краткое состояние текущей игровой сессии."""
        return f'Игра TicTacToe [Поле: {self.board_size}x{self.board_size}]'

    def _generate_win_combinations(self):
        """
        Динамическая генерация выигрышных линий.
        Проходит по горизонталям, вертикалям и двум главным диагоналям,
        сохраняя координаты кортежами (row, col).
        """
        win_combinations = []
        for i in range(self.board_size):
            # Горизонтальная траектория i
            win_combinations.append([(i, j) for j in range(self.board_size)])
            # Вертикальная траектория i
            win_combinations.append([(j, i) for j in range(self.board_size)])
        # Диагонали
        win_combinations.append([(i, i) for i in range(self.board_size)])
        win_combinations.append([(i, self.board_size - 1 - i)
                                for i in range(self.board_size)])
        return win_combinations

    def reset(self):
        """
        Сброс всех игровых параметров к начальному состоянию.
        Вызывается в __init__ для первичной настройки переменных при создании объекта,
        а также после завершения партии, если игроки решили сыграть снова.
        """
        self.reset_player = False
        self.current_player = 'X'
        self.board = [[' ' for _ in range(self.board_size)]
                      for _ in range(self.board_size)]
        self.winning_coords = []
        self.board_limit = self.board_size * self.board_size
        self.winner_count = 0
        self.change_bot_play = 'player'
        self.is_play_bot = None if self.mode is None else self.mode
        self.position = None

    def get_colored_symbol(self, symbol, r=None, c=None):
        """
        Управляет цветом и форматированием игровых символов.

        Логика работы:
        1. Назначает красный цвет для 'X' и зеленый для 'O'.
        2. Если игра завершена (есть winning_coords), метод подсвечивает ярким цветом
           только победную линию, а остальные символы окрашивает в тускло-серый,
           акцентируя внимание на результате матча.
        3. Обеспечивает центрирование символа внутри ячейки согласно CELL_WIDTH.
        """
        if symbol == 'X':
            color = Fore.RED
        elif symbol == 'O':
            color = Fore.GREEN
        else:
            return f"{' ':^{self.CELL_WIDTH}}"
        if self.winning_coords:
            if (r, c) not in self.winning_coords:
                return f'{Fore.LIGHTBLACK_EX}{symbol:^{self.CELL_WIDTH}}{Style.RESET_ALL}'
        return f'{color}{symbol:^{self.CELL_WIDTH}}{Style.RESET_ALL}'

    def display_board(self):
        """
        Визуализация игрового поля в консоли.
        Использует CELL_WIDTH для выравнивания и 'hybrid_sep' для создания
        эффекта сетки с нижним подчеркиванием ячеек.
        """
        # 1. Пустая линия для создания высоты ячейки
        empty_line = '|'.join(
            [f"{' ':{self.CELL_WIDTH}}" for _ in range(self.board_size)])
        # 2. Линия-разделитель (гибридная идея с нижним подчеркиванием)
        # Используется нижнее подчеркивание только ТАМ, где проходят границы
        # между клетками
        hybrid_sep = '|'.join(
            [f"{'_' * self.CELL_WIDTH}" for _ in range(self.board_size)])
        for i, row in enumerate(self.board):
            print(empty_line)
            formatted_row = [
                f'{self.get_colored_symbol(cell, i, j)}' for j, cell in enumerate(row)]
            print('|'.join(formatted_row))
            if i < self.board_size - 1:
                print(hybrid_sep)
            else:
                print(empty_line)

    def _is_draw(self):
        return all(' ' not in row for row in self.board)

    def _is_winner(self):
        """
        Проверка наличия выигрышной комбинации на поле.

        Метод анализирует все заранее сгенерированные линии (строки, столбцы, диагонали).
        Если находится линия, полностью заполненная символом текущего игрока,
        координаты этой линии сохраняются в self.winning_coords для последующей
        подсветки при отрисовке поля.
        """
        for combo in self.win_combinations:
            may_win = [self.board[r][c] for r, c in combo]
            if may_win.count('X') == self.board_size or may_win.count(
                    'O') == self.board_size:
                self.winning_coords = combo
                return True
        return False

    def _is_cell_occupied(self, row, col):
        return self.board[row][col] != ' '

    def _try_make_move(self, position):
        position = int(position)
        if not (1 <= position <= self.board_limit):
            raise InvalidPositionError(position, self.board_limit)
        row = (position - 1) // self.board_size
        col = (position - 1) % self.board_size
        if self._is_cell_occupied(row, col):
            raise CellOccupiedError(position, self.board[row][col])
        self.winner_count += 1
        self.board[row][col] = self.current_player

    def _validate_move(self, pos_str):
        if not pos_str.isdigit():
            raise InvalidInputError(pos_str)

    def show_current_player(self):
        return (f'{Fore.RED}{'X'}{Style.RESET_ALL}' if self.current_player == 'X'
                else f'{Fore.GREEN}{'O'}{Style.RESET_ALL}')

    def _is_continue_game(self, result: str):
        if result == 'win':
            print(f'Игрок {self.show_current_player()} победил!')
            self._save_game_history(f'Победил {self.current_player}')
        else:
            print('Игра закончилась вничью!')
            self._save_game_history('Ничья')
        ask_replay = input('Хотите сыграть ещё раз? [Y\\n] ')
        if ask_replay.lower() in ['да', 'д', 'y', 'yes']:
            self.reset()
            self.reset_player = True
            return True
        print('Хорошего дня', '\U0001F917')
        return False

    def _save_game_history(self, result: str = None):
        mode = 'Бот' if self.is_play_bot is True else 'PVP'
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        # строка лога
        log_entry = (f"[{now}] Режим: {mode} | Поле: {self.board_size}x{self.board_size} | "
                     f"Количество ходов: {self.winner_count} | Итог: {result}\n")
        try:
            with open('tic_tac_toe_history.txt', 'a', encoding='utf-8') as file:
                file.write(log_entry)
        except OSError as e:
            print(f"Произошла системная ошибка при работе с файлом: {e}")

    def _message_mode(self, mode):
        print('Начата игра против бота. Вы ходите первым') if mode\
            else print('Начата игра в режиме PVP')
        
    def _mode_selection(self):
        print(
            'Чтобы выйти из игры ДО её завершения нажмите ENTER (пустой ввод)')
        ask_play_with_bot = input('Хотите сыграть проти бота?[Y\\n] ')
        self.is_play_bot = (True if ask_play_with_bot in
                            ['y', 'yes', 'д', 'да'] else False)
        

    def pvp_mode(self):
        self.display_board()
        print(f'Ходит игрок: {self.show_current_player()}')
        self.pos_str = input(f'Введите ячейку 1 - {self.board_limit}: ')

    def bot_mode(self):
        # Логика игры против бота
        if self.change_bot_play == 'player':
            self.display_board()
            print(f'Ваш ход {self.show_current_player()}')
            self.pos_str = input(
                f'Введите ячейку 1 - {self.board_limit}: ')
        elif self.change_bot_play == 'bot':
            move_bot = self._get_ai_move()
            self.pos_str = str(
                move_bot[0] * self.board_size + move_bot[1] + 1)
            print(f'Бот сделал ход, теперь ваша очередь')

    def _is_stop_game(self):
        if not self.pos_str:
            return True

    def play(self):
        """
        Основной игровой цикл.
        Управляет логикой ходов, переключением между игроком и ботом,
        а также обрабатывает прерывание игры пользователем (через ENTER).
        """
        while True:
            try:
                if self.is_play_bot is None:
                    self._mode_selection()

                if self.winner_count == 0:
                    self._message_mode(self.is_play_bot)

                self.bot_mode() if self.is_play_bot else self.pvp_mode()
                if self._is_stop_game():
                    print('Вы досрочно завершили игру')
                    return
                self._validate_move(self.pos_str)
                self._try_make_move(self.pos_str)
                if self._is_winner():
                    self.display_board()
                    if not self._is_continue_game('win'):
                        return
                elif self._is_draw():
                    self.display_board()
                    if not self._is_continue_game('draw'):
                        return
                self._switch_player()

            except TicTacToeError as e:
                print(e)

    def _switch_player(self):
        if self.is_play_bot is not None and self.reset_player is False:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        if self.is_play_bot and self.reset_player is False:
            self.change_bot_play = 'player' if self.change_bot_play == 'bot' else 'bot'
        if self.reset_player:
            self.reset_player = False
            
            

    def _get_ai_move(self):
        """
        Алгоритм принятия решения искусственным интеллектом (ботом).

        Логика бота строится на системе приоритетов:
        1. Атака: Если до победы остался один ход, бот ставит символ в пустую ячейку линии.
        2. Защита: Если игрок может победить следующим ходом, бот блокирует эту возможность.
        3. Центр: Если центр поля свободен, бот занимает его (стратегическое преимущество).
        4. Случайный ход: Если приоритетные варианты отсутствуют, выбирается любая свободная ячейка.
        """
        def find_empty_in_line(symbol, target_count):
            for combo in self.win_combinations:
                line_values = [self.board[r][c] for r, c in combo]
                if line_values.count(
                        symbol) == target_count and line_values.count(' ') == 1:

                    empty_idx = line_values.index(' ')
                    return combo[empty_idx]
            return None
        move = find_empty_in_line('O', self.board_size - 1)
        if move:
            return move

        move = find_empty_in_line('X', self.board_size - 1)
        if move:
            return move

        center = self.board_size // 2
        if self.board[center][center] == ' ':
            return (center, center)

        empty_cells = [(r, c) for r in range(self.board_size)
                       for c in range(self.board_size) if self.board[r][c] == ' ']
        return choice(empty_cells) if empty_cells else None





# if __name__ == "__main__":
#     game = TicTacToe()
#     game.play()
