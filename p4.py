from datetime import datetime
from colorama import Fore, Style
from os import path, remove
import re
from random import choice


class TicTacToe:
    CELL_WIDTH = 5  # ширина ячеек по ГОСТу

    def __init__(self, board_size: int = 3):
        """
        Инициализация игры. 
        board_size: определяет сторону квадрата(игрового поля) (например, 3x3).
        Здесь мы сразу генерируем все выигрышные комбинации, чтобы не вычислять их во время игры.
        """
        if not isinstance(board_size, int):
            raise TypeError(
                'Размер игрового поля должен быть цифрой от 2 до 9')
        if not (2 <= board_size <= 9):
            raise ValueError('Значение игрового поля должно быть от 2 до 9')
        self.board_size = board_size
        self.board_limit = board_size * board_size
        self.win_combinations = self._generate_win_combinations()
        self.reset()

    def __str__(self):
        '''Возвращает краткое состояние текущей игровой сессии.'''
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
        self.current_player = 'X'
        self.board = [[' ' for _ in range(self.board_size)]
                      for _ in range(self.board_size)]
        self.winning_coords = []
        self.board_limit = self.board_size * self.board_size
        self.winner_count = 0
        self.change_bot_play = 'player'
        self.is_play_bot = False

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
        # Мы используем нижнее подчеркивание только ТАМ, где проходят границы
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
            raise ValueError(
                f'Число {position} вне диапазона, диапазон: 1-{self.board_limit}')
        row = (position - 1) // self.board_size
        col = (position - 1) % self.board_size
        if self._is_cell_occupied(row, col):
            raise ValueError('Ячейка занята, выберите другую')
        self.winner_count += 1
        self.board[row][col] = self.current_player

    def _validate_move(self, pos_str):
        if not pos_str.isdigit():
            raise ValueError('Некорректный ввод, попробуйте ещё раз')

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
            with open("tic_tac_toe_history.txt", "a", encoding="utf-8") as file:
                file.write(log_entry)
        except OSError as e:
            print(f"Произошла системная ошибка при работе с файлом: {e}")

    def play(self):
        """
        Основной игровой цикл. 
        Управляет логикой ходов, переключением между игроком и ботом, 
        а также обрабатывает прерывание игры пользователем (через ENTER).
        """
        while True:
            try:
                if self.is_play_bot is False:
                    print(
                        'Чтобы выйти из игры ДО её завершения нажмите ENTER (пустой ввод)')
                    ask_play_with_bot = input(
                        'Хотите сыграть проти бота?[Y\\n] ')
                    if ask_play_with_bot.lower() in ['y', 'yes', 'д', 'да']:
                        self.is_play_bot = True
                        print('Начата игра против бота. Вы ходите первым')
                    else:
                        self.is_play_bot = None
                # Логика игры против бота
                if self.is_play_bot:
                    if self.change_bot_play == 'bot':
                        move_bot = self._get_ai_move()
                        pos_str = str(
                            move_bot[0] * self.board_size + move_bot[1] + 1)
                        print(f'Бот сделал ход, теперь ваша очередь')
                    elif self.change_bot_play == 'player':
                        self.display_board()
                        print(f'Ваш ход {self.show_current_player()}')
                        pos_str = input(
                            f'Введите ячейку 1 - {self.board_limit}: ')
                # Логика игры против человек
                elif not self.is_play_bot:
                    self.display_board()
                    print(f'Ходит игрок: {self.show_current_player()}')
                    pos_str = input(f'Введите ячейку 1 - {self.board_limit}: ')
                if not pos_str:
                    return print('Игра прервана')
                self._validate_move(pos_str)
                self._try_make_move(pos_str)
                if self._is_winner():
                    self.display_board()
                    if not self._is_continue_game('win'):
                        return
                elif self._is_draw():
                    self.display_board()
                    if not self._is_continue_game('draw'):
                        return
                elif self.is_play_bot:
                    # Переключение очередности хода для бота и игрока
                    self.change_bot_play = 'player' if self.change_bot_play == 'bot' else 'bot'
                    self.current_player = 'O' if self.current_player == 'X' else 'X'
                elif not self.is_play_bot:
                    # Смена текущего игрока в режиме PVP
                    self.current_player = 'O' if self.current_player == 'X' else 'X'
            except ValueError as e:
                print(e)

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

    def game_history(self, action: int | str | None = None):
        """
        Интерфейс управления историей матчей.

        Аргументы:
            action:
            - 1 / 'show_match_story': Показать весь лог игр.
            - 2 / 'show_draws': Показать только ничьи.
            - 3 / 'show_stats': Общая статистика побед X и O.
            - 25 / 'remove_story': Удалить файл истории.
            - 'show_win_[X/O]': Победы конкретного игрока (например, show_win_X).
            - 'show_last_matches_[N]': Показать последние N игр.

            АНАЛИТИКА (через 'show_advanced_'):
            - 'show_advanced_pvp_stats': Винрейт в режиме PVP.
            - 'show_advanced_ai_stats': Винрейт в режиме против бота.
            - 'show_advanced_sum_moves': Суммарное количество ходов за все игры.
            - 'show_advanced_sum_boards': Суммарная площадь игровых полей.
            - 'show_advanced_fastest_game': Информация о самой короткой игре.
            - 'show_advanced_data_[ДД.ММ.ГГГГ]': Поиск игр по конкретной дате.
        """
        if action is None:
            print(self.game_history.__doc__)
            return
        elif not path.isfile('tic_tac_toe_history.txt'):
            print('Файл с историей игры не создан. Сыграйте чтобы его создать',)
            return

        with open('tic_tac_toe_history.txt', 'r', encoding='UTF-8') as f:
            lines = [line.strip() for line in f]

        if action == 1 or action == 'show_match_story':
            print('--- История игр ---')
            for one_party in lines:
                print(one_party)

        elif action == 2 or action == 'show_draws':
            print('--- История игр в ничью ---')
            for one_party in lines:
                if 'Ничья' in one_party:
                    print(one_party)

        elif action == 25 or action == 'remove_story':
            remove('tic_tac_toe_history.txt')
            print('Файл с историей игр успешно удалён')

        elif action == 'show_stats' or action == 3:
            win_X, win_O, draws = 0, 0, 0
            for one_party in lines:
                # True + 1, False + 0
                win_X += one_party.endswith('X')
                win_O += one_party.endswith('O')
                draws += one_party.endswith('Ничья')
            print(f'Количество побед игрока X: [{win_X}]\n'
                  f'Количество побед игрока O: [{win_O}]\n'
                  f'Количество игр в ничью: [{draws}]')
        elif action.startswith('show_win_'):
            target = action.replace('show_win_', '').upper()
            if target in ['X', 'O']:
                print(f'--- Победы игрока {target} ---')
                for one_party in lines:
                    if one_party.endswith(target):
                        print(one_party)
            else:
                print('Такого игрока нет. Введите X или O')

        elif action.startswith('show_last_matches'):
            raw_val = action.replace('show_last_matches', '').lstrip('_')
            # Определение количества игр N для вывода (по умолчанию 5)
            if not raw_val:
                target = 5
            elif raw_val.isdigit():
                target = int(raw_val)
            else:
                print('Введите число последних игр!')
                return

            if target is None or not (1 <= target <= 40):
                print('Введите диапазон игр от 1 до 40 включительно')
                return

            sum_of_games = min(target, len(lines))
            if sum_of_games == 0:
                print('История игр пока пуста.')
                return

            last_word = 'игры' if sum_of_games < 5 else 'игр'
            # Срез для получения последних игр
            last_games = lines[-1:-sum_of_games - 1: -1]
            (print(f'--- Последние {sum_of_games} {last_word} ---') if sum_of_games > 1
             else print('--- Последняя игра ---'))
            for one_party in last_games:
                print(one_party)

        elif action.startswith('show_advanced_'):
            data = self._extract_history(lines)
            target = action.replace('show_advanced_', '').lower()
            if not data:
                print("История пуста или формат логов не распознан.")
                return

            if target == 'sum_moves':
                print(
                    f'Общее кол-во ходов: {sum(line["moves"] for line in data)}')
            elif target == 'sum_boards':
                print(
                    f'Общая площадь всех полей: {sum(line['size'] for line in data)}')

            elif target in ['pvp_stats', 'ai_stats']:
                def chance_calc_f(a, c): return f'{(100 / a * c):.1f}%'
                mode_name = 'Бот' if target == 'ai_stats' else 'PVP'
                # Фильтруем данные из распарсенных словарей по режиму и результату
                win_x = sum(
                    1 for line in data if line['mode'] == mode_name and line['winner'] == 'X')
                win_o = sum(
                    1 for line in data if line['mode'] == mode_name and line['winner'] == 'O')
                draws = sum(
                    1 for line in data if line['mode'] == mode_name and line['draw'])
                total_games = win_x + win_o + draws
                if total_games == 0:
                    return print(f"Статистика для режима {mode_name} пока отсутствует.")
                # подсчёт винрейта с использованием функции chance_calc_f с готовым форматированием
                win_x = chance_calc_f(total_games, win_x)
                win_o = chance_calc_f(total_games, win_o)
                draws = chance_calc_f(total_games, draws)
                print((f'Процент побед | mode PVP | X: {win_x} | O: {win_o} | Ничья: {draws}') if target == 'pvp_stats'
                      else f'Процент побед | mode Бот | Игрок(X) {win_x} | Бот(O) {win_o} | Ничья {draws}')
            elif target == 'fastest_game':
                record = min(data, key=lambda x: x['moves'])
                print(
                    f'Наименьшее кол-во ходов. Дата: {record["date"]}. Всего {record["moves"]} ходов')

            elif target.startswith('data_'):
                target = target.replace('data_', '')
                # Поиск игр, где дата лога начинается с искомой даты (ДД.ММ.ГГГГ)
                result = [
                    line for line in data if line['date'].startswith(target)]
                if not result:
                    print(f'За дату {target} игр не найдено.')
                else:
                    print(f'{"-"*10} Все игры за дату {target} {"-"*10}')
                    for res in result:
                        outcome = f"Победил {res['winner']}" if res['winner'] else "Ничья"

                        print(f"[{res['date']}] Режим: {res['mode']} | "
                              f"Поле: {res['size']} | Ходов: {res['moves']} | Итог: {outcome}")

    def _extract_history(self, lines):
        """
        Парсинг текстового лога с помощью регулярных выражений.
        Использует именованные группы (date, mode, size и т.д.) для 
        преобразования строк файла в структурированные словари Python.
        """
        pattern = re.compile(r'''
    \[(?P<date>.*?)\]
    \s+Режим: \s+(?P<mode>Бот|PVP)\s+ \|
    \s+ Поле: \s+ (?P<size>\d+x\d+)
    \s+ \| \s+ Количество\s+ходов:\s+ (?P<moves>\d+)
    \s+ \| \s+ Итог: \s+ (Победил\s+ (?P<winner>[XO])|(?P<draw>Ничья))
    ''', re.VERBOSE)
        data = [m.groupdict() for line in lines if (m := pattern.search(line))]
        for entry in data:
            entry['size'] = int(entry['size'][0]) * int(entry['size'][2])
            entry['moves'] = int(entry['moves'])
        return data


if __name__ == "__main__":
    game = TicTacToe()
    game.play()
