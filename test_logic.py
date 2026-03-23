from tictactoe_library import TicTacToe
game = TicTacToe(3)

assert game._is_winner() is False, 'Метод нашел победу на пустом поле!'

game.board[0][0] = 'X'
assert game._is_cell_occupied(0, 0), 'Ошибка: занятая клетка считается пустой'
assert not game._is_cell_occupied(1, 1), 'Ошибка: пустая клетка считается занятой'
game.reset()

win_row = [(0, 0),(0, 1),(0, 2)]
for r, c in win_row:
    game.board[r][c] = 'X'
assert game._is_winner(), f'Ошибка: не распознана победа по горизонтали {win_row}'
game.reset()

win_diagonal = [(0, 2), (1, 1), (2, 0)]
for r, c in win_diagonal:
    game.board[r][c] = 'X'
assert game._is_winner(), f'Ошибка: не распознана выигрышная диагональ {win_diagonal}'
game.reset()

garbage_coords = [(0,0), (0,1), (1,2)]
for r, c in garbage_coords:
    game.board[r][c] = 'X'
assert not game._is_winner(), f'Ошибка: распознана победа с не выигрышной комбинацией {garbage_coords}'
game.reset()

assert len(game.win_combinations) == 8, 'Выигрышных комбинаций при поле 3x3 должно быть 8'

for i in range(3):
    for j in range(3):
        game.board[i][j] = 'X'
assert game._is_draw(), 'Ошибка: метод проверки на ничью не вернул True при всех занятых клетках'
game.reset()

print('✅ Все тесты показали что код полностью работоспособный! ✅')

