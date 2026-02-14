import telebot
import random
import threading

API_TOKEN = '8551978188:AAHRZj47tvkiqVz9ZLSOKdCLnZPiu0XW-G4'
bot = telebot.TeleBot(API_TOKEN)

# Состояния
lobbies = {}

# Темы
themes = {
    "Знаменитости": [
        "Эпштейн", "Адольф Гитлер", "Павел Дуров", "Саша Фокин", "Саша Грей",
        "Ева Элфи", "Макс Корж", "Сэм Альтман", "Сатоши Накамото", "Моргенштерн",
        "Слава Мэрлоу", "Группа Горох", "Джордж Флойд", "Чарли Кирк",
        "Владимир Путин", "Сталин", "Ленин", "Трамп", "Обэма"
    ]
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Используй /create для создания лобби.")

@bot.message_handler(commands=['create'])
def create_lobby(message):
    user_id = message.from_user.id
    lobby_key = str(random.randint(10000, 99999))
    lobbies[lobby_key] = {
        "creator": user_id,
        "players": [user_id],
        "theme": None,
        "current_word": None,
        "spy": None,
        "status": "waiting"
    }
    bot.reply_to(message, f"Лобби создано! Ключ: {lobby_key}\nОтправь его друзьям для присоединения.\n\nКоманды:\n/start_game — начать игру\n/end_round — завершить раунд\n/close_lobby — закрыть лобби")

@bot.message_handler(commands=['join'])
def join_lobby(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Укажите ключ лобби: /join <ключ>")
        return
    key = args[1]
    user_id = message.from_user.id
    if key not in lobbies:
        bot.reply_to(message, "Лобби не найдено.")
        return
    if lobbies[key]["status"] != "waiting":
        bot.reply_to(message, "Игра уже началась!")
        return
    if user_id in lobbies[key]["players"]:
        bot.reply_to(message, "Вы уже в лобби.")
        return
    lobbies[key]["players"].append(user_id)
    bot.reply_to(message, f"Вы присоединились к лобби {key}")

@bot.message_handler(commands=['start_game'])
def start_game(message):
    user_id = message.from_user.id
    lobby = None
    for k, v in lobbies.items():
        if v["creator"] == user_id and v["status"] == "waiting":
            lobby = k
            break
    if not lobby:
        bot.reply_to(message, "Вы не создатель активного лобби.")
        return

    players = lobbies[lobby]["players"]
    if len(players) < 2:
        bot.reply_to(message, "Недостаточно игроков (минимум 3).")
        return

    theme_name = "Знаменитости"
    word = random.choice(themes[theme_name])
    spy = random.choice(players)

    lobbies[lobby]["theme"] = theme_name
    lobbies[lobby]["current_word"] = word
    lobbies[lobby]["spy"] = spy
    lobbies[lobby]["status"] = "playing"

    for player_id in players:
        if player_id == spy:
            bot.send_message(player_id, f"Вы шпион!")
        else:
            bot.send_message(player_id, f"Слово: {word}")

    bot.reply_to(message, "Игра началась! Игроки получили свои роли.")

@bot.message_handler(commands=['end_round'])
def end_round(message):
    user_id = message.from_user.id
    lobby = None
    for k, v in lobbies.items():
        if v["creator"] == user_id and v["status"] == "playing":
            lobby = k
            break
    if not lobby:
        bot.reply_to(message, "Вы не создатель активного лобби.")
        return

    players = lobbies[lobby]["players"]
    old_spy = lobbies[lobby]["spy"]
    new_spy = random.choice(players)
    while new_spy == old_spy:
        new_spy = random.choice(players)

    word = random.choice(themes[lobbies[lobby]["theme"]])

    lobbies[lobby]["current_word"] = word
    lobbies[lobby]["spy"] = new_spy

    for player_id in players:
        if player_id == new_spy:
            bot.send_message(player_id, f"Вы шпион!")
        else:
            bot.send_message(player_id, f"Слово: {word}")

    bot.reply_to(message, "Раунд завершён. Новые роли и слово выданы.")

@bot.message_handler(commands=['close_lobby'])
def close_lobby(message):
    user_id = message.from_user.id
    lobby = None
    for k, v in lobbies.items():
        if v["creator"] == user_id:
            lobby = k
            break
    if not lobby:
        bot.reply_to(message, "Вы не создатель лобби.")
        return

    del lobbies[lobby]
    bot.reply_to(message, "Лобби закрыто.")

bot.polling(none_stop=True)