import telebot
from telebot import types

from parsing.parsing import Parser, cities_ru
from user_data import UserData

bot = telebot.TeleBot('6924846054:AAF56WNwKipFUs9wTakgLm_JK36514tVUEE')

ukrainian_cities = cities_ru

users = {}


@bot.message_handler(commands=['my'])
def info(message):
    bot.send_message(message.chat.id, users[message.from_user.id])


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    print(type(message))
    print(message.from_user.id)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Начать')
    markup.add(btn1)
    bot.send_message(message.chat.id, 'Этот бот найдет на сайте OlX свежие объявления об аренде квартир и '
                                      'предоставит ссылку.\nОтправьте '
                                      '"Начать" или нажмите кнопку:', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, find)


def find(message: telebot.types.Message):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(city, callback_data=city) for city in ukrainian_cities]
    markup.add(*buttons)
    users[message.from_user.id]: UserData = UserData('waiting_city')
    bot.send_message(message.chat.id, 'Выберите областной центр:', reply_markup=markup)
    print(users[message.from_user.id].state)

    bot.send_message(message.chat.id, users[message.from_user.id])


@bot.message_handler(func=lambda message: message.text.lower() == 'Начать'.lower())
def call_cities(message):
    find(message)


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'waiting_city')
def handle_city_selection(message):
    user: UserData = users[message.from_user.id]
    print(f'Юзер написал сообщение: {message.text}')
    if message.text.lower() in [city.lower() for city in ukrainian_cities]:
        user.selected_city = message.text
        bot.send_message(message.chat.id, f'Выбран город: {user.selected_city}')
        user.state = 'waiting_rooms'
        bot.send_message(message.chat.id, f'Выбран город: {user.selected_city}\nВведите минимум комнат (1 - 5):')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_room)
    else:
        bot.send_message(message.chat.id, f'Неизвестный областной центр: {message.text}\n '
                                          f'Введите еще раз или выберите из списка')


