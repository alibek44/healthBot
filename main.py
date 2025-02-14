import base64
import random
import requests
import telebot
from openai import (OpenAI)
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import threading
import time
from datetime import datetime, timedelta
import json
import os

#reading keys from json file
with open("kick.json", "r") as json_file:
    a = json.load(json_file)

with open("token.json", "r") as f:
    key=json.load(f)

OPENAI_API_KEY=key["Open_AI_key"]
client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_TOKEN = a["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_TOKEN)
#dictionaries to store data
user_bmi_data = {}
user_challenges = {}
user_data = {}
reminders = {}
CHALLENGES_FILE = "challenges.json"
DATA_FILE = "challenges.json"

def load_challenges():
    if os.path.exists(CHALLENGES_FILE):
        with open(CHALLENGES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_challenges(challenges):
    with open(CHALLENGES_FILE, "w", encoding="utf-8") as file:
        json.dump(challenges, file, indent=4, ensure_ascii=False)

#chalanges dictionary
challenges = [
    "Сделать 100 отжиманий",
    "Сделать 100 приседаний",
    "Сделать 50 подтягиваний",
    "Пробежать 5 км",
    "Встать в планку на 5 минут",
    "Отказаться от сладкого на 3 дня",
    "Сделать 200 прыжков на скакалке",
    "Пройти 10 000 шагов за день"
]

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
#check for active reminders and reminding them
def reminder_checker():
    while True:
        now = datetime.now()
        for user_id, user_reminders in list(reminders.items()):
            for reminder in user_reminders:
                reminder_time, message = reminder
                if now >= reminder_time:
                    bot.send_message(user_id, f"⏰ Напоминание: *{message}*")
                    reminders[user_id].remove(reminder)
            if not reminders[user_id]:
                del reminders[user_id]
        time.sleep(30)
#welcome message
@bot.message_handler(commands=['start'])
def start_message(message: Message):
    bot.send_message(
        message.chat.id,
        "👋 *Привет!* Я бот, который поможет тебе с тренировками и челленджами! 🎯\n\n"
        "📝 Помоги нам стать лучше, напиши отзыв сюда /reviews !\n"
        "📌 Также я могу напоминать тебе о тренировках. Напиши 'Установить напоминание'!"
    )
    bot.send_message(message.chat.id, "Как вас зовут?")
    user_data[message.chat.id] = {"name": message.text}
    bot.register_next_step_handler(message, func)

#Buttons
def func(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("📊 Рассчитать ИМТ")
    btn2 = KeyboardButton("⏰ Установить напоминание")
    btn3 = KeyboardButton("📸 Фото еды")
    btn4 = KeyboardButton("🔥 Челлендж дня")
    btn5 = KeyboardButton("🔥 Твои челленджы")
    btn6 = KeyboardButton("📉 Ваш ИМТ сейчас")

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, "👇 Выберите действие:", reply_markup=markup)

#fuction that counts bmi
@bot.message_handler(func=lambda message: message.text == "📊 Рассчитать ИМТ")
def ask_height(message: Message):
    bot.send_message(message.chat.id, "📏 Введите ваш *рост* (в см):")
    bot.register_next_step_handler(message, ask_weight)

def ask_weight(message: Message):
    try:
        height = float(message.text)

        if message.chat.id not in user_data:
            user_data[message.chat.id] = {}

        user_data[message.chat.id]["height"] = height  #saving user height
        bot.send_message(message.chat.id, "⚖️ Теперь введите ваш *вес* (в кг):")
        bot.register_next_step_handler(message, calculate_bmi)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите *число* для роста (например: 175).")
        bot.register_next_step_handler(message, ask_weight)

def calculate_bmi(message: Message):
    try:
        weight = float(message.text)
        user_data[message.chat.id]["weight"] = weight  #saving user weight
        height = user_data[message.chat.id]["height"] / 100
        bmi = weight / (height ** 2)

        #saving user bmi
        user_bmi_data[message.chat.id] = bmi
        #checking bmi for recommendations
        if bmi < 18.5:
            status = "🔹 У вас *недостаток веса*. Рекомендуем проконсультироваться с врачом."
        elif 18.5 <= bmi <= 24.9:
            status = "✅ Ваш вес *в норме*! Отличный результат, продолжайте в том же духе!"
        elif 25 <= bmi <= 29.9:
            status = "⚠️ У вас *избыточный вес*. Подумайте о сбалансированном питании и физической активности."
        else:
            status = "🚨 У вас *ожирение*. Рекомендуем обратиться к специалисту для составления плана питания и тренировок."

        bot.send_message(
            message.chat.id,
            f"🧮 Ваш *ИМТ*: `{bmi:.2f}`\n\n{status}"
        )
    except ValueError:   #error handling
        bot.send_message(message.chat.id, "❌ Введите корректное *число* для веса.")
        bot.register_next_step_handler(message, calculate_bmi)


def userBMI(message: Message):
    bmi = user_bmi_data.get(message.chat.id)

    if bmi:
        bot.send_message(
            message.chat.id,
            f"📉 Ваш последний *ИМТ*: `{bmi:.2f}`\n\n"
            "Если ваш вес изменился, рекомендуется пересчитать ИМТ."
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ У вас пока нет сохраненного ИМТ. Рассчитайте его с помощью кнопки *📊 Рассчитать ИМТ*."
        )


@bot.message_handler(func=lambda message: message.text == "📉 Ваш ИМТ сейчас")
def handle_bmi_now(message: Message):
    bmi = user_bmi_data.get(message.chat.id)  # Get saved BMI
    user_info = user_data.get(message.chat.id)  # Get user height & weight

    if bmi and user_info:
        height = user_info.get("height")  #passing height value
        weight = user_info.get("weight")  #passing weight value
        bot.send_message(
            message.chat.id,
            f"📊 Ваш последний *ИМТ*: `{bmi:.2f}`\n\n"
            f"📏 Ваш *рост*: `{height} см`\n"
            f"⚖️ Ваш *вес*: `{weight} кг`\n\n")
    elif not bmi:  #error handling
        bot.send_message(message.chat.id,"У вас пока нет сохраненного ИМТ. Рассчитайте его с помощью кнопки *📊 Рассчитать ИМТ*.")
#function that sets reminders
@bot.message_handler(func=lambda message: message.text == "⏰ Установить напоминание")
def set_reminder_prompt(message: Message):   #asking user to set reminder
    bot.send_message(
        message.chat.id,
        "⏳ Введите напоминание в формате: `HH:MM Текст напоминания`\n\n"
        "📌 *Пример:* `07:30 Утренняя тренировка`"
    )
    bot.register_next_step_handler(message, set_reminder)

def set_reminder(message: Message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: #error handling
            bot.send_message(message.chat.id, "❌ *Ошибка!* Используйте формат: `HH:MM Тренировка в зале`")
            return

        time_str, reminder_text = parts[0], parts[1]
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time)

        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)

        user_id = message.chat.id
        if user_id not in reminders:
            reminders[user_id] = []
        reminders[user_id].append((reminder_datetime, reminder_text))

        bot.send_message(user_id, f"✅ Напоминание установлено на *{time_str}*: _{reminder_text}_")
    except ValueError:  #error handling
        bot.send_message(message.chat.id, "❌ *Ошибка!* Используйте формат: `HH:MM Текст`.")
#funtion that counts kcal by uploaded photo using AI
@bot.message_handler(func=lambda message: message.text == "📸 Фото еды")
def welcome(message: Message):
    bot.send_message(message.chat.id, "Отправте фото еды")
@bot.message_handler(content_types=['photo']) #take an uploaded photo
def photo_kcal(message):
    if message.photo:
        file_id = message.photo[-1].file_id  #getting photo id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"  #photo url
    else:
        bot.send_message(message.chat.id, "⚠️ Пожалуйста, отправьте фото, а не текст!")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = requests.get(file_url)
    if response.status_code != 200:
        bot.send_message(message.chat.id, "⚠️ Ошибка при загрузке изображения!")
        return

    image_data = base64.b64encode(response.content).decode("utf-8")   #encoding photo to base64
#analyzing photo with chatGPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Estimate the calories in this food. Give the answer on russian and be precise.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ],
    )
    analysis = str(response.choices[0].message.content).strip()
    bot.send_message(message.chat.id, f"📸 Анализ изображения: {analysis}")
