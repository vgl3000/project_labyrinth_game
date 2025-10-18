#!/usr/bin/env python3
from labyrinth_game.constants import ROOMS
from labyrinth_game.utils import describe_current_room, show_help, solve_puzzle, attempt_open_treasure
from .player_actions import get_input, show_inventory, move_player, take_item, use_item


def process_command(game_state, command_line):
    if not command_line:
        return

    parts = command_line.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

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
            print("Укажите направление: go north, go south и т.д.")
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
        current = game_state['current_room']
        if current == 'treasure_room' and 'treasure_chest' in ROOMS['treasure_room']['items']:
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

