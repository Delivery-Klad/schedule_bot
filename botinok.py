import telebot
import requests
import psycopg2
import os
import linecache
import sys


bot = telebot.TeleBot(os.environ.get('TOKEN'))
sm = "🤖"
group_list = []
commands = ["сегодня", "завтра", "на неделю"]
day_dict = {"monday": "Понедельник",
            "tuesday": "Вторник",
            "wednesday": "Среда",
            "thursday": "Четверг",
            "friday": "Пятница",
            "saturday": "Суббота",
            "sunday": "Воскресенье"}
lesson_dict = {"9:": "1", "10": "2", "12": "3", "14": "4", "16": "5", "18": "6", "19": "7", "20": "8"}
time_dict = {"9:": "🕘", "10": "🕦", "12": "🕐", "14": "🕝", "16": "🕟", "18": "🕕", "19": "🕢", "20": "🕘"}
print(bot.get_me())


def db_connect():  # функция подключения к первой базе данных
    try:
        con = psycopg2.connect(
            host="ec2-52-70-67-123.compute-1.amazonaws.com",
            database="os.environ.get('DB')",
            user="os.environ.get('DB_user')",
            port="5432",
            password="os.environ.get('DB_pass')"
        )
        cur = con.cursor()
        return con, cur
    except Exception as er:
        print(er)


def create_tables():
    connect, cursor = db_connect()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, first_name TEXT,"
                   "last_name TEXT, grp TEXT, ids BIGINT)")
    connect.commit()
    cursor.close()
    connect.close()


def error_log(er):
    if "string indices must be integers" in str(er):
        return
    print(er)
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    reason = f"EXCEPTION IN ({filename}, LINE {lineno} '{line.strip()}'): {exc_obj}"
    print(reason)


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
    print(f"{message.from_user.id} {message.from_user.username} {message.text}")
    try:
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row("сегодня", "завтра", "на неделю")
        connect, cursor = db_connect()
        cursor.execute(f"SELECT count(ids) FROM users WHERE ids={message.from_user.id}")
        res = cursor.fetchall()[0][0]
        if res == 0:
            cursor.execute(f"INSERT INTO users VALUES($taG${message.from_user.username}$taG$,"
                           f"$taG${message.from_user.first_name}$taG$, $taG${message.from_user.last_name}$taG$, "
                           f"$taG$None$taG$, {message.from_user.id})")
            connect.commit()
            cursor.close()
            connect.close()
        text = f"<b>{sm}Камнями кидаться <a href='t.me/delivery_klad'>СЮДА</a></b>\n" \
               f"/group (+группа если бот в беседе)- установить/изменить группу\n" \
               f"/today - расписание на сегодня\n" \
               f"/tomorrow - расписание на завтра\n" \
               f"/week - расписание на неделю"
        if message.chat.type == "private":
            bot.send_message(message.from_user.id, text, reply_markup=user_markup, parse_mode="HTML",
                             disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, text, parse_mode="HTML",
                             disable_web_page_preview=True)
    except Exception as er:
        error_log(er)
        try:
            if message.chat.type == "private":
                bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
            else:
                bot.send_message(message.chat.id, f"{sm}А ой, ошиб04ка")
        except Exception as err:
            error_log(err)


@bot.message_handler(commands=['group'])
def handler_group(message):
    print(f"{message.from_user.id} {message.from_user.username} {message.text}")
    try:
        if message.chat.type == "private":
            if message.from_user.id not in group_list:
                group_list.append(message.from_user.id)
            bot.send_message(message.from_user.id, f"{sm}Напишите вашу группу")
        else:
            try:
                group = message.text.split(" ", 1)[1]
                connect, cursor = db_connect()
                cursor.execute(f"SELECT count(ids) FROM users WHERE ids={message.chat.id}")
                res = cursor.fetchall()[0][0]
                if res == 0:
                    cursor.execute(
                        f"INSERT INTO users VALUES($taG${message.from_user.username}$taG$,"
                        f"$taG${message.from_user.first_name}$taG$, $taG${message.from_user.last_name}$taG$, "
                        f"$taG${group.upper()}$taG$, {message.chat.id})")
                else:
                    cursor.execute(
                        f"UPDATE users SET grp=$taG${group.upper()}$taG$ WHERE ids={message.chat.id}")
                connect.commit()
                cursor.close()
                connect.close()
                print(f"{message.chat.id} {message.from_user.id}")
                bot.send_message(message.chat.id, f"{sm}Я вас запомнил")
            except IndexError:
                bot.send_message(message.chat.id, f"{sm}/group (группа)")
    except Exception as er:
        error_log(er)
        try:
            if message.chat.type == "private":
                bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
            else:
                bot.send_message(message.chat.id, f"{sm}А ой, ошиб04ка")
        except Exception as err:
            error_log(err)


