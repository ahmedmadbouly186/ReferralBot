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
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]
creds=Credentials.from_service_account_file('credentials.json', scopes=scopes)
client =gspread.authorize(creds)
# Read sheet URL from environment (.env)
sheet_url = os.getenv('SHEET_URL')
sheet = client.open_by_url(sheet_url)

# Select the specific worksheet you want to append to
users = sheet.worksheet("users") 
constants=sheet.worksheet("constants")
data = constants.get_all_records()
constants_map = {row["constant_name"]: row["value"] for row in data}

# # Your bot's API token
bot_token = constants_map['bot_token']

# # Chat ID or username (e.g., @channelusername or channel ID)
chat_id = constants_map['chat_to_invite_id']

now = int(time.time())

after_3_minutes = now + int(constants_map['time_limit_to_acctept_invitation'])*60

# # Create the invite link
url = f'https://api.telegram.org/bot{bot_token}/createChatInviteLink'

params = {
    'chat_id': chat_id,
    'expire_date': after_3_minutes,  # Expiry time as Unix timestamp
    'member_limit': 1,               # Optional: Set the member limit
    'creates_join_request': False,    # Optional: Set to True if users need admin approval
    'name': 'Special Invite Link',    # Optional: Invite link name
}

response = requests.post(url, data=params)

# Check the response
if response.status_code == 200:
    result = response.json()
    print(f"Invite Link: {result['result']['invite_link']}")
else:
    print(f"Error: {response.text}")
