# labyrinth_game/utils.py
from labyrinth_game.constants import ROOMS


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
    print("  go <direction>  - перейти в направлении (north/south/east/west)")
    print("  look            - осмотреть текущую комнату")
    print("  take <item>     - поднять предмет")
    print("  use <item>      - использовать предмет из инвентаря")
    print("  inventory       - показать инвентарь")
    print("  solve           - попытаться решить загадку в комнате")
    print("  quit            - выйти из игры")
    print("  help            - показать это сообщение")


def solve_puzzle(game_state):
    room_name = game_state['current_room']
    room = ROOMS[room_name]

    if room['puzzle'] is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = room['puzzle']
    print(f"\n{question}")
    user_answer = input("Ваш ответ: ").strip()

    if user_answer.lower() == correct_answer.lower():
        print("Верно! Загадка решена.")
        # Убираем загадку
        room['puzzle'] = None

        # Награда за загадку
        if room_name == 'hall':
            if 'treasure_key' not in game_state['player_inventory']:
                game_state['player_inventory'].append('treasure_key')
                print("Вы получили ключ от сокровищницы!")
        elif room_name == 'trap_room':
            print("Плиты успокоились. Вы в безопасности.")
        elif room_name == 'library':
            print("Свиток исчезает в дымке.")
        elif room_name == 'treasure_room':
            # Это обрабатывается в attempt_open_treasure
            pass
    else:
        print("Неверно. Попробуйте снова.")


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

