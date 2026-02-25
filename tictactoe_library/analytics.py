from os import path, remove
import re
from .exceptions import InvalidConfigurationError


class GameHistoryManager:
    """
    Класс для анализа и управления историей игр TicTacToe.
    Обеспечивает чтение лог-файла, структурирование данных и
    предоставление различной статистики (винрейт, история, поиск по дате).
    """

    def __init__(self):
        """Инициализация менеджера: проверка файла, чтение строк и парсинг данных."""
        self.log_name = 'tic_tac_toe_history.txt'
        if not path.isfile('tic_tac_toe_history.txt'):
            raise InvalidConfigurationError(
                f'Файл {self.log_name} не найден. Сыграйте хотя бы раз!'
            )
        try:
            with open(self.log_name, 'r', encoding='UTF-8') as f:
                self.lines = [line.strip() for line in f if line.strip()]
        except OSError as e:
            raise InvalidConfigurationError(
                f'Ошибка доступа к файлу: {e}') from e
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
        data = [m.groupdict()
                for line in self.lines if (m := pattern.search(line))]
        for entry in data:
            entry['size'] = int(entry['size'][0]) * int(entry['size'][2])
            entry['moves'] = int(entry['moves'])
        self.parsed_data = data

    @property
    def show_match_story(self):
        """Выводит полную историю матчей в консоль."""
        print('--- История игр ---')
        for one_party in self.lines:
            print(one_party)

    @property
    def show_draws(self):
        """Отображение только тех игр, которые закончились ничьей."""
        print('--- История игр в ничью ---')
        for one_party in self.lines:
            if 'Ничья' in one_party:
                print(one_party)

    def remove_story(self, confirm=False):
        """Безопасное удаление файла истории с запросом подтверждения у пользователя."""
        if confirm is False or confirm != 'delete':
            print('Если вы уверены что хотите удалить файл с логами, '
                  'введите "delete"')
        elif confirm == 'delete':
            remove('tic_tac_toe_history.txt')
            print('Файл с историей игр успешно удалён')

    def _count_results(self, mode, winner, key='winner'):
        """Вспомогательный метод для подсчета количества матчей по заданным критериям."""
        return sum(1 for line in self.parsed_data
                   if line['mode'] == mode and line[key] == winner)

    @property
    def show_stats(self):
        """Краткая сводка: статистика побед и ничьих с разделением по режимам."""
        win_x_pvp = self._count_results('PVP', 'X')
        win_x_bot = self._count_results('Бот', 'X')
        win_o_pvp = self._count_results('PVP', 'O')
        win_o_bot = self._count_results('Бот', 'O')

        draws_pvp = self._count_results('PVP', 'Ничья', 'draw')
        draws_bot = self._count_results('Бот', 'Ничья', 'draw')

        total_x_win = win_x_pvp + win_x_bot
        total_o_win = win_o_pvp + win_o_bot
        total_draws = draws_pvp + draws_bot
        total_matches = total_x_win + total_o_win + total_draws
        print('----- Статистика побед и ничьих -----')
        print(f'Количество побед X | Режим PVP {win_x_pvp} | '
              f'Режим Бот {win_x_bot} | Всего {total_x_win}')
        print(f'Количество побед O | Режим PVP {win_o_pvp} | '
              f'Режим Бот {win_o_bot} | Всего {total_o_win}')
        print(f'Количество игр в ничью | Режим PVP {draws_pvp} | '
              f'Режим Бот {draws_bot} | Всего {total_draws}')
        print(f'Общее количество матчей {total_matches}')

    def win(self, char=None):
        if char not in ['x', 'o', 'X', 'O']:
            print('Укажите игрока [X / O]')
            return

        print(f'--- Победы игрока {char} ---')
        for one_party in self.lines:
            if one_party.endswith(char.upper()):
                print(one_party)

    def last_matches(self, n = None):
        """Отображение последних N сыгранных матчей."""
        if not isinstance(n, int):
            print('Введите целое число от 1 до 40')
            return
        if not (1 <= n <= 40):
            print('Введите диапазон игр от 1 до 40 включительно')
            return

        sum_of_games = min(n, len(self.lines))
        if sum_of_games == 0:
            print('История игр пока пуста.')
            return

        last_word = 'игры' if sum_of_games < 5 else 'игр'
        # Срез для получения последних игр
        last_games = self.lines[-1:-sum_of_games - 1: -1]
        (print(f'--- Последние {sum_of_games} {last_word} ---') if sum_of_games > 1
         else print('--- Последняя игра ---'))
        for one_party in last_games:
            print(one_party)

    @property
    def sum_moves(self):
        """Подсчет общего количества совершенных ходов за всю историю игр."""
        print(
            f'Общее кол-во ходов: {sum(line["moves"] for line in self.parsed_data)}')

    @property
    def sum_boards(self):
        """Подсчет суммарной площади всех игровых полей."""
        print(
            f'Общая площадь всех полей: {sum(line["size"] for line in self.parsed_data)}')

    def winrate(self, target=None):
        """
        Расчет винрейта (процентного соотношения побед и ничьих)
        для конкретного режима игры ('pvp' или 'бот').
        """
        if target is None or target.lower() not in ['bot', 'pvp']:
            print('Укажите режим игры: [bot / pvp]')
            return
        target = target.lower()
        def chance_calc_f(a, c): return f'{(100 / a * c):.1f}%'

        mode_name = 'Бот' if target == 'bot' else 'PVP'

        win_x = self._count_results(mode_name, 'X')
        win_o = self._count_results(mode_name, 'O')
        draws = self._count_results(mode_name, 'Ничья')
        total_games = win_x + win_o + draws
        if total_games == 0:
            return print(
                f"Статистика для режима {mode_name} пока отсутствует.")

        win_x = chance_calc_f(total_games, win_x)
        win_o = chance_calc_f(total_games, win_o)
        draws = chance_calc_f(total_games, draws)
        print((f'Процент побед | mode: Bot | Игрок(X) {win_x} | Бот(O) {win_o} | Ничья: {draws}')
              if target == 'bot'
              else f'Процент побед | mode: PVP | Игрок(X) {win_x} |'
              f' Игрок(O) {win_o} | Ничья {draws}')

    @property
    def fastest_game(self):
        """Поиск и вывод информации о матче с минимальным количеством ходов."""
        record = min(self.parsed_data, key=lambda x: x['moves'])
        print(
            f'Наименьшее кол-во ходов. Дата: {record["date"]}. Всего {record["moves"]} ходов')

    def date(self, target=None):
        """Поиск и отображение всех матчей за конкретную дату (ДД.ММ.ГГГГ)."""
        if target is None:
            print('Укажите дату в формате ДД.ММ.ГГГГ')
            return
        result = [
            line for line in self.parsed_data if line['date'].startswith(target)]

        if not result:
            print(f'За дату {target} игр не найдено.')
        else:
            print(f'{"-" * 10} Все игры за дату {target} {"-" * 10}')
            for res in result:
                outcome = f"Победил {
                    res['winner']}" if res['winner'] else "Ничья"

                print(f"[{res['date']}] Режим: {res['mode']} | "
                      f"Поле: {res['size']} | Ходов: {res['moves']} | Итог: {outcome}")
