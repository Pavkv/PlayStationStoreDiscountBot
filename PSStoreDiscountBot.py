import sqlite3
import requests
from telebot import TeleBot, types
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Define global variables
DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('TELEGRAM_TOKEN')
API_URL = "https://platprices.com/api.php"

# Initialize bot
bot = TeleBot(TOKEN)

# Configure logging
logging.basicConfig(filename='PSStoreBot.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def log_info(message, type):
    """
    Logs an info message.

    Parameters:
    message (str): The message to log.
    type (str): The type of the log message. Can be 'error' or 'success'.

    Returns:
    str: The logged message.
    """
    if type == 'error':
        logging.error(message)
    else:
        logging.info(message)

    return message


def collect_game_data(data):
    """Collects game data from the API response."""
    return [data['ProductName'], data['formattedBasePrice']]


def get_game_data_from_api(game_name):
    """
    Fetches game data from the API.

    Parameters:
    game_name (str): The name of the game to fetch data for.

    Returns:
    dict: The game data if found, else an error message.
    """
    response = requests.get(f"{API_URL}?key={API_KEY}&name={game_name}")
    data = response.json()
    if not data:
        return log_info(f'Game was not found or incorrect name provided: {game_name}', 'error')
    return data


def add_game_to_database(game_name):
    """
    Adds a game to the database if it's not already present.

    Parameters:
    game_name (str): The name of the game to add to the database.

    Returns:
    str: A success message if the game was added, else an error message.
    """
    data = get_game_data_from_api(game_name)

    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        game = data['ProductName']
        cursor.execute("SELECT Game_Name FROM GAMES WHERE Game_Name = ?", (game,))
        if cursor.fetchone():
            return log_info(f'{game} is already in your wishlist.', 'error')
        cursor.execute("INSERT INTO GAMES (Game_Name, Base_Price) VALUES (?, ?)", (game,
                                                                                   data['formattedBasePrice']))
        return log_info(f'{game} was successfully added to your wishlist.', 'success')


def delete_game_from_database(game_name):
    """
    Deletes a game from the database.

    Parameters:
    game_name (str): The name of the game to delete from the database.

    Returns:
    str: A success message if the game was deleted, else an error message.
    """
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM GAMES WHERE Game_Name LIKE ?", ('%' + game_name + '%',))
        if cursor.rowcount > 0:
            return log_info(f'{game_name} was successfully deleted from your wishlist.', 'success')
        return log_info(f'{game_name} was not found in your wishlist.', 'error')


def setup_discount_check_scheduler():
    """
    Sets up a scheduled job to check for discounts.
    The job is scheduled to run every Monday at 13:00 UTC.
    """
    scheduler = BlockingScheduler()

    def scheduled_discount_check():
        """Executes discount checks for all users."""
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM USER_IDS")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                discount_message = check_for_discounts()
                bot.send_message(user_id[0], discount_message)

        scheduler.add_job(scheduled_discount_check, 'cron', day_of_week='mon', hour=13, timezone='UTC')
        scheduler.start()


class User:
    def __init__(self, user_name, user_id):
        """
        Initializes a new User object.

        Parameters:
        user_name (str): The name of the user.
        user_id (int): The ID of the user.
        """
        self.user_name = user_name
        self.user_id = user_id

    def check_user(self):
        """
        Check if the user exists in the database, and add them if not.
        """
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM USER_IDS WHERE user_id = ?", (self.user_id,))
            user = cursor.fetchone()
            if not user:
                self.add_user()

    def add_user(self):
        """
        Adds the user to the database.
        """
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO USER_IDS (user_id, user_name) VALUES (?, ?)", (self.user_id, self.user_name))


def process_name_step(message):
    """
    Processes the name step and presents the initial menu to the user.

    Parameters:
    message (Message): The message received from the user.
    """
    try:
        user_id = message.chat.id
        user_name = message.from_user.first_name + (message.from_user.last_name or '')
        user = User(user_name, user_id)
        user.check_user()
        options = ['Add new game', 'Delete game', 'Check discount']
        start_menu = types.ReplyKeyboardMarkup(row_width=1)
        for option in options:
            start_menu.add(types.KeyboardButton(text=option))

        bot.reply_to(message, 'What would you like to do?', reply_markup=start_menu)
    except Exception as e:
        bot.reply_to(message, log_info(f'An error occurred: {e}', 'error'))


def add_new_game(message):
    """
    Adds a new game based on user input.

    Parameters:
    message (Message): The message received from the user.
    """
    if message.text:
        response = add_game_to_database(message.text)
        bot.reply_to(message, response)


def delete_game(message):
    """
    Deletes a game based on user input.

    Parameters:
    message (Message): The message received from the user.
    """
    if message.text:
        response = delete_game_from_database(message.text)
        bot.reply_to(message, response)


def check_for_discounts():
    """
    Checks for discounts on all games in the database.

    Returns:
    str: A message containing all the discounts, or a message saying there are no current discounts.
    """
    discount_messages = []
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        for game_name, in cursor.execute("SELECT Game_Name FROM GAMES"):
            game_data = get_game_data_from_api(game_name)
            if game_data and game_data['formattedBasePrice'] != game_data['formattedSalePrice']:
                discount_messages.append(f'{game_data["ProductName"]} is on sale until {game_data["DiscountedUntil"]} '
                                         f'for {game_data["formattedSalePrice"]}/{game_data["formattedBasePrice"]}')
    return log_info('\n'.join(discount_messages) if discount_messages else 'No current discounts.', 'success')


def main():
    """
    The main function that starts the bot and sets up the message handlers.
    """
    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(message):
        """Sends a welcome message and prompts for user registration."""
        bot.send_message(message.chat.id, log_info('Welcome to PS Store Bot! Please enter your name.', 'success'))
        bot.register_next_step_handler(message, process_name_step)

    @bot.message_handler(content_types=["text"])
    def choose_button(message):
        """
        Handles user response from the initial menu.

        Parameters:
        message (Message): The message received from the user.
        """
        text_map = {
            'Add new game': add_new_game,
            'Delete game': delete_game,
            'Check discount': lambda msg: bot.reply_to(msg, check_for_discounts())
        }

        try:
            if message.text in text_map:
                action = text_map[message.text]
                if action == add_new_game or action == delete_game:
                    bot.send_message(message.chat.id, log_info('Please enter the name of the game.', 'success'))
                    bot.register_next_step_handler(message, action)
                else:
                    action(message)
            else:
                bot.reply_to(message, log_info('Please choose a valid option.', 'error'))
        except Exception as e:
            bot.reply_to(message, log_info(f'An error occurred: {e}', 'error'))


if __name__ == '__main__':
    main()
    setup_discount_check_scheduler()
    bot.infinity_polling()
