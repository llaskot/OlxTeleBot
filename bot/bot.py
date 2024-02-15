import telebot
from telebot import types

bot = telebot.TeleBot('6924846054:AAF56WNwKipFUs9wTakgLm_JK36514tVUEE')


@bot.message_handler(commands=['start'])
def main(message):
    city_drp = types.In
    bot.send_message(message.chat.id, 'Этот бот найдет на сайте OlX свежие обьявления об аренде квартир и предоставит '
                                      'ссылку \nВыберите город')


@bot.message_handler(commands=['message'])
def main(message):
    bot.send_message(message.chat.id, message)


bot.infinity_polling()
