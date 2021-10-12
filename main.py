import telebot
from telebot import types
import os
from flask import Flask, request

TOKEN = '2064275827:AAHGY8DwPUzhsRfqqvSApWbef4rLfIe8DEU'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

user_dict = {}

gender_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
gender_markup.add('Чоловік', 'Жінка', 'Назад')

only_back_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
only_back_markup.add('Назад')

menu_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
menu_markup.add('Інформація про мене', 'Налаштування', 'Назад')

settings_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
settings_markup.add('Змінити ім`я', 'Змінити вік', 'Змінити стать', 'Назад')

hide_markup = types.ReplyKeyboardRemove()


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.gender = None


@bot.message_handler(commands=['help', 'start'])
def start(message):
    if message.chat.id not in user_dict:
        bot.reply_to(message, "Привіт. Я простий бот анкетування і я дуже хочу дізнатися про тебе більше.")
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Як тебе звати?", reply_markup=hide_markup),
                                       registration_name_step)
    else:
        return main_menu(message)


def registration_name_step(message):
    user = User(message.text)
    user_dict[message.chat.id] = user
    if message.text == 'Назад' or len(message.text) > 20 or len(message.text) < 2:
        return bot.register_next_step_handler(bot.send_message(message.chat.id,
                                                               "Мені здається це твоє несправжнє ім'я. "
                                                               "Спробуй ще раз. Як тебе звати? "),
                                              registration_name_step)

    bot.register_next_step_handler(
        bot.reply_to(message, "Скільки тобі років?", reply_markup=only_back_markup), registration_age_step)


def registration_age_step(message):
    if message.text == 'Назад':
        return bot.register_next_step_handler(
            bot.send_message(message.chat.id, "Повернемося до попереднього питання. Як тебе звати?"),
            registration_name_step)
    age = message.text
    if not age.isdigit() or int(age) > 128 or int(age) < 2:
        return bot.register_next_step_handler(bot.reply_to(message, "Твій вік точно вірно введений? Перевір будь ласка",
                                                           reply_markup=only_back_markup), registration_age_step)
    user = user_dict[message.chat.id]
    user.age = age
    bot.register_next_step_handler(bot.reply_to(message, "А тепер дуже інтимне питання. Яка твоя стать?",
                                                reply_markup=gender_markup), registration_gender_step)


def registration_gender_step(message):
    if message.text == 'Назад':
        return bot.register_next_step_handler(
            bot.send_message(message.chat.id, "Повернемося до попереднього питання. Все ж таки, скільки тобі років?",
                             reply_markup=only_back_markup), registration_age_step)
    user = user_dict[message.chat.id]
    if not (message.text == 'Чоловік' or message.text == 'Жінка'):
        return bot.register_next_step_handler(
            bot.reply_to(message, "Але немає такої статі... Спробуй ще раз!", reply_markup=gender_markup),
            registration_gender_step)
    user.gender = message.text
    bot.send_message(message.chat.id, "Дякую за реєстрацію, " + user.name + "\nТепер ми знаємо, що тобі " + user.age +
                     " років і ти " + user.gender.lower())
    bot.send_message(message.chat.id, "Використовуй команду /menu, аби потрапити у меню.")
    main_menu(message)


@bot.message_handler(commands=['menu'])
def main_menu(message):
    if message.text == 'Інформація про мене':
        user = user_dict[message.chat.id]
        bot.send_message(message.chat.id,
                         "Твоє ім'я: " + user.name + "\nТобі " + user.age +
                         " років і ти " + user.gender.lower())
        return bot.send_message(message.chat.id, "Повертаємось у головне меню.\n"
                                                 "Тут ти можеш подивитися інформацію про себе, а також перейти у налаштування.",
                                reply_markup=menu_markup)
    if message.text == 'Налаштування':
        settings(message)
        return
    bot.send_message(message.chat.id, "Ти у головному меню. "
                                      "Тут ти можеш подивитися інформацію про себе, а також перейти у налаштування.",
                     reply_markup=menu_markup)
    bot.register_next_step_handler(bot.send_message(message.chat.id, "Введіть назву пункту головного меню"), main_menu)


def settings(message):
    user = user_dict[message.chat.id]
    if message.text == 'Назад':
        return main_menu(message)
    if message.text == 'Змінити ім`я':
        return bot.register_next_step_handler(
            bot.reply_to(message, "Раніше тебе звали " + user.name + ".\nЯк ти хочеш аби тебе звали зараз?",
                         reply_markup=only_back_markup), change_name)

    if message.text == 'Змінити вік':
        return bot.register_next_step_handler(
            bot.reply_to(message, "Раніше тобі було " + user.age + " років.\nЯкий твій рік зараз?",
                         reply_markup=only_back_markup), change_age)
    if message.text == 'Змінити стать':
        return bot.register_next_step_handler(
            bot.reply_to(message, "Твоя минула стать - " + user.gender + ".\nХто ти зараз?", reply_markup=gender_markup),
            change_gender)
    bot.register_next_step_handler(bot.send_message(message.chat.id, "Ти у меню налаштувань. "
                                                                     "Тут ти можеш змінити якусь інформацію про себе.",
                                                    reply_markup=settings_markup), settings)


def change_name(message):
    user = user_dict[message.chat.id]
    if message.text == 'Назад':
        return bot.register_next_step_handler(bot.send_message(message.chat.id, "Ти повертаєшся меню налаштувань. "
                                                                                "Тут ти можеш змінити якусь інформацію про себе.",
                                                               reply_markup=settings_markup), settings)
    if len(message.text) > 20 or len(message.text) < 2:
        return bot.register_next_step_handler(bot.send_message(message.chat.id,
                                                               "Мені здається це твоє несправжнє ім'я. "
                                                               "Спробуй ще раз. Як тебе звати? "),
                                              change_name)
    user.name = message.text
    bot.send_message(message.chat.id, "Тепер тебе звати " + user.name)
    return main_menu(message)


def change_age(message):
    user = user_dict[message.chat.id]
    if message.text == 'Назад':
        return bot.register_next_step_handler(bot.send_message(message.chat.id, "Ти повертаєшся меню налаштувань. "
                                                                                "Тут ти можеш змінити якусь інформацію про себе.",
                                                               reply_markup=settings_markup), settings)
    age = message.text
    if not age.isdigit() or int(age) > 128 or int(age) < 2:
        return bot.register_next_step_handler(bot.reply_to(message, "Твій вік точно вірно введений? Перевір будь ласка",
                                                           reply_markup=only_back_markup), change_age)
    user.age = age
    bot.send_message(message.chat.id, "Тепер тобі " + user.age + " років.")
    return main_menu(message)


def change_gender(message):
    user = user_dict[message.chat.id]
    if message.text == 'Назад':
        return bot.register_next_step_handler(bot.send_message(message.chat.id, "Ти повертаєшся меню налаштувань. "
                                                                                "Тут ти можеш змінити якусь інформацію про себе.",
                                                               reply_markup=settings_markup), settings)
    if not (message.text == 'Чоловік' or message.text == 'Жінка'):
        return bot.register_next_step_handler(
            bot.reply_to(message, "Але немає такої статі... Спробуй ще раз!", reply_markup=gender_markup),
            change_gender)
    user.gender = message.text
    bot.send_message(message.chat.id, "Тепер твоя стать: " + user.gender)
    return main_menu(message)


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://exampleqbot.herokuapp.com/bot' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
