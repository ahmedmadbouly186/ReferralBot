import os
import telebot
import gspread
from google.oauth2.service_account import Credentials
import threading
from threading import Timer
from datetime import datetime, timedelta
from threading import Thread
import heapq
import time
import random
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
from dotenv import load_dotenv

load_dotenv()

scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]
creds=Credentials.from_service_account_file('credentials.json', scopes=scopes)
client =gspread.authorize(creds)
# Read sheet URL from environment (from .env)
sheet_url = os.getenv('SHEET_URL')
sheet = client.open_by_url(sheet_url)

# Select the specific worksheet you want to append to
worksheet = sheet.get_worksheet(0)  # 0 refers to the first sheet/tab in the Google Sheets document


API_KEY = os.getenv('API_KEY')
print(API_KEY)
bot = telebot.TeleBot(API_KEY)


class Promotion():
    def __init__(self, message,post_date,post_time):
        self.message = message
        self.post_date = post_date
        self.post_time = post_time
        # Convert date and time into a datetime object for comparison
        self.post_datetime = datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M:%S")

    def __lt__(self, other):
        # This will ensure the priority queue sorts by the earliest date and time
        return self.post_datetime < other.post_datetime
    
    def is_upcoming(self):
        # Check if the promotion's date and time is in the future (upcoming)
        return self.post_datetime > datetime.now()
Giveaway_id = 1
class Giveaway():
    def __init__(self,title, message,duration,post_date,post_time):
        # use the global variable to increment the id
        global Giveaway_id
        days, hours, minutes = map(int, duration.split('-'))
        self.duration = timedelta(days=days, hours=hours, minutes=minutes)

        self.title = title
        self.message = message
        self.post_date = post_date
        self.post_time = post_time
        self.winner = None
        self.participants = []  

        # Convert date and time into a datetime object for comparison
        self.post_datetime = datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M:%S")
        self.end_datetime = self.post_datetime + self.duration  # End time is post time + duration
        self.id = Giveaway_id
        Giveaway_id+=1

    def __lt__(self, other):
        # This will ensure the priority queue sorts by the earliest date and time
        return self.post_datetime < other.post_datetime
    
    def is_upcoming(self):
        # Check if the promotion's date and time is in the future (upcoming)
        return self.post_datetime > datetime.now()
    def is_ended(self):
        return self.end_datetime < datetime.now()
    def add_participant(self, user_name):
        if user_name not in self.participants:
            self.participants.append(user_name)
            return True
        return False  # Return False if user already joined
    def choose_winner(self):
        if(self.winner):
            return self.winner
        if self.participants:
            self.winner = random.choice(self.participants)
            return self.winner
        print(f"No participants found for giveaway {self.id}")
        return None
    

promotions_queue = []
Giveaways_queue = []
posted_giveaways = []
def add_promotion():
    # Taking message, date and time as input
    message = input("Enter the promotion message: ")
    post_date = input("Enter the promotion date (YYYY-MM-DD): ")
    post_time = input("Enter the promotion time (HH:MM:SS): ")

    # Create a new promotion object
    promotion = Promotion(message, post_date, post_time)

    # Check if the promotion is upcoming
    if promotion.is_upcoming():
        print(f"The promotion '{promotion.message}' is upcoming.")
    else:
        print(f"The promotion '{promotion.message}' is already in the past.")
        return
    print("---------------------------------")
    # Push the promotion into the priority queue
    heapq.heappush(promotions_queue, promotion)

def add_give_away():
    # Infinite loop to take user input
    title = input("Enter the give away title: ")
    message = input("Enter the give away message: ")
    duration = input("Enter the duration of the giveaway in 'days-hours-minutes' format: ")
    post_date = input("Enter the give away date (YYYY-MM-DD): ")
    post_time = input("Enter the give away time (HH:MM:SS): ")
    
    # create a new give away object
    give_away = Giveaway(title, message, duration, post_date, post_time)
    
    # Check if the promotion is upcoming
    if give_away.is_upcoming():
        print(f"The give_away '{give_away.message}' is upcoming.")
    else:
        print(f"The give_away '{give_away.message}' is already in the past.")
        return
    print("---------------------------------")
    # Push the promotion into the priority queue
    heapq.heappush(Giveaways_queue, give_away)

def select_winner():
    give_away_id = input("Enter the give away ID: ")
    winner_name = input("Enter the winner name: ")
    find = False
    for giveaway in posted_giveaways:
        if giveaway.id == int(give_away_id):
            find = True
            giveaway.winner = winner_name
            return
    for giveaway in Giveaways_queue:
        if giveaway.id == int(give_away_id):
            find = True
            giveaway.winner = winner_name
            return
    if not find:
        print("Giveaway id not found")
    

def take_input():
    # Infinite loop to take user input
    while True:
        # take p or q as input
        choice = input("")
        if choice == "1":
            add_give_away()
        elif choice == "2":
            select_winner()
        elif choice == "3":
            add_promotion()
        # else:
        #     # set all posted giveaways to ended
        #     for giveaway in posted_giveaways:
        #         giveaway.end_datetime = datetime.now()
