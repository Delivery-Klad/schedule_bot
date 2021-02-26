import telebot
import requests
import psycopg2
from googletrans import Translator

bot = telebot.TeleBot("1695146161:AAEcW2Rk2Fo39dGGMvnx2Kkz7qZ_4iFygx4")
sm = "🤖"
group_list = []
commands = ["сегодня", "завтра", "на неделю"]
translator = Translator(service_urls=["translate.google.com", "translate.google.net"])
print(bot.get_me())


def db_connect():  # функция подключения к первой базе данных
    try:
        con = psycopg2.connect(
            host="ec2-52-70-67-123.compute-1.amazonaws.com",
            database="d68nmk23reqak4",
            user="egnnjetsqjwwji",
            port="5432",
            password="dcf3bd216bd19303409eb66b094b902d35610feb0fab452eb46365592829061b"
        )
        cur = con.cursor()
        return con, cur
    except Exception as er:
        print(er)


def create_tables():
    connect, cursor = db_connect()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER, username TEXT, first_name TEXT,"
                   "last_name TEXT, grp TEXT)")
    connect.commit()
    cursor.close()
    connect.close()


def translate_text(text):
    try:
        res = translator.translate(text, dest='ru').text
        first = res[0]
        res = first.upper() + res[1:]
        return res
    except Exception as er:
        print(er)
        return text


@bot.message_handler(commands=['db'])
def handler_db(message):
    if message.from_user.id == 496537969:
        create_tables()
        connect, cursor = db_connect()
        cursor.execute("SELECT * FROM users")
        for i in cursor.fetchall():
            print(i)
        cursor.close()
        connect.close()


@bot.message_handler(commands=['start'])
def handler_start(message):
    try:
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row("сегодня", "завтра", "на неделю")
        connect, cursor = db_connect()
        cursor.execute(f"SELECT count(id) FROM users WHERE id={message.from_user.id}")
        res = cursor.fetchall()[0][0]
        if res == 0:
            cursor.execute(f"INSERT INTO users VALUES({message.from_user.id}, $taG${message.from_user.username}$taG$,"
                           f"$taG${message.from_user.first_name}$taG$, $taG${message.from_user.last_name}$taG$, "
                           f"$taG$None$taG$)")
            connect.commit()
            cursor.close()
            connect.close()
        bot.send_message(message.from_user.id, f"<b>{sm}Камнями кидаться <a href='t.me/delivery_klad'>СЮДА</a></b>\n"
                                               "/group - установить/изменить группу\n"
                                               "/today - расписание на сегодня\n"
                                               "/tomorrow - расписание на завтра\n"
                                               "/week - расписание на неделю",
                         reply_markup=user_markup, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as er:
        bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
        print(er)


@bot.message_handler(commands=['group'])
def handler_group(message):
    try:
        if message.from_user.id not in group_list:
            group_list.append(message.from_user.id)
        bot.send_message(message.from_user.id, f"{sm}Напишите вашу группу")
    except Exception as er:
        bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
        print(er)


def sort_days(days):
    temp, day = [], ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i in days:
        temp.append(day.index(i))
    temp.sort()
    days, tmp, index = [], [], 10
    for i in temp:
        days.append(day[i])
    return days


def number_of_lesson(time):
    if time[0] == "9":
        return "1 пара"
    elif time[:2] == "10":
        return "2 пара"
    elif time[:2] == "12":
        return "3 пара"
    elif time[:2] == "14":
        return "4 пара"
    elif time[:2] == "16":
        return "5 пара"
    elif time[:2] == "18":
        return "6 пара"
    elif time[:2] == "19":
        return "7 пара"
    return time


@bot.message_handler(content_types=['text'])
def handler_text(message):
    print(f"{message.from_user.id} {message.from_user.username} {message.text}")
    if message.from_user.id in group_list:
        try:
            connect, cursor = db_connect()
            cursor.execute(f"SELECT count(id) FROM users WHERE id={message.from_user.id}")
            res = cursor.fetchall()[0][0]
            if res == 0:
                cursor.execute(
                    f"INSERT INTO users VALUES({message.from_user.id}, $taG${message.from_user.username}$taG$,"
                    f"$taG${message.from_user.first_name}$taG$, $taG${message.from_user.last_name}$taG$, "
                    f"$taG${message.text.upper()}$taG$)")
            else:
                cursor.execute(f"UPDATE users SET grp=$taG${message.text.upper()}$taG$ WHERE id={message.from_user.id}")
            connect.commit()
            cursor.close()
            connect.close()
            bot.send_message(message.from_user.id, f"{sm}Я вас запомнил")
            group_list.pop(group_list.index(message.from_user.id))
            return
        except Exception as er:
            bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
            print(er)
    if message.text[0] == "/" or message.text in commands:
        try:
            connect, cursor = db_connect()
            cursor.execute(f"SELECT grp FROM users WHERE id={message.from_user.id}")
            try:
                group = cursor.fetchone()[0]
                cursor.close()
                connect.close()
            except IndexError:
                bot.send_message(message.from_user.id, f"{sm}У вас не указана группа\n/group, чтобы указать группу")
                return
            if group == "None":
                bot.send_message(message.from_user.id, f"{sm}У вас не указана группа\n/group, чтобы указать группу")
                return
        except Exception as er:
            print(er)
            bot.send_message(message.from_user.id, f"{sm}Не удается получить вашу группу\n/group, чтобы указать группу")
            return
        if "today" in message.text or commands[0] in message.text:
            res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/today")
            lessons = res.json()
            rez = "<b>Пары сегодня:\n</b>"
            for i in lessons:
                j, o = i['lesson'], i['time']
                try:
                    rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>🕘{o['start']} - " \
                           f"{o['end']})</b>\n{j['name']} ({j['type']})\nПреподаватель: {j['teacher']}\n\n"
                except TypeError:
                    pass
            if len(rez) > 50:
                bot.send_message(message.from_user.id, rez, parse_mode="HTML")
            else:
                bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
        elif "tomorrow" in message.text or commands[1] in message.text:
            res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/tomorrow")
            lessons = res.json()
            rez = "<b>Пары завтра:\n</b>"
            for i in lessons:
                j, o = i['lesson'], i['time']
                try:
                    rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>🕘{o['start']} - " \
                           f"{o['end']})</b>\n{j['name']} ({j['type']})\nПреподаватель: {j['teacher']}\n\n"
                except TypeError:
                    pass
            if len(rez) > 50:
                bot.send_message(message.from_user.id, rez, parse_mode="HTML")
            else:
                bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
        elif "week" in message.text or commands[2] in message.text:
            res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/week")
            lessons = res.json()
            rez, days = "", []
            try:
                for i in lessons:
                    days.append(i)
                days = sort_days(days)
                for i in days:
                    rez += f"<b>{translate_text(i)}\n</b>"
                    for k in lessons[i]:
                        j, o = k['lesson'], k['time']
                        try:
                            rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>🕘{o['start']} -" \
                                   f" {o['end']})</b>\n{j['name']} ({j['type']})\n" \
                                   f"Преподаватель: {j['teacher']}\n\n"
                        except TypeError:
                            pass
                    rez += "------------------------\n"
            except Exception as er:
                bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
                print(er)
            if len(rez) > 50:
                bot.send_message(message.from_user.id, f"{rez}", parse_mode="HTML")
            else:
                bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
    else:
        bot.send_message(message.from_user.id, f"{sm}<b>Я вас не понял</b>", parse_mode="HTML")


try:
    while True:
        try:
            bot.polling(none_stop=True, interval=0)  # обращение к api
        except Exception as e:
            print(e)
except Exception as e:
    print(e)
