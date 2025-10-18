#!/usr/bin/env python3
from .constants import ROOMS, COMMANDS
from .utils import describe_current_room, show_help, solve_puzzle, attempt_open_treasure
from .player_actions import get_input, show_inventory, move_player, take_item, use_item

def process_command(game_state: dict, command_line: str) -> None:
    """
    Обрабатывает введённую пользователем команду и вызывает соответствующие функции.

    Поддерживает:
    - Односложные команды движения (north, south и т.д.)
    - Команды с аргументами (go, take, use)
    - Специальные команды (solve, inventory, look, help, quit)

    В treasure_room команда 'solve' вызывает attempt_open_treasure.

    Args:
        game_state (dict): Словарь с состоянием игры
        command_line (str): Полная строка ввода от пользователя
    """
    if not command_line:
        return

    parts = command_line.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ('north', 'south', 'east', 'west'):
        move_player(game_state, cmd)
        return

    if cmd == "quit" or cmd == "exit":
        game_state['game_over'] = True
        print("Спасибо за игру!")
    elif cmd == "look":
        describe_current_room(game_state)
    elif cmd == "inventory":
        show_inventory(game_state)
    elif cmd == "help":
        show_help()
    elif cmd == "go":
        if arg:
            move_player(game_state, arg)
        else:
            print("Укажите направление: go north и т.д.")
    elif cmd == "take":
        if arg:
            take_item(game_state, arg)
        else:
            print("Укажите предмет: take torch")
    elif cmd == "use":
        if arg:
            use_item(game_state, arg)
        else:
            print("Укажите предмет: use torch")
    elif cmd == "solve":
        if game_state['current_room'] == 'treasure_room':
            attempt_open_treasure(game_state)
        else:
            solve_puzzle(game_state)
    else:
        print("Неизвестная команда. Введите 'help' для справки.")


def main() -> None:
    game_state = {
        'player_inventory': [],
        'current_room': 'entrance',
        'game_over': False,
        'steps_taken': 0
    }

    print("Добро пожаловать в Лабиринт сокровищ!")
    describe_current_room(game_state)

    while not game_state['game_over']:
        command = get_input()
        process_command(game_state, command)


if __name__ == "__main__":
    main()

