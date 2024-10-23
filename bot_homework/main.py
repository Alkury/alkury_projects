import sqlite3

import requests
import telebot
import datetime
import time
from telebot import types

bot_token = '8144493435:AAFJ5S9a5gqsIY_ms8bWzTuwTUC0utuApco'  # Вставь свой токен
bot = telebot.TeleBot(bot_token)


conn = sqlite3.connect('dz.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY,
    subject TEXT,
    chislo TEXT, 
    assignment TEXT
)''')


@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    user_input = query.query.lower()
    subjects = {
        "физика": "Дз по физике",
        "матан": "Дз по матану",
        "англ": "Дз по английскому",
        "линал": "Дз по линалу",
        "матлог": "Дз по математической логике и теории алгоритмов",
        "инфа": "Дз по информатике"
    }

    if user_input in subjects:
        cursor.execute("SELECT assignment, chislo FROM homework WHERE subject=?", (user_input,))
        homework = cursor.fetchone()

        if homework:
            subject = types.InlineQueryResultArticle(
                str(1), subjects[user_input],
                types.InputTextMessageContent(
                    f"Дз по предмету {user_input[0].upper() + user_input[1:]} на {homework[1]}: {homework[0]}"
                )
            )
        else:
            subject = types.InlineQueryResultArticle(
                str(1), 'Нет данных',
                types.InputTextMessageContent(f"Нет данных по предмету {user_input[0].upper() + user_input[1:]}")
            )

        bot.answer_inline_query(query.id, [subject])
    else:
        subject = types.InlineQueryResultArticle(
            str(1), 'Пасхалка, либо введи верный формат или нажми на меня',
            types.InputTextMessageContent("Этого бота сделал @a1kury")
        )
        bot.answer_inline_query(query.id, [subject])


# Функция для добавления домашнего задания
def add_homework(message):
    try:
        subject, assignment = [i.lower() for i in message.text.split(':')[1].split('; ')]
        subject = subject.strip()
        date_str = message.text.split(':')[0].strip().split(' ')[1]
        print(date_str, subject, assignment)
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        cursor.execute("SELECT subject, chislo FROM homework WHERE subject=?", (subject,))
        homework = cursor.fetchone()
        if homework:
            cursor.execute("UPDATE homework SET assignment=?, chislo=? WHERE subject=?", (assignment, date, subject,))
            conn.commit()
        else:
            cursor.execute("INSERT INTO homework (subject, assignment, chislo) VALUES (?, ?, ?)",
                           (subject, assignment, date))
            conn.commit()

        bot.reply_to(message, "Домашнее задание успешно добавлено!")
    except (IndexError, ValueError):
        bot.reply_to(message, "Ошибка: неверный формат. Используй формат:/add <YYYY-MM-DD>: <предмет>; <задание>")


# Функция для отправки по команде
def send_reminders():
    today = datetime.date.today()
    cursor.execute("SELECT * FROM homework ORDER by chislo")
    rows = cursor.fetchall()
    homework_for_date = []
    for i, row in enumerate(rows, start=1):
        date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()
        if date >= today:
            homework_for_date.append(f"{i}) {row[1]}({row[2].split('-')[2]}.{row[2].split('-')[1]}): {row[3]}")

    if homework_for_date:
        bot.send_message(chat_id=-1002196123776, text="Актуальное дз:\n{}".format('\n\n'.join(homework_for_date)))


def reminder_loop():
    now = datetime.datetime.now()
    tomorrow = now.date() + datetime.timedelta(days=1)
    cursor.execute("SELECT * FROM homework ORDER by chislo")
    rows = cursor.fetchall()
    homework_for_tomorrow = []
    for i, row in enumerate(rows, start=1):
        date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()
        if date == tomorrow:
            homework_for_tomorrow.append(f"{i}) {row[1]}: {row[3]}")
            i += 1

    if homework_for_tomorrow:
        bot.send_message(chat_id=-1002196123776,
                         text="Дз на завтра: \n" + "\n".join(homework_for_tomorrow))


# Команда для добавления домашнего задания
@bot.message_handler(commands=['add'], content_types=['text'])
def handle_add_homework(message):
    add_homework(message)


# Команда для отправки напоминаний вручную
@bot.message_handler(commands=['send'], content_types=['text'])
def handle_send_reminders(message):
    send_reminders()


while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=120, long_polling_timeout=240)
    except requests.exceptions.ReadTimeout:
        print("Read timeout occurred. Restarting polling...")
        time.sleep(10)