@bot.callback_query_handler(func=lambda call: users[call.from_user.id].state == 'waiting_city')
def handle_city_selection_callback(call):
    user: UserData = users[call.from_user.id]
    city_name = call.data
    print(f'Юзер нажал кнопку с городом: {city_name}')
    user.selected_city = city_name
    # Очищаем состояние
    user.state = 'waiting_rooms'
    print(user.selected_city)
    print(call)
    bot.send_message(call.message.chat.id, f'Выбран город: {user.selected_city}\nВведите минимум комнат (1 - 5):')
    # bot.register_next_step_handler_by_chat_id(call.message.chat.id, min_room)


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'waiting_rooms')
def min_room(message):
    user: UserData = users[message.from_user.id]
    print(message.text)
    min_rooms: int
    try:
        min_rooms = int(message.text)
    except Exception as e:
        print(f"An exception occurred: {e}")
        min_rooms = -1
    if min_rooms not in range(1, 6):
        bot.send_message(message.chat.id, f'Неверное колличество комнат!\nОтправьте цифру от 1 до 5')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_room)
    else:
        user.state = 'waiting_max_rooms'
        user.min_rooms = min_rooms
        bot.send_message(message.chat.id, f'Введите максимум комнат (1 - 5):')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, max_room)


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'waiting_max_rooms')
def max_room(message):
    user: UserData = users[message.from_user.id]
    max_rooms: int
    try:
        max_rooms = int(message.text)
    except Exception as e:
        print(f"An exception occurred: {e}")
        max_rooms = -1
    if max_rooms not in range(1, 6):
        bot.send_message(message.chat.id, f'Неверное колличество комнат!\nОтправьте цифру от 1 до 5')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, max_room)
    elif max_rooms < users[message.from_user.id].min_rooms:
        bot.send_message(message.chat.id, f'максимальное значение меньше минимального!\nДавайте попробуем еще раз')
        bot.send_message(message.chat.id, f'Выбран город: {users[message.chat.id].selected_city}'
                                          f'\nВведите минимум комнат (1 - 5):')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_room)
        user.state = 'waiting_rooms'
    else:
        users[message.from_user.id].max_rooms = max_rooms
        users[message.from_user.id].state = 'wait_price'
        bot.send_message(message.chat.id, f'Выбран город: {users[message.from_user.id].selected_city}\n'
                                          f'Выбрано колличество комнат: {users[message.from_user.id].min_rooms}'
                                          f' - {users[message.from_user.id].max_rooms}')
        bot.send_message(message.chat.id, 'Введите минимальную стоимость аренды в грн. (0 если не имеет значения)')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_price)


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'wait_price')
def min_price(message):
    user: UserData = users[message.from_user.id]
    min_rent: int
    try:
        min_rent = round(float(message.text.replace(',', '.')))
    except Exception as e:
        print(f"An exception occurred: {e}")
        min_rent = -1
    print(f'min rent: {min_rent}')
    if min_rent < 0:
        bot.send_message(message.chat.id, f'Введено неправильное значение!\nВведите любое число от 0')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_price)
    else:
        user.min_price = min_rent
        bot.send_message(message.chat.id, 'Введите максимальную стоимость аренды в грн. (0 если не имеет значения)')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, max_price)
        users[message.from_user.id].state = 'wait_max_price'


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'wait_max_price')
def max_price(message):
    user: UserData = users[message.from_user.id]
    max_rent: int
    ready_btn = ready_btns()
    try:
        max_rent = round(float(message.text.replace(',', '.')))
    except Exception as e:
        print(f"An exception occurred: {e}")
        max_rent = -1
    print(f'max rent: {max_rent}')
    if max_rent < 0:
        bot.send_message(message.chat.id, f'Введено неправильное значение!\nВведите любое число от 0')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, max_price)
    elif max_rent != 0 and max_rent < user.min_price:
        bot.send_message(message.chat.id, f'Максимальная стоимость {max_rent} меньше минимальной '
                                          f'стоимости {user.min_price}\nДавайте попробуем еще раз.')
        # bot.register_next_step_handler_by_chat_id(message.chat.id, min_price)
        user.state = 'wait_price'
        bot.send_message(message.chat.id, 'Введите минимальную стоимость аренды в грн. (0 если не имеет значения)')
    else:
        user.max_price = max_rent
        user.state = 'min_ready'
        bot.send_message(message.chat.id, f'Выбран город: {users[message.from_user.id].selected_city}\n'
                                          f'Выбрано колличество комнат: {users[message.from_user.id].min_rooms}'
                                          f' - {users[message.from_user.id].max_rooms}'
                                          f'\nВыбран ценовой диапозон: '
                                          f'{"Не важно" if user.min_price == 0 else user.min_price} - '
                                          f'{"Не важно" if user.max_price == 0 else user.max_price}')
        bot.send_message(message.chat.id, 'ssss', reply_markup=ready_btn)
    print(users)


@bot.callback_query_handler(func=lambda call: users[call.from_user.id].state == 'min_ready')
def get_adv(call):
    user = users[call.from_user.id]
    bot.send_message(call.message.chat.id, f"ожидайте {users[call.from_user.id]}")
    parser = Parser(user)
    advertising = parser.get_advertising()
    bot.send_message(call.message.chat.id, f"ожидайте \n{advertising}")



def ready_btns():
    markup = types.InlineKeyboardMarkup()
    searching = types.InlineKeyboardButton('Искать', callback_data="get_adv")
    markup.add(searching)
    return markup





bot.infinity_polling()

# @bot.message_handler(commands=['message'])
# def main(message):
#     bot.send_message(message.chat.id, message)


# def room_checkbox():
#     markup = types.InlineKeyboardMarkup()
#     for i in range(1, 6):
#         button_text = f'☑ {i}'  # ☑ символизирует выбранный чекбокс
#         callback_data = f'checkbox_{i}'
#         button = types.InlineKeyboardButton(button_text, callback_data=callback_data)
#         markup.add(button)
#
#     return markup
