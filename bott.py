import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import json
from mytoken import my_token #отдельный файл, из которого импортируется токен бота

bot = telebot.TeleBot(token=my_token)

score = 0


def answer(message, user, current_question_index):
    if current_question_index < len(answers_to_character):
        if message.text == answers_to_character[current_question_index]['1']:
          user['score'] += 4
        if message.text == answers_to_character[current_question_index]['2']:
          user['score'] += 1

def get_question_markup(question):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*question['options'])
    return markup


def send_question(user_id):
    user = users_data.get(user_id, {'current_question': 0, 'score': 0})
    question = questions[user['current_question']]
    markup = get_question_markup(question)
    bot.send_message(user_id, question['text'], reply_markup=markup)


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content['questions'], content['answers_to_character'], content['results']


questions, answers_to_character, results = load_json('questions.json')


def load_user_data():
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)


users_data = {}


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '''/help-список доступных команд
/start-запустить бота или перезапустить анкету''')


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id in users_data and 'current_question' in users_data[user_id]:
        bot.send_message(user_id, 'Продолжаем вашу предыдущую сессию.')
        send_question(user_id)
    else:
        bot.send_message(message.chat.id, 'Привет это бот проверки на оптимизм!')
        bot.send_message(user_id,
                         '''
                         Этот тест исключительно субъективен и основан только на моём личном мнении.
                         
(Чтобы запустить анкету, введи команду /start ещё раз)''')
        users_data[user_id] = {
            'current_question': 0,
            'score': score
        }
        save_user_data()
        send_question(user_id)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if user_id not in users_data:
        bot.send_message(user_id, 'Чтобы начать анкету, используй команду /start')
        return

    user = users_data[user_id]
    current_question_index = user['current_question']
    question = questions[current_question_index]

    if message.text not in question['options']:
        bot.send_message(user_id, 'Пожалуйста, выбери один из предложенных вариантов')
        return

    user = users_data[user_id]
    current_question_index = user['current_question']
    questions[current_question_index]

    answer(message, user, current_question_index)
    save_user_data()
    user['current_question'] += 1
    if user['current_question'] < len(questions):
        send_question(user_id)
    else:
        if user['score'] <= 8:
            bot.send_message(user_id, results["Оптимист"]['text'])
            bot.send_message(user_id, results["Оптимист"]['description'])
            bot.send_photo(user_id, results["Оптимист"]['image'])

            del users_data[user_id]
            save_user_data()
        elif user['score'] > 8:
            bot.send_message(user_id, results["Пессимист"]['text'])
            bot.send_message(user_id, results["Пессимист"]['description'])
            bot.send_photo(user_id, results["Пессимист"]['image'])

            del users_data[user_id]
            save_user_data()

@bot.message_handler(func=lambda m: True)
def unknown_command(message):
 known_commands = ['/start', '/help', '/person', '/news']
 if message.text.split()[0] not in known_commands:
     bot.reply_to(message, "Некорректный ввод. Введите /help для просмотра доступных функций")

save_user_data()

bot.polling()
