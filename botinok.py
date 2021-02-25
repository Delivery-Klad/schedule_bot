import telebot
import requests

bot = telebot.TeleBot("1695146161:AAEcW2Rk2Fo39dGGMvnx2Kkz7qZ_4iFygx4")
sm = "🤖"
print(bot.get_me())


@bot.message_handler(commands=['start'])
def handler_exec(message):
    bot.send_message(message.from_user.id, "/today <группа> - расписание на сегодня\n"
                                           "/tomorrow <группа> - расписание на завтра\n"
                                           "/week <группа> - расписанире на неделю")


@bot.message_handler(content_types=['text'])
def handler_text(message):
    print(str(message.from_user.id) + " " + message.text)
    if message.text[0] == "/":
        try:
            group = message.text.split(" ", 1)[1]
        except IndexError:
            return
        if "today" in message.text:
            res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/today")
            lessons = res.json()
            rez = ""
            for i in lessons:
                j = i['lesson']
                o = i['time']
                try:
                    rez += f"Аудитория: {j['classRoom']}\nНазвание: {j['name']}\nПреподаватель: {j['teacher']}\n" \
                           f"Тип: {j['type']}\nВремя: {o['start']} - {o['end']}\n\n"
                except TypeError:
                    pass
            try:
                bot.send_message(message.from_user.id, rez)
            except Exception as e:
                if "empty" in str(e):
                    bot.send_message(message.from_user.id, "Пар не обнаружено")
        elif "tomorrow" in message.text:
            res = requests.get(f"https://schedule-rtu.rtuitlab.dev/api/schedule/{group}/tomorrow")
            lessons = res.json()
            rez = ""
            for i in lessons:
                j = i['lesson']
                o = i['time']
                try:
                    rez += f"Аудитория: {j['classRoom']}\nНазвание: {j['name']}\nПреподаватель: {j['teacher']}\n" \
                           f"Тип: {j['type']}\nВремя: {o['start']} - {o['end']}\n\n"
                except TypeError:
                    pass
            try:
                bot.send_message(message.from_user.id, rez)
            except Exception as e:
                if "empty" in str(e):
                    bot.send_message(message.from_user.id, "Пар не обнаружено")
        elif "week" in message.text:
            pass


try:
    while True:
        try:
            bot.polling(none_stop=True, interval=0)  # обращение к api
        except Exception as e:
            pass
except Exception as e:
    print(e)
