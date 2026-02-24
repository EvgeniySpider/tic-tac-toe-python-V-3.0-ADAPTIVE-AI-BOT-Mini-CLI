from .exceptions import *
from .game import TicTacToe

def play():    
    """Быстрый запуск игры."""
    game = TicTacToe()
    game.play()

__all__ = ["TicTacToe", "play"]


def play_bot():
    game = TicTacToe(mode = True)
    game.play()

def play_pvp():
    game = TicTacToe(mode = False)
    game.play()