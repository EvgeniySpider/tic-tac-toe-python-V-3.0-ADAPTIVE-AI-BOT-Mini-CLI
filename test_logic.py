"""
Модуль Unit-тестирования логики игры TicTacToe.

Использует фреймворк pytest для проверки:
- Состояний игрового поля (победа, ничья, занятость клеток).
- Валидации ходов и обработки исключений (InvalidPositionError, CellOccupiedError).
- Адаптивного поведения AI (приоритет центра, блокировка игрока, завершение игры).

Тесты изолированы с помощью фикстур, что гарантирует чистый экземпляр игры для каждого прогона.
"""
import pytest
from tictactoe_library import TicTacToe, exceptions


@pytest.fixture
def game() -> TicTacToe:
    return TicTacToe(3)


def test_initial_state(game: TicTacToe):
    assert game._is_winner() is False, \
        'Ошибка: победитель найден на пустой доске'


def test_occupied_cell(game: TicTacToe):
    game.board[0][0] = 'X'
    assert game._is_cell_occupied(0, 0)
    assert not game._is_cell_occupied(1, 1), \
        'Ошибка: пустая клетка считается занятой'


# Проверка всех горизонталей
@pytest.mark.parametrize("symbol", ["X", "O"])
@pytest.mark.parametrize("row_index", [0, 1, 2])
def test_all_horizontal_wins(game: TicTacToe, symbol: str, row_index: int):
    game.board[row_index] = [symbol, symbol, symbol]
    assert game._is_winner() is True


# Проверка всех вертикалей
@pytest.mark.parametrize("symbol", ["X", "O"])
@pytest.mark.parametrize("col_index", [0, 1, 2])
def test_all_vertical_wins(game: TicTacToe, symbol: str, col_index: int):
    for row in range(3):
        game.board[row][col_index] = symbol

    assert game._is_winner() is True


# Проверка всех диагоналей
@pytest.mark.parametrize("symbol", ["X", "O"])
@pytest.mark.parametrize("diagonal_type", ["main", "anti"])
def test_all_diagonal_wins(game: TicTacToe, symbol: str, diagonal_type: str):
    if diagonal_type == "main":
        coords = [(0, 0), (1, 1), (2, 2)]
    else:
        coords = [(0, 2), (1, 1), (2, 0)]

    for r, c in coords:
        game.board[r][c] = symbol

    assert game._is_winner() is True


@pytest.fixture
def custom_game(request: pytest.FixtureRequest) -> TicTacToe:
    size: int = getattr(request, "param", 3)
    return TicTacToe(board_size=size)


@pytest.mark.parametrize("custom_game", [3, 4, 5], indirect=True)
def test_board_size_combinations(custom_game: TicTacToe):
    # Для поля 3x3 комбинаций 8, для 4x4 — 10, для 5x5 — 12
    expected_combos: int = custom_game.board_size * 2 + 2
    assert len(custom_game.win_combinations) == expected_combos


def test_display_board_output(
    game: TicTacToe,
    capsys: pytest.CaptureFixture[str]
):
    game.display_board()
    # Перехватываем всё, что напечаталось в консоль
    captured = capsys.readouterr()
    # Проверяем, что в выводе есть разделители
    assert "|" in captured.out


def test_garbage_coords(game: TicTacToe):
    garbage_coords = [(0, 0), (0, 1), (1, 2)]
    for r, c in garbage_coords:
        game.board[r][c] = 'X'
    assert not game._is_winner(), \
        f'Ошибка: распознана победа с невыигрышной комбинацией {garbage_coords}'


def test_sum_win_coords(game: TicTacToe):
    assert len(game.win_combinations) == 8, \
        'Выигрышных комбинаций при поле 3x3 должно быть 8'


def test_draw_method(game: TicTacToe):
    game.board = [
        ['X', 'O', 'X'],
        ['X', 'O', 'O'],
        ['O', 'X', 'X']
    ]
    assert not game._is_winner(), \
        'Ошибка: на полностью заполненной доске найден победитель'
    assert game._is_draw(), \
        'Ошибка: Метод не распознал ничью при полностью заполненном полном поле'


@pytest.mark.parametrize("invalid_pos", [0, 10, 99])
def test_try_make_move_invalid_position(game: TicTacToe, invalid_pos: int):
    with pytest.raises(exceptions.InvalidPositionError):
        game._try_make_move(invalid_pos)


def test_ai_winning_move(game: TicTacToe):
    game.board[0][0], game.board[0][1] = 'X', 'X'
    game.board[1][0], game.board[1][1] = 'O', 'O'
    assert game._get_ai_move() == (1, 2), \
        'Бот не сделал решающий ход в последнюю клетку'


def test_ai_center_priority(game: TicTacToe):
    game.board[0][0] = 'X'
    assert game._get_ai_move() == (1, 1), 'Бот не занял центральную клетку'


def test_ai_blocking_move(game: TicTacToe):
    game.board[0][0] = 'X'
    game.board[0][1] = 'X'
    assert game._get_ai_move() == (0, 2), \
        'Бот не заблокировал выигрышный ход игрока'


@pytest.mark.parametrize("invalid_input", ["abc", "", "1.5", "-5", " "])
def test_validate_move_invalid_input(game: TicTacToe, invalid_input: str):
    with pytest.raises(exceptions.InvalidInputError):
        game._validate_move(invalid_input)
