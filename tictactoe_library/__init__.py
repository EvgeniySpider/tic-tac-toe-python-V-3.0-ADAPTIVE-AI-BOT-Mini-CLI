"""
Библиотека TicTacToe: игра "Крестики-нолики" и инструменты аналитики.

Пакет предоставляет интерфейс для запуска игры в различных режимах (PVP, против бота)
и вложенное пространство имен 'log' для работы с историей сыгранных матчей,
просмотра статистики и расчета винрейта.
"""

from .exceptions import *
from .game import TicTacToe
from .analytics import *


def play():
    """Быстрый запуск игры."""
    game = TicTacToe()
    game.play()


def play_bot():
    '''Запуск игры с ботом'''
    game = TicTacToe(mode=True)
    game.play()


def play_pvp():
    '''Запуск игры друг с другом'''
    game = TicTacToe(mode=False)
    game.play()


class LogNamespace:
    """Вспомогательный класс для группировки функций аналитики."""

    @staticmethod
    def show_history():
        """Показать полную историю игр."""
        GameHistoryManager().show_match_story

    @staticmethod
    def show_draws():
        """Показать только ничьи."""
        GameHistoryManager().show_draws

    @staticmethod
    def show_stats():
        """Показать общую статистику по режимам."""
        GameHistoryManager().show_stats

    @staticmethod
    def show_sum_moves():
        """Показать общее количество ходов."""
        GameHistoryManager().sum_moves

    @staticmethod
    def show_sum_boards():
        """Показать суммарную площадь всех полей."""
        GameHistoryManager().sum_boards

    @staticmethod
    def show_fastest():
        """Показать самую быструю игру."""
        GameHistoryManager().fastest_game

    @staticmethod
    def show_win(char=None):
        """Показать победы конкретного игрока (X/O)."""
        GameHistoryManager().win(char)

    @staticmethod
    def show_last_games(n=None):
        """Показать последние N игр."""
        GameHistoryManager().last_matches(n)

    @staticmethod
    def show_winrate(target=None):
        """Показать винрейт для режима (bot/pvp)."""
        GameHistoryManager().winrate(target)

    @staticmethod
    def show_by_date(target=None):
        """Найти игры по дате (ДД.ММ.ГГГГ)."""
        GameHistoryManager().date(target)

    @staticmethod
    def delete(confirm=None):
        """Удалить файл истории игр."""
        GameHistoryManager().remove_story(confirm)


log = LogNamespace()
