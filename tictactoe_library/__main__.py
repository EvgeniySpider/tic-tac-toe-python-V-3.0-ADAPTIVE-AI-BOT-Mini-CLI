"""
Точка входа для запуска пакета tictactoe_library как скрипта.

Позволяет запускать игру напрямую из терминала командой:
python -m tictactoe_library
"""

from . import play

# Этот файл сработает, когда напишешь: python -m tictactoe_library
if __name__ == "__main__":
    play()
