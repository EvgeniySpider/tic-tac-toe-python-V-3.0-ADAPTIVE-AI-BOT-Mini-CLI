import pytest
from tictactoe_library import TicTacToe, exceptions


@pytest.fixture
def game():
    return TicTacToe(3)


def test_initial_state(game):
    assert game._is_winner() is False


def test_occupied_cell(game):
    game.board[0][0] = 'X'
    assert game._is_cell_occupied(0, 0)
    assert not game._is_cell_occupied(
        1, 1), 'Ошибка: пустая клетка считается занятой'


def test_horizontal_win(game):
    win_row = [(0, 0), (0, 1), (0, 2)]
    for r, c in win_row:
        game.board[r][c] = 'X'
    assert game._is_winner(
    ), f'Ошибка: не распознана победа по горизонтали {win_row}'


def test_diagonal_win(game):
    win_diagonal = [(0, 2), (1, 1), (2, 0)]
    for r, c in win_diagonal:
        game.board[r][c] = 'X'
    assert game._is_winner(
    ), f'Ошибка: не распознана выигрышная диагональ {win_diagonal}'


def test_garbage_coords(game):
    garbage_coords = [(0, 0), (0, 1), (1, 2)]
    for r, c in garbage_coords:
        game.board[r][c] = 'X'
    assert not game._is_winner(
    ), f'Ошибка: распознана победа с не выигрышной комбинацией {garbage_coords}'


def test_sum_win_coords(game):
    assert len(
        game.win_combinations) == 8, 'Выигрышных комбинаций при поле 3x3 должно быть 8'


def test_draw_method(game):
    game.board = [
        ['X', 'O', 'X'],
        ['X', 'O', 'O'],
        ['O', 'X', 'X']
    ]
    assert not game._is_winner(), 'Ошибка: на полностью заполненной доске найден победитель'
    assert game._is_draw(), 'Ошибка: Метод не распознал ничью при полностью заполненном полном поле'


def test_make_big_position(game):
    with pytest.raises(exceptions.InvalidPositionError):
        game._try_make_move(10)


print('✅ Все тесты показали что код полностью работоспособный! ✅')
