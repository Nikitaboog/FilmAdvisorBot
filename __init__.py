try:
    import telebot
except ImportError:
    import os

    os.system("pip install pyTelegramBotAPI")
    os.system("pip install PySocks")
    import telebot
from telebot import *

import random

from bot.bot_info import *
from bot.imdbAPI import IMDBAPI, Movie

bot = telebot.TeleBot(token=token)
apihelper.proxy = PROXY


def create_markup(buttons):
    markup = types.ReplyKeyboardMarkup()
    for row in buttons:
        markup.row(*[types.KeyboardButton(text=button) for button in row])
    return markup


message_start = "This bot will help you to choose a film.\n" \
    "To start, choose start year of production."
message_get_end_year = "Now choose end year of production."
message_get_country = "Now choose country of production."
message_get_genre = "Now choose genre."
message_finalize = "Everything is ok. Results should appear shortly."

year_choices = [[str(1990 + x) for x in range(5 * y + 1, 5 * (y + 1) + 1)] for y in range(6)]
country_choices = [["Russia", "United States", "Other"]]
genre_choices = [
    ["Action", "Adventure", "Biography", "Comedy"],
    ["Crime", "Documentary", "Drama", "Family"],
    ["Fantasy", "Film-Noir", "History", "Horror"],
    ["Musical", "Mystery", "Romance", "Sci-Fi"],
    ["Sport", "Thriller", "War", "Western"]]

user_input = {}
imdb = IMDBAPI()


@bot.message_handler(commands=['start'])
def start(message):
    user_input[message.chat.id] = {}
    markup = create_markup(year_choices)
    msg = bot.send_message(message.chat.id, message_start, reply_markup=markup)
    bot.register_next_step_handler(msg, get_end_year)


def get_end_year(message):
    try:
        user_input[message.chat.id]["start_year"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Not a valid number")
        start(message)
        return
    markup = create_markup(year_choices)
    msg = bot.send_message(message.chat.id, message_get_end_year, reply_markup=markup)
    bot.register_next_step_handler(msg, get_country_category)


def get_country_category(message):
    try:
        user_input[message.chat.id]["end_year"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Not a valid number")
        start(message)
        return
    markup = create_markup(country_choices)
    msg = bot.send_message(message.chat.id, message_get_country, reply_markup=markup)
    bot.register_next_step_handler(msg, get_genre)


def get_genre(message):
    user_input[message.chat.id]["country"] = message.text
    markup = create_markup(genre_choices)
    msg = bot.send_message(message.chat.id, message_get_genre, reply_markup=markup)
    bot.register_next_step_handler(msg, finalize)


def finalize(message):
    user_input[message.chat.id]["genre"] = message.text
    bot.send_message(message.chat.id, message_finalize)
    movies = imdb.present_movie(*user_input[message.chat.id].values())
    if len(movies) == 0:
        bot.send_message(message.chat.id, "Sorry, no results found.")
    else:
        random.shuffle(movies)
        if len(movies) > 3:
            movies = movies[:3]
        for movie in movies:
            answer = "*{}*\n".format(movie.name)
            answer += "*Year:* " + str(movie.year) + "\n"
            answer += "*Country:* " + ", ".join(movie.country) + "\n"
            answer += "*Genres:* " + ", ".join(movie.category) + "\n"
            answer += "*Producer:* " + movie.producer + "\n"
            answer += "*Description:*\n" + movie.description.split("::")[0]
            print(answer)
            bot.send_message(message.chat.id, answer, parse_mode="Markdown")

    bot.send_message(message.chat.id, "You can start again by sending \"/start\"")


if __name__ == '__main__':
    imdb.initialise()
    print("Bot starts")
    bot.polling(none_stop=True)
