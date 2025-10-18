# labyrinth_game/player_actions.py
from .constants import ROOMS


def get_input(prompt="> "):
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def show_inventory(game_state):
    inv = game_state['player_inventory']
    if inv:
        print("Ваш инвентарь:", ", ".join(inv))
    else:
        print("Ваш инвентарь пуст.")


def move_player(game_state: dict, direction: str) -> None:
    """
    Перемещает игрока в указанном направлении, если выход существует.

    При попытке войти в treasure_room без rusty_key — доступ запрещён.
    После успешного перемещения вызывается случайное событие.

    Args:
        game_state (dict): Словарь с состоянием игры, содержит:
            - 'current_room' (str)
            - 'steps_taken' (int)
        direction (str): Направление движения (например, 'north')
    """
    current = game_state['current_room']
    exits = ROOMS[current]['exits']

    if direction not in exits:
        print("Нельзя пойти в этом направлении.")
        return

    next_room = exits[direction]

    if next_room == 'treasure_room':
        if 'rusty_key' in game_state['player_inventory']:
            print("Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ.")
        else:
            print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
            return

    game_state['current_room'] = next_room
    game_state['steps_taken'] += 1

    from .utils import describe_current_room, random_event
    describe_current_room(game_state)
    random_event(game_state)


def take_item(game_state, item_name):
    current = game_state['current_room']
    room_items = ROOMS[current]['items']

    if item_name == 'treasure_chest':
        print("Вы не можете поднять сундук, он слишком тяжелый.")
        return

    if item_name in room_items:
        room_items.remove(item_name)
        game_state['player_inventory'].append(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")


def use_item(game_state, item_name):
    inv = game_state['player_inventory']
    if item_name not in inv:
        print("У вас нет такого предмета.")
        return

    if item_name == 'torch':
        print("Вы зажгли факел. Стало светлее!")
    elif item_name == 'sword':
        print("Вы сжали меч в руке. Чувствуете себя увереннее.")
    elif item_name == 'bronze_box':
        if 'rusty_key' not in inv:
            inv.append('rusty_key')
            print("Вы открыли бронзовую шкатулку и нашли внутри ржавый ключ!")
        else:
            print("Шкатулка пуста.")
    elif item_name == 'ancient_book':
        print("Вы листаете древнюю книгу. Ничего полезного не нашли.")
    else:
        print(f"Вы не знаете, как использовать {item_name}.")

