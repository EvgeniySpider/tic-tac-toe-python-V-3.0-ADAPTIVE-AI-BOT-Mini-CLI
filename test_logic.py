import pytest
from pathlib import Path

from tictactoe_library import TicTacToe, exceptions


@pytest.fixture
def game() -> TicTacToe:
    return TicTacToe(board_size=3)


@pytest.mark.parametrize('board_size', [3, 4, 5])
def test_board_size_combinations(board_size: int):
    # Создаём новый экземпляр игры под нужный размер
    test_game = TicTacToe(board_size=board_size)

    expected_combos: int = test_game.board_size * 2 + 2
    assert len(test_game.win_combinations) == expected_combos


@pytest.mark.parametrize(
    "board_setup, expected_move",
    [
        ([(0, 0), (0, 1)], (0, 2)),
        ([(1, 0), (1, 1)], (1, 2)),
        ([(2, 0), (2, 1)], (2, 2)),
    ]
)
def test_ai_wins_immediately(
    game: TicTacToe,
    board_setup: list[tuple[int, int]],
    expected_move: tuple[int, int]
):
    for r, c in board_setup:
        game.board[r][c] = 'O'

    assert game._get_ai_move() == expected_move


board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]


@pytest.mark.parametrize('board_setup, expected_move',
                         [
                             ([(0, 0), (1, 0)], '7'),
                             ([(0, 2), (2, 2)], '6'),
                         ]
                         )
def test_ai_blocks_player_win(
    board_setup: list[tuple[int, int]],
    expected_move: str
):
    game = TicTacToe(board_size=3, mode='Бот')
    game.change_bot_play = 'bot'

    for r, c in board_setup:
        game.board[r][c] = 'X'

    game.bot_mode()
    assert game.pos_str == expected_move


@pytest.mark.parametrize('invalid_input', ('abc', '', '1.5', '-5', ' '))
def test_validate_move_invalid_input(game: TicTacToe, invalid_input: str):
    with pytest.raises(exceptions.InvalidInputError):
        game._validate_move(invalid_input)


@pytest.mark.parametrize('invalid_input', (0, 10, 99))
def test_try_make_move_invalid_position(game: TicTacToe, invalid_input: int):
    with pytest.raises(exceptions.InvalidPositionError):
        game._try_make_move(invalid_input)


def test_display_board_output(game: TicTacToe, capsys: pytest.CaptureFixture[str]):
    game.display_board()
    # Перехватываем всё, что напечаталось в консоль
    captured = capsys.readouterr()
    # Проверяем, что в выводе есть разделители
    assert "|" in captured.out


@pytest.mark.parametrize("invalid_size", [1, 10, 100])
def test_invalid_board_size_raises_error(invalid_size: int):
    with pytest.raises(exceptions.BoardSizeValueError, match=str(invalid_size)):
        TicTacToe(board_size=invalid_size)


def test_save_game_history(
    game: TicTacToe,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
):
    # 1. Перенаправляем работу с файлами во временную директорию tmp_path
    monkeypatch.chdir(tmp_path)

    # 2. Вызываем метод сохранения
    game._save_game_history("Победил X")

    # 3. Находим файл во временной папке
    history_file = tmp_path / "tic_tac_toe_history.txt"

    # 4. Проверяем, что файл действительно создался
    assert history_file.exists()

    # 5. Читаем содержимое и проверяем нужную подстроку
    content = history_file.read_text(encoding="utf-8")
    assert "Победил X" in content
    assert "Режим: PVP" in content


def test_switch_player_pvp(game: TicTacToe):
    game.is_play_bot = False
    assert game.current_player == 'X'

    game._switch_player()
    assert game.current_player == 'O'

    game._switch_player()
    assert game.current_player == 'X'


def test_switch_player_bot_mode(game: TicTacToe):
    assert game.change_bot_play == 'player'
    game.is_play_bot = True

    game._switch_player()
    assert game.current_player == 'O'
    assert game.change_bot_play == 'bot'


def test_reset_game_state(game: TicTacToe):
    for rс in range(game.board_size):
        game.board[rс][rс] = 'X'
    game.winner_count = game.board_size
    game.current_player = 'O'

    game.reset()
    for rс in range(game.board_size):
        assert game.board[rс][rс] == ' '
    assert game.current_player == 'X'
    assert game.winner_count == 0


@pytest.mark.parametrize("win_combo", TicTacToe(3).win_combinations)
def test_all_win_combinations(game: TicTacToe, win_combo: list[tuple[int, int]]):
    for r, c in win_combo:
        game.board[r][c] = 'X'

    assert game._is_winner() is True


def test_no_winner_on_incomplete_line(game: TicTacToe):
    for rc in range(game.board_size - 1):
        game.board[rc][rc] = 'X'

    assert game._is_winner() is False


def test_is_draw_dynamic(game: TicTacToe):
    # Заполняем поле чередующимися символами X и O (шахматка)
    for r in range(game.board_size):
        for c in range(game.board_size):
            game.board[r][c] = 'X' if (r + c) % 2 == 0 else 'O'

    assert game._is_draw() is True


def test_is_not_draw_when_empty_cells_exist(game: TicTacToe):
    # Заполняем всё крестиками
    for r in range(game.board_size):
        for c in range(game.board_size):
            game.board[r][c] = 'X'

    # Освобождаем ровно одну ячейку
    game.board[0][0] = ' '

    assert game._is_draw() is False


def test_ai_prefers_center_when_no_threat(game: TicTacToe):
    move = game._get_ai_move()
    assert move == (1, 1)


def test_ai_makes_random_move_when_center_taken(game: TicTacToe):
    game.board[1][1] = 'X'
    move = game._get_ai_move()

    assert move is not None
    r, c = move
    assert game.board[r][c] == ' '


def test_full_game_pvp_x_wins(
    game: TicTacToe,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
):
    # 1. Настраиваем режим игры
    game.is_play_bot = False
    game.mode = 'PVP'

    # 2. Подготавливаем очередь команд пользователей
    user_inputs = iter(["1", "4", "2", "5", "3", "n"])

    # 3. Подменяем builtins.input лямбдой, которая вызывает next()
    monkeypatch.setattr('builtins.input', lambda _: next(user_inputs))

    # 4. Запускаем игровой цикл (теперь input() берет значения из user_inputs)
    game.play()

    # 5. Перехватываем вывод консоли
    captured = capsys.readouterr()

    # 6. Проверяем результаты
    assert "Победил" in captured.out or "X" in captured.out
    assert game.board[0] == ['X', 'X', 'X']


def test_try_make_move_cell_occupied(game: TicTacToe):
    game.board[0][0] = 'X'
    with pytest.raises(exceptions.CellOccupiedError):
        game._try_make_move(1)


def test_invalid_board_size_type():
    with pytest.raises(exceptions.BoardSizeTypeError):
        TicTacToe(3.5)


def test_play_early_exit(
    game: TicTacToe,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
):
    monkeypatch.setattr('builtins.input', lambda _: '')
    game.play()

    captured = capsys.readouterr()
    assert 'досрочно завершили' in captured.out