def sort_days(days):
    temp, day = [], ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i in days:
        temp.append(day.index(i))
    temp.sort()
    days, index = [], 10
    for i in temp:
        days.append(day[i])
    return days


def number_of_lesson(lsn):
    global lesson_dict
    try:
        return f"{lesson_dict[lsn[:2]]} пара"
    except KeyError:
        return "? пара"


def get_teacher_ico(name):
    try:
        symbol = name.split(' ', 1)[0]
        if symbol[len(symbol) - 1] == "а":
            return "👩‍🏫"
        else:
            return "👨‍🏫"
    except IndexError:
        return ""


def get_time_ico(time):
    global time_dict
    try:
        return time_dict[time[:2]]
    except Exception as er:
        error_log(er)
        return "🕐"


@bot.message_handler(content_types=['text'])
def handler_text(message):
    print(f"{message.from_user.id} {message.from_user.username} {message.text}")
    try:
        if message.from_user.id in group_list:
            try:
                if "/" in message.text or message.text in commands:
                    bot.send_message(message.from_user.id, f"{sm}НАПИШИТЕ ВАШУ ГРУППУ")
                    return
                connect, cursor = db_connect()
                cursor.execute(f"SELECT count(ids) FROM users WHERE ids={message.from_user.id}")
                res = cursor.fetchall()[0][0]
                if message.chat.type == "private":
                    user_id = message.from_user.id
                else:
                    user_id = message.chat.id
                if res == 0:
                    cursor.execute(
                        f"INSERT INTO users VALUES($taG${message.from_user.username}$taG$,"
                        f"$taG${message.from_user.first_name}$taG$, $taG${message.from_user.last_name}$taG$, "
                        f"$taG${message.text.upper()}$taG$, {user_id})")
                else:
                    cursor.execute(f"UPDATE users SET grp=$taG${message.text.upper()}$taG$ WHERE "
                                   f"ids={message.from_user.id}")
                connect.commit()
                cursor.close()
                connect.close()
                bot.send_message(message.from_user.id, f"{sm}Я вас запомнил")
                group_list.pop(group_list.index(message.from_user.id))
                return
            except Exception as er:
                error_log(er)
                bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
        if message.text[0] == "/" or message.text.lower() in commands:
            try:
                connect, cursor = db_connect()
                if message.chat.type == "private":
                    cursor.execute(f"SELECT grp FROM users WHERE ids={message.from_user.id}")
                else:
                    cursor.execute(f"SELECT grp FROM users WHERE ids={message.chat.id}")
                try:
                    group = cursor.fetchone()[0]
                    cursor.close()
                    connect.close()
                except IndexError:
                    if message.chat.type == "private":
                        bot.send_message(message.from_user.id, f"{sm}У вас не указана группа\n"
                                                               f"/group, чтобы указать группу")
                    else:
                        bot.send_message(message.chat.id, f"{sm}У вас не указана группа\n/group (группа), чтобы указать"
                                                          f" группу")
                    return
                if group == "None":
                    if message.chat.type == "private":
                        bot.send_message(message.from_user.id, f"{sm}У вас не указана группа\n/group, чтобы указать "
                                                               f"группу")
                    else:
                        bot.send_message(message.chat.id, f"{sm}У вас не указана группа\n/group (группа), чтобы указать"
                                                          f" группу")
                    return
            except Exception as er:
                error_log(er)
                try:
                    if message.chat.type == "private":
                        bot.send_message(message.from_user.id,
                                         f"{sm}Не удается получить вашу группу\n/group, чтобы указать группу")
                    else:
                        bot.send_message(message.chat.id, f"{sm}Не удается получить вашу группу\n/group (группа), "
                                                          f"чтобы указать группу")
                except Exception as err:
                    error_log(err)
                return
            if "today" in message.text.lower() or commands[0] in message.text.lower():
                try:
                    res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/today")
                    lessons = res.json()
                    rez = "<b>Пары сегодня:\n</b>"
                    for i in lessons:
                        j, o = i['lesson'], i['time']
                        try:
                            rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>" \
                                   f"{get_time_ico(o['start'])}{o['start']} - {o['end']})</b>\n{j['name']} " \
                                   f"({j['type']})\n{get_teacher_ico(j['teacher'])} {j['teacher']}\n\n"
                        except Exception as er:
                            error_log(er)
                    if len(rez) > 50:
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, rez, parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, rez, parse_mode="HTML")
                    else:
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
                except Exception as er:
                    error_log(er)
                    if "line 1 column 1" in str(er):
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, f"{sm}<b>Сегодня воскресенье</b>", parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, f"{sm}<b>Сегодня воскресенье</b>", parse_mode="HTML")
            elif "tomorrow" in message.text.lower() or commands[1] in message.text.lower():
                try:
                    res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/tomorrow")
                    lessons = res.json()
                    rez = "<b>Пары завтра:\n</b>"
                    for i in lessons:
                        j, o = i['lesson'], i['time']
                        try:
                            rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>" \
                                   f"{get_time_ico(o['start'])}{o['start']} - {o['end']})</b>\n{j['name']} " \
                                   f"({j['type']})\n{get_teacher_ico(j['teacher'])} {j['teacher']}\n\n"
                        except Exception as er:
                            error_log(er)
                    if len(rez) > 50:
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, rez, parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, rez, parse_mode="HTML")
                    else:
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
                except Exception as er:
                    error_log(er)
                    if "line 1 column 1" in str(er):
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, f"{sm}<b>Завтра воскресенье</b>", parse_mode="HTML")
                        else:
                            bot.send_message(message.chat.id, f"{sm}<b>Завтра воскресенье</b>", parse_mode="HTML")
            elif "week" in message.text.lower() or commands[2] in message.text.lower():
                res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/week")
                lessons = res.json()
                rez, days = "", []
                try:
                    for i in lessons:
                        days.append(i)
                    days = sort_days(days)
                    for i in days:
                        rez += f"<b>{day_dict[i]}\n</b>"
                        for k in lessons[i]:
                            j, o = k['lesson'], k['time']
                            try:
                                rez += f"<b>{number_of_lesson(o['start'])} (<code>{j['classRoom']}</code>" \
                                       f"{get_time_ico(o['start'])}{o['start']} - {o['end']})</b>\n{j['name']} " \
                                       f"({j['type']})\n{get_teacher_ico(j['teacher'])} {j['teacher']}\n\n"
                            except Exception as er:
                                error_log(er)
                        rez += "------------------------\n"
                except Exception as er:
                    error_log(er)
                    try:
                        if message.chat.type == "private":
                            bot.send_message(message.from_user.id, f"{sm}А ой, ошиб04ка")
                        else:
                            bot.send_message(message.chat.id, f"{sm}А ой, ошиб04ка")
                    except Exception as err:
                        error_log(err)
                if len(rez) > 50:
                    if message.chat.type == "private":
                        bot.send_message(message.from_user.id, rez, parse_mode="HTML")
                    else:
                        bot.send_message(message.chat.id, rez, parse_mode="HTML")
                else:
                    if message.chat.type == "private":
                        bot.send_message(message.from_user.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
                    else:
                        bot.send_message(message.chat.id, f"{sm}<b>Пар не обнаружено</b>", parse_mode="HTML")
        else:
            bot.send_message(message.from_user.id, f"{sm}<b>Я вас не понял</b>", parse_mode="HTML")
    except Exception as er:
        error_log(er)


try:
    while True:
        try:
            bot.polling(none_stop=True, interval=0)  # обращение к api
        except Exception as e:
            print(e)
except Exception as e:
    print(e)