@bot.message_handler(commands=['start'])
def start(message):
        # Extract user details
    first_name = message.from_user.first_name or "No Name"

    user_id = str(message.from_user.id)  
    username = message.from_user.username or "User"
    print(f"User ID: {user_id}, Username: {username}")
    print("name: ",first_name)
    bot.send_message(message.chat.id, f"Hello {username} in our giveways bot, enjoy your time with us.")
    # Check if the first value already exists in the sheet
    existing_values = worksheet.col_values(1)  # Assuming the first column contains the IDs
    if user_id not in existing_values:
        # Append the row if the first value is not found
        worksheet.append_row([user_id, username])
        print(f"id: {user_id},username: {username} appended successfully.")
        print("---------------------------------")
    else:
        print(f"id: {user_id},username: {username} this user already exists in the sheet.")
        print("---------------------------------")


def send_promotions(message_text):
    # Get the current date and time to create a unique sheet title
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH-MM-SS
    log_sheet_title = f"Promotion Log {current_time}"

    # Create a new sheet for logging with the current date and time in the title
    log_sheet = sheet.add_worksheet(title=log_sheet_title, rows="100", cols="3")
    log_sheet.append_row(["Chat ID", "Status", "Message"])

    # Retrieve all user chat IDs from the sheet
    chat_ids = worksheet.col_values(1)[1:]  # Skip the header row if there is one
    failed_chat_ids = []  # List to store failed chat IDs
    successful_chat_ids = []  # List to store successful chat IDs

    for chat_id in chat_ids:
        try:
            # Attempt to send the message
            bot.send_message(chat_id, message_text)
            successful_chat_ids.append(chat_id)  # Store successful chat ID
            # Log successful delivery in the new sheet
            log_sheet.append_row([chat_id, "Success", message_text])
        except Exception as e:
            failed_chat_ids.append(chat_id)  # Store failed chat ID
            # Log failed delivery in the new sheet
            log_sheet.append_row([chat_id, "Failed", str(e)])
        # Count the total successes and failures
    total_successes = len(successful_chat_ids)
    total_failures = len(failed_chat_ids)

    # Append a summary row at the end of the sheet
    log_sheet.append_row(["Total Successes", total_successes])
    log_sheet.append_row(["Total Failures", total_failures])

def send_giveaway(give_away: Giveaway):

    chat_ids = worksheet.col_values(1)[1:]  # Skip the header row if there is one
    message = f"Giveaway ID: {give_away.id}\nGIveaway title:{give_away.title}\n{give_away.message}\n\nthis giveaway will end in {give_away.duration.days} days, {give_away.duration.seconds//3600} hours, {give_away.duration.seconds%3600//60} minutes.\nyou could join by typing /join_giveaway {give_away.id}"
    for chat_id in chat_ids:
        try:
            # Attempt to send the message
            bot.send_message(chat_id, message)
        except Exception as e:
            print(e)
def send_message(message_text):
    chat_ids = worksheet.col_values(1)[1:]  # Skip the header row if there is one
    for chat_id in chat_ids:
        try:
            # Attempt to send the message
            bot.send_message(chat_id, message_text)
        except Exception as e:
            print(e)

def broadcast():
    while True:
        if Giveaways_queue:
            next_giveaway = heapq.heappop(Giveaways_queue)
            if next_giveaway.is_upcoming()==False:
                send_giveaway(next_giveaway)
                posted_giveaways.append(next_giveaway)
                print(f"Posted giveaway: {next_giveaway.title}")
                print("---------------------------------")
            else:
                heapq.heappush(Giveaways_queue, next_giveaway)
        if posted_giveaways:
            for giveaway in posted_giveaways:
                if giveaway.is_ended():
                    winner = giveaway.choose_winner()
                    if winner:
                        send_message(message_text=f"Winner of giveaway id: {giveaway.id}\ntitle: {giveaway.title}:\n @{winner}")
                    posted_giveaways.remove(giveaway)
                    print(f"Giveaway {giveaway.title} has ended.")
                    print("---------------------------------")
        # Check if there are promotions in the queue
        if promotions_queue:
            # Get the next upcoming promotion
            next_promotion = heapq.heappop(promotions_queue)
            # Check if the promotion is upcoming
            if next_promotion.is_upcoming()==False:
                # Send the promotion message to all users
                send_promotions(next_promotion.message)
                print(f"Broadcasted promotion: {next_promotion.message}")
                print("---------------------------------")
            else:
                # If the promotion is still upcoming, push it back into the queue
                heapq.heappush(promotions_queue, next_promotion)
        # Wait for 10 seconds before checking the queue again
        time.sleep(10) 

@bot.message_handler(commands=['join_giveaway'])
def join_giveaway(message):
    user_id = message.from_user.id
    user_name = message.from_user.username or "User"
    try:
        # Extract giveaway ID from the message text, e.g., "/join_giveaway 1"
        giveaway_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Please provide a valid giveaway ID. Usage: /join_giveaway <giveaway_id>")
        return

    # Find the giveaway in the queue by ID
    for giveaway in posted_giveaways:
        if giveaway.id == giveaway_id:
            if giveaway.add_participant(user_name):
                bot.send_message(message.chat.id, f"You have successfully joined the giveaway {giveaway.title}!")
                print(f"User {user_id} joined giveaway {giveaway_id}")
            else:
                bot.send_message(message.chat.id, "You have already joined this giveaway.")
            return

    bot.send_message(message.chat.id, "No giveaway found with the provided ID.")

t = Thread(target=broadcast)
t.start()
promotion_thread = Thread(target=take_input)
promotion_thread.start()
# Start polling for bot commands
bot.polling(non_stop=True)