#funtion that gives challenges
@bot.message_handler(func=lambda message: message.text == "🔥 Челлендж дня")
def give_challenge(message):
    user_id = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    #check if user not in dictionary
    if user_id not in user_data:
        user_data[user_id] = {"active": [], "completed": [], "last_challenge_date": "", "challenge_count": 0}

    if user_data[user_id]["last_challenge_date"] == today and user_data[user_id]["challenge_count"] >= 3:
        bot.send_message(user_id, "⚠ Ты уже взял 3 челленджа на сегодня! Попробуй завтра 💪")
        return

    available_challenges = [ch for ch in challenges if ch not in user_data[user_id]["active"]]

    challenge = random.choice(available_challenges)
    user_data[user_id]["active"].append(challenge)
    user_data[user_id]["last_challenge_date"] = today
    user_data[user_id]["challenge_count"] += 1

    save_data()

    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{challenge}")
    markup.add(button)

    bot.send_message(user_id, f"🔥 Твой челлендж: {challenge}\n\n"
                              "Когда ты его выполнишь, нажми на кнопку ниже 👇", reply_markup=markup)

#saving completed challenge
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def complete_challenge(call):
    user_id = str(call.message.chat.id)
    challenge = call.data[5:]

    if user_id in user_data and challenge in user_data[user_id]["active"]:
        user_data[user_id]["active"].remove(challenge)
        user_data[user_id]["completed"].append(challenge)
        save_data()

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"✅ Челлендж выполнен: {challenge} 💪")
#funtion that shows your challenges
@bot.message_handler(func=lambda message: message.text == "🔥 Твои челленджы")
def list_challenges(message):
    user_id = str(message.chat.id)
    active = user_data.get(user_id, {}).get("active", [])  #getting active challenges
    completed = user_data.get(user_id, {}).get("completed", [])  #getting completed challenges

    response = "📋 *Твои челленджи:*\n\n"

    if active:
        response += "🔥 *Активные челленджи:*\n" + "\n".join([f"▪ {ch}" for ch in active]) + "\n\n"
    else:
        response += "🔥 *Активные челленджи:* Нет активных челленджей.\n\n"

    if completed:
        response += "✅ *Выполненные челленджи:*\n" + "\n".join([f"✔ {ch}" for ch in completed])
    else:
        response += "✅ *Выполненные челленджи:* Пока нет выполненных челленджей."

    bot.send_message(user_id, response, parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target= reminder_checker, daemon=True).start()
    bot.polling(none_stop=True)