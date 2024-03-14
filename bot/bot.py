import telebot
from telebot import types

from parsing.parsing import Parser, cities_ru
from .user_data import UserData
from credentials.creds import token

bot = telebot.TeleBot(token)

ukrainian_cities = cities_ru

users = {}


@bot.message_handler(commands=['my'])
def info(message):
    bot.send_message(message.chat.id, users[message.from_user.id])


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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


@bot.message_handler(func=lambda message: message.text.lower() == 'Начать'.lower())
def call_cities(message):
    find(message)


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'waiting_city')
def handle_city_selection(message):
    user: UserData = users[message.from_user.id]
    if message.text.lower() in [city.lower() for city in ukrainian_cities]:
        user.selected_city = message.text
        bot.send_message(message.chat.id, f'Выбран город: {user.selected_city}')
        user.state = 'waiting_rooms'
        bot.send_message(message.chat.id, f'Выбран город: {user.selected_city}\nВведите минимум комнат (1 - 5):')
    else:
        bot.send_message(message.chat.id, f'Неизвестный областной центр: {message.text}\n '
                                          f'Введите еще раз или выберите из списка')


@bot.callback_query_handler(func=lambda call: users[call.from_user.id].state == 'waiting_city')
def handle_city_selection_callback(call):
    user: UserData = users[call.from_user.id]
    city_name = call.data
    user.selected_city = city_name
    user.state = 'waiting_rooms'
    bot.send_message(call.message.chat.id, f'Выбран город: {user.selected_city}\nВведите минимум комнат (1 - 5):')


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'waiting_rooms')
def min_room(message):
    user: UserData = users[message.from_user.id]
    min_rooms: int
    try:
        min_rooms = int(message.text)
    except Exception as e:
        print(f"An exception occurred: {e}")
        min_rooms = -1
    if min_rooms not in range(1, 6):
        bot.send_message(message.chat.id, f'Неверное колличество комнат!\nОтправьте цифру от 1 до 5')
    else:
        user.state = 'waiting_max_rooms'
        user.min_rooms = min_rooms
        bot.send_message(message.chat.id, f'Введите максимум комнат (1 - 5):')


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
    elif max_rooms < users[message.from_user.id].min_rooms:
        bot.send_message(message.chat.id, f'максимальное значение меньше минимального!\nДавайте попробуем еще раз')
        bot.send_message(message.chat.id, f'Выбран город: {users[message.chat.id].selected_city}'
                                          f'\nВведите минимум комнат (1 - 5):')
        user.state = 'waiting_rooms'
    else:
        users[message.from_user.id].max_rooms = max_rooms
        users[message.from_user.id].state = 'wait_price'
        bot.send_message(message.chat.id, f'Выбран город: {users[message.from_user.id].selected_city}\n'
                                          f'Выбрано колличество комнат: {users[message.from_user.id].min_rooms}'
                                          f' - {users[message.from_user.id].max_rooms}')
        bot.send_message(message.chat.id, 'Введите минимальную стоимость аренды в грн. (0 если не имеет значения)')


@bot.message_handler(func=lambda message: users[message.from_user.id].state == 'wait_price')
def min_price(message):
    user: UserData = users[message.from_user.id]
    min_rent: int
    try:
        min_rent = round(float(message.text.replace(',', '.')))
    except Exception as e:
        print(f"An exception occurred: {e}")
        min_rent = -1
    if min_rent < 0:
        bot.send_message(message.chat.id, f'Введено неправильное значение!\nВведите любое число от 0')
    else:
        user.min_price = min_rent
        bot.send_message(message.chat.id, 'Введите максимальную стоимость аренды в грн. (0 если не имеет значения)')
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
    if max_rent < 0:
        bot.send_message(message.chat.id, f'Введено неправильное значение!\nВведите любое число от 0')
    elif max_rent != 0 and max_rent < user.min_price:
        bot.send_message(message.chat.id, f'Максимальная стоимость {max_rent} меньше минимальной '
                                          f'стоимости {user.min_price}\nДавайте попробуем еще раз.')
        user.state = 'wait_price'
        bot.send_message(message.chat.id, 'Введите минимальную стоимость аренды в грн. (0 если не имеет значения)')
    else:
        user.max_price = max_rent
        user.state = 'min_ready'
        bot.send_message(message.chat.id, f'Выбран город: <b>{users[message.from_user.id].selected_city}</b>\n'
                                          f'Выбрано колличество комнат: <b>{users[message.from_user.id].min_rooms}'
                                          f' - {users[message.from_user.id].max_rooms}</b>'
                                          f'\nВыбран ценовой диапозон: <b>от '
                                          f'{"Не важно" if user.min_price == 0 else user.min_price} до '
                                          f'{"Не важно" if user.max_price == 0 else user.max_price}</b>'
                         , parse_mode='HTML')
        bot.send_message(message.chat.id, 'Нажмите "Искать" или добавьте дополнительные параметры',
                         reply_markup=ready_btn)
    print(users)


@bot.callback_query_handler(func=lambda call: users[call.from_user.id].state == 'min_ready')
def get_adv(call):
    print(call)
    if call.data == 'get_adv':
        user = users[call.from_user.id]
        user.state = None
        bot.send_message(call.message.chat.id, f"Идет поиск...")
        parser = Parser(user)
        qty, advertising = parser.get_advertising()
        if qty == 0:
            bot.send_message(call.message.chat.id,
                             'По вашему запросу найдено 0 объявлений\nПопробуйе внести другие параметры поиска')
        else:
            bot.send_message(call.message.chat.id,
                             f'По вашему запросу найдено {qty} объявлений\n'
                             f'Показаны самые новые. Продвигаемые объявления не скрыты.')
            adv_messages(advertising, call.message.chat.id)
    elif call.data == 'additional_params':
        markup = ready_btns()
        bot.send_message(call.message.chat.id, "Sorry! Developing is in progress yet.", reply_markup=markup)


def adv_messages(resp: list[{}], c_id):
    for adv in resp:
        # print(adv)
        pic = f'{adv["location_date"]} <a href="{adv["foto"]}">&#8205;</a>'
        text_link = f'<a href="{adv["link"]}">{adv["info"]}</a>'
        paid = '<b>Продвигается</b>' if adv["paid"] else ''
        bot.send_message(c_id, pic + f'\nЦена: {adv["price"]}     Площадь: {adv["square"]}'
                                     f'        {paid}\n{text_link}',
                         parse_mode='HTML')


def ready_btns():
    markup = types.InlineKeyboardMarkup()
    searching = types.InlineKeyboardButton('Искать', callback_data="get_adv")
    additional_params = types.InlineKeyboardButton('Доп. параметры', callback_data="additional_params")
    markup.add(searching, additional_params)
    return markup


# bot.infinity_polling()

def start_bot():
    try:
        # ваш код инициализации бота и другие настройки
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка: {e}")


# if __name__ == "__main__":
#     start_bot()