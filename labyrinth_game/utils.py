# labyrinth_game/utils.py
import math
from .constants import ROOMS, COMMANDS


def describe_current_room(game_state):
    room_name = game_state['current_room']
    room = ROOMS[room_name]
    print(f"\n== {room_name.upper()} ==")
    print(room['description'])

    if room['items']:
        print("Заметные предметы:", ", ".join(room['items']))
    else:
        print("Предметов здесь нет.")

    exits = list(room['exits'].keys())
    if exits:
        print("Выходы:", ", ".join(exits))
    else:
        print("Выходов нет.")

    if room['puzzle'] is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def show_help():
    print("\nДоступные команды:")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd:<16} - {desc}")


def solve_puzzle(game_state):
    room_name = game_state['current_room']
    room = ROOMS[room_name]

    if room['puzzle'] is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = room['puzzle']
    print(f"\n{question}")
    user_answer = input("Ваш ответ: ").strip().lower()

    # Альтернативные ответы
    correct_variants = {correct_answer.lower()}
    if correct_answer == '10':
        correct_variants.add('десять')

    if user_answer in correct_variants:
        print("Верно! Загадка решена.")
        room['puzzle'] = None

        # Награды
        if room_name == 'hall':
            if 'treasure_key' not in game_state['player_inventory']:
                game_state['player_inventory'].append('treasure_key')
                print("Вы получили сокровищный ключ!")
        elif room_name == 'trap_room':
            print("Плиты успокоились.")
        elif room_name == 'library':
            print("Свиток исчезает в дымке.")
    else:
        print("Неверно. Попробуйте снова.")
        # Ловушка при ошибке в trap_room
        if room_name == 'trap_room':
            trigger_trap(game_state)


def attempt_open_treasure(game_state):
    if game_state['current_room'] != 'treasure_room':
        print("Здесь нет сундука с сокровищами.")
        return

    if 'treasure_chest' not in ROOMS['treasure_room']['items']:
        print("Сундук уже открыт.")
        return

    if 'treasure_key' in game_state['player_inventory']:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        ROOMS['treasure_room']['items'].remove('treasure_chest')
        print("В сундуке сокровище! Вы победили!")
        game_state['game_over'] = True
        return

    # Нет ключа — пробуем код
    choice = input("Сундук заперт. Хотите попробовать ввести код? (да/нет): ").strip().lower()
    if choice in ('да', 'yes', 'y'):
        code = input("Введите код: ").strip()
        puzzle = ROOMS['treasure_room']['puzzle']
        if puzzle and code.lower() == puzzle[1].lower():
            print("Код верный! Сундук открывается с лязгом.")
            ROOMS['treasure_room']['items'].remove('treasure_chest')
            print("В сундуке сокровище! Вы победили!")
            game_state['game_over'] = True
        else:
            print("Неверный код. Сундук остаётся запертым.")
    else:
        print("Вы отступаете от сундука.")

def check_for_trap(game_state):
    """Проверяет, находится ли игрок в ловушке, и активирует её с псевдослучайным шансом."""
    room_name = game_state['current_room']
    room = ROOMS.get(room_name, {})

    if not room.get('trap', False):
        return  # Ловушки нет

    # Генерация "псевдослучайного" числа на основе состояния игры
    seed = hash((room_name, game_state['steps_taken'], tuple(sorted(game_state['player_inventory']))))
    # Используем math.sin для получения числа от -1 до 1 → преобразуем в [0, 100]
    trap_chance = abs(math.sin(seed)) * 100
    trap_threshold = 30  # 30% шанс сработать

    if trap_chance < trap_threshold:
        print("\n Вы наступили на ловушку! Потолок начинает опускаться!")
        print("Быстро решите задачу, или вас раздавит!")

        # Простая математическая задача
        a = abs(seed) % 10 + 1
        b = abs(seed) % 5 + 1
        correct = a * b
        print(f"Сколько будет {a} × {b}?")
        try:
            answer = input("Ваш ответ: ").strip()
            if answer.isdigit() and int(answer) == correct:
                print("Вы успели вовремя! Потолок остановился.")
            else:
                print("Неверно! Вас раздавило...")
                game_state['game_over'] = True
        except (KeyboardInterrupt, EOFError):
            print("\nВы не успели... Ловушка сработала.")
            game_state['game_over'] = True

def pseudo_random(seed: int, modulo: int) -> int:
    """Генерирует псевдослучайное число в диапазоне [0, modulo) без random."""
    if modulo <= 0:
        return 0
    x = math.sin(seed * 12.9898) * 43758.5453
    fractional = x - math.floor(x)
    return int(fractional * modulo) % modulo


def trigger_trap(game_state):
    """Активирует ловушку: удаляет случайный предмет или завершает игру."""
    print("\n Ловушка активирована! Пол стал дрожать...")
    inv = game_state['player_inventory']

    if inv:
        idx = pseudo_random(game_state['steps_taken'], len(inv))
        lost_item = inv.pop(idx)
        print(f"Вы потеряли предмет: {lost_item}!")
    else:
        danger_roll = pseudo_random(game_state['steps_taken'] + 100, 10)
        if danger_roll < 3:  # 30% шанс смерти
            print("Вы не успели увернуться... Ловушка убила вас!")
            game_state['game_over'] = True
        else:
            print("Вам удалось уцелеть!")


def random_event(game_state):
    """Генерирует редкое случайное событие после перемещения."""
    # 10% шанс события
    if pseudo_random(game_state['steps_taken'], 10) != 0:
        return

    event_type = pseudo_random(game_state['steps_taken'] + 50, 3)

    if event_type == 0:
        # Находка монетки
        current = game_state['current_room']
        if 'coin' not in ROOMS[current]['items']:
            ROOMS[current]['items'].append('coin')
        print("Вы заметили блестящую монетку на полу!")

    elif event_type == 1:
        # Испуг
        print("Вы слышите странный шорох в темноте...")
        if 'sword' in game_state['player_inventory']:
            print("Вы сжимаете меч — шорох прекратился.")

    elif event_type == 2:
        # Ловушка в trap_room без факела
        if (game_state['current_room'] == 'trap_room' and
            'torch' not in game_state['player_inventory']):
            print("Без света вы не видите плиты... Опасность!")
            trigger_trap(game_state)
