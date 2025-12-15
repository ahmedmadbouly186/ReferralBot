import telebot
import gspread
from google.oauth2.service_account import Credentials
from threading import Timer
from datetime import datetime, timedelta
from threading import Thread
import time
import random
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import requests
import os
import threading
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
reward_codes=sheet.worksheet("reward_codes")
data = constants.get_all_records()
constants_map = {row["constant_name"]: row["value"] for row in data}

############################################################################################################
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['redeem_reward_code'])
def redeem_reward_code(message):
    try:
        user_id = str(message.from_user.id)  
        text=message.text
        text=text.split()
        if(len(text)==1):
            bot.send_message(user_id,"write your rewarded code after the command /redeem_reward_code")
            return
        text=text[1]
        accept=False
        index=-1
        index=reward_codes.col_values(1).index(text) or -1
        if(index!=-1):
            # get the generated time and check if it dosnt acceed 14 days
            generated_time=reward_codes.cell(index+1,5).value
            generated_time=datetime.strptime(generated_time, "%Y-%m-%d %H:%M:%S")
            if((datetime.now()-generated_time).days<=14):
                accept=True
                # userid and username and reward tire (1 or 2 or 3) and date of generation the code
                user_id = reward_codes.cell(index+1,2).value
                username = reward_codes.cell(index+1,3).value
                tire = reward_codes.cell(index+1,4).value
                
                # send message to user that the admin will contat to you soon with the reward
                bot.send_message(user_id,"your code is valid, the admin will contact you soon to give you the reward with tire "+tire)
                # send to the admin the user id and username and tire and date of the generated code
                bot.send_message(constants_map['admin_id'],f"the user with id: {user_id} and username: @{username} has redeemed the reward code with tire {tire} and the code was generated at {generated_time}")

            # remove this row from the reward codes
            reward_codes.delete_rows(index+1)
        if(accept == False):
            bot.send_message(user_id,"your code is invalid or expired")
    except Exception as e:
        print(e)

@bot.message_handler(commands=['generate_reward_code'])
def generate_reward_code(message):
    try:
        first_name = message.from_user.first_name 
        user_id = str(message.from_user.id)  
        username = message.from_user.username or "User"
        index=users.col_values(1).index(user_id)
        if(index!=-1):
            referral_count = int(users.cell(index+1,5).value)
            # generate code from 6 digits
            rand_code=random.randint(100000,999999)
            if(referral_count>=int(constants_map['tire3_limit'])):
                # reduce tire3limit from the referral count
                users.update_cell(index+1,5,str(referral_count-int(constants_map['tire3_limit'])))
                bot.send_message(user_id, f"Congrats you have exedded tire3 in referrals,here is your reward code:\n{rand_code}\nyour code will expire after 14 days\nto redeem it wrute /redeem_reward_code {rand_code}")
                reward_codes.append_row([rand_code,user_id,username,3,datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            elif(referral_count>=int(constants_map['tire2_limit'])):
                users.update_cell(index+1,5,str(referral_count-int(constants_map['tire2_limit'])))
                bot.send_message(user_id, f"Congrats you have exedded tire2 in referrals,here is your reward code:\n{rand_code}\nyour code will expire after 14 days\nto redeem it wrute /redeem_reward_code {rand_code}")
                reward_codes.append_row([rand_code,user_id,username,2,datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

            elif(referral_count>=int(constants_map['tire1_limit'])):
                users.update_cell(index+1,5,str(referral_count-int(constants_map['tire1_limit'])))
                bot.send_message(user_id, f"Congrats you have exedded tire1 in referrals,here is your reward code:\n{rand_code}\nyour code will expire after 14 days\nto redeem it wrute /redeem_reward_code {rand_code}")
                reward_codes.append_row([rand_code,user_id,username,1,datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            else:
                bot.send_message(user_id, f"you have to reach tire1 in referrals count to get your reward code.")
    except Exception as e:
        print(e)

@bot.message_handler(commands=['get_referral_count'])
def get_referral_count(message):
    try:
        user_id = str(message.from_user.id)  
        index=users.col_values(1).index(user_id)
        if(index!=-1):
            referral_count = int(users.cell(index+1,5).value)
            bot.send_message(user_id, f"your referral count is: {referral_count}\ntire1 limit it : {constants_map['tire1_limit']}\ntire2 limit it : {constants_map['tire2_limit']}\ntire3 limit it : {constants_map['tire3_limit']}")
    except Exception as e:
        print(e)
def referral_handler(message):
    try:
        text=message.text
        text=text.split()
        if(len(text)==1):
            return
        text=text[1]
        # check text is a number
        try:
            referral_code=int(text)
        except:
            return
        # check if the referral code exists in the sheet
        codes=users.col_values(4)
        if str(referral_code) in codes:  
            index=codes.index(str(referral_code))
            new_count=int(users.cell(index+1,5).value)+1
            users.update_cell(index+1,5,str(new_count))
            user_id = users.cell(index+1,1).value  
            # user_id='1198671094'
            print(user_id)
            if(new_count==int(constants_map['tire1_limit'])):
                bot.send_message(user_id, f"Congrats you have reached tire1 in referrals,write /generate_reward_code to get your reward code,or continue untile reaching tire2")
            elif(new_count==int(constants_map['tire2_limit'])):
                bot.send_message(user_id, f"Congrats you have reached tire2 in referrals,write /generate_reward_code to get your reward code or continue untile reaching tire3")
            elif(new_count==int(constants_map['tire3_limit'])):
                bot.send_message(user_id, f"Congrats you have reached tire3 in referrals wich is the best tire,write /generate_reward_code to get your reward code ")
            elif(new_count>int(constants_map['tire3_limit'])):
                bot.send_message(user_id, f"you have acceded tire3 in referrals count,write /generate_reward_code to get your reward code")
    except Exception as e:
        print(e)

@bot.message_handler(commands=['start'])
def start(message):
    # Extract user details
    first_name = message.from_user.first_name 
    user_id = str(message.from_user.id)  
    username = message.from_user.username or "User"
    print(f"User ID: {user_id}, Username: {username}, first name: {first_name}")
    # Check if the first value already exists in the sheet
    existing_values = users.col_values(1)  # Assuming the first column contains the IDs
    if user_id not in existing_values:
        referral_handler(message)
        new_referral_code=1
        codes=users.col_values(4)[1:]
        if(len(codes)>0):
            # max +1
            # Convert codes to integers
            numeric_codes = list(map(int, codes))  # or [int(code) for code in codes]
            
            # Find max and add 1
            new_referral_code = max(numeric_codes) + 1

        users.append_row([user_id, username,first_name,new_referral_code,0])
        bot.send_message(message.chat.id, f"Hello {username} in our giveways bot, enjoy your time with us.")
        print(f"id: {user_id},username: {username} appended successfully.")
        # # Your bot's API token
        bot_token = constants_map['bot_token']
        # # Chat ID or username (e.g., @channelusername or channel ID)
        chat_id = constants_map['chat_to_invite_id']
        now = int(time.time())
        minutes = int(constants_map['time_limit_to_acctept_invitation'])
        expire = now + minutes*60
        # # Create the invite link
        url = f'https://api.telegram.org/bot{bot_token}/createChatInviteLink'
        params = {
            'chat_id': chat_id,
            'expire_date': expire,  # Expiry time as Unix timestamp
            'member_limit': 1,               # Optional: Set the member limit
            'creates_join_request': False,    # Optional: Set to True if users need admin approval
            'name': 'Special Invite Link',    # Optional: Invite link name
        }
        response = requests.post(url, data=params)

        # Check the response
        if response.status_code == 200:
            result = response.json()
            link = result['result']['invite_link']
            bot.send_message(message.chat.id, f"use this invitation link for the follwing {minutes} minutes,its allowed to use it only one time:\n{link}")
            print(f"Invite Link: {link}")
        else:
            print(f"Error couldnt send invitation link: {response.text}")        
        print("---------------------------------")
    else:
        bot.send_message(message.chat.id, f"Hello again {username}!.")
        print(f"id: {user_id},username: {username} this user already exists in the sheet.")
        print("---------------------------------")

@bot.message_handler(commands=['generate_link'])
def generate_link(message):
    first_name = message.from_user.first_name 
    user_id = str(message.from_user.id)  
    username = message.from_user.username or "User"
    existing_values = users.col_values(1) 
    index=-1
    chat_username=bot.get_me().username
    if user_id in existing_values:
        index=existing_values.index(user_id)
    if index!=-1:
        link=f"https://t.me/{chat_username}?start={users.cell(index+1,4).value}"
        
    else:
        new_referral_code=1
        codes=users.col_values(4)[1:]
        if(len(codes)>0):
            # max +1
            new_referral_code=max(codes)+1
        users.append_row([user_id, username,first_name,new_referral_code,0])
        link=f"https://t.me/{chat_username}?start={new_referral_code}"
    bot.send_message(message.chat.id, f"Here is your referral link:\n{link}")
    
def send_promotions(message_text):
    # Get the current date and time to create a unique sheet title
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH-MM-SS
    log_sheet_title = f"Promotion Log {current_time}"

    # Create a new sheet for logging with the current date and time in the title
    log_sheet = sheet.add_worksheet(title=log_sheet_title, rows="100", cols="3")
    log_sheet.append_row(["Chat ID", "Status", "Message"])

    # Retrieve all user chat IDs from the sheet
    chat_ids = users.col_values(1)[1:]  # Skip the header row if there is one
    failed_chat_ids = []  # List to store failed chat IDs
    successful_chat_ids = []  # List to store successful chat IDs
    for chat_id in chat_ids:
        try:
            # Attempt to send the message
            bot.send_message(chat_id, message_text, parse_mode="HTML")
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


@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = str(message.from_user.id)  # Ensure user_id is a string
    admin_id = str(constants_map['admin_id'])  # Convert admin_id to a string
    if user_id != admin_id:
        bot.send_message(user_id, "You are not authorized to use this command.")
        return
    # Extract the message from the command
    if len(message.text.split(maxsplit=1)) < 2:
        bot.send_message(user_id, "Please provide a message to broadcast. Example: /broadcast *Hello*!")
        return

    message_text = message.text.split(maxsplit=1)[1]
    # Send the message to all users
    send_promotions(message_text)
    bot.send_message(user_id, "Broadcast completed successfully!")
    print(f"Broadcasted message: {message_text}")
    print("---------------------------------")

# Handle media messages (photo, video, document) with caption containing /broadcast_media
@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_media_with_broadcast(message):
    user_id = str(message.from_user.id)  # Ensure user_id is a string
    admin_id = str(constants_map['admin_id'])  # Convert admin_id to a string
    if user_id != admin_id:
        bot.send_message(user_id, "You are not authorized to send media.")
        return

    if not message.caption or "/broadcast" not in message.caption:
        # Ignore if caption doesn't contain /broadcast_media
        bot.send_message(user_id, "Caption does not contain /broadcast_media. Media ignored.")
        return

    # Extract media type and file ID
    if message.photo:
        file_id = message.photo[-1].file_id  # Get the highest-resolution photo
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    elif message.document:
        file_id = message.document.file_id
        media_type = "document"
    else:
        bot.send_message(user_id, "Unsupported media type.")
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH-MM-SS
    log_sheet_title = f"Promotion Log {current_time}"

    # Create a new sheet for logging with the current date and time in the title
    log_sheet = sheet.add_worksheet(title=log_sheet_title, rows="100", cols="3")
    log_sheet.append_row(["Chat ID", "Status", "Message"])


    # Remove the /broadcast_media command from the caption
    caption = message.caption.replace("/broadcast", "").strip()

    # Retrieve all user chat IDs from the sheet
    chat_ids = users.col_values(1)[1:]  # Skip the header row
    failed_chat_ids = []
    successful_chat_ids = []

    for chat_id in chat_ids:
        try:
            # Send the media based on its type
            if media_type == "photo":
                bot.send_photo(chat_id, file_id, caption=caption, parse_mode="HTML")
            elif media_type == "video":
                bot.send_video(chat_id, file_id, caption=caption, parse_mode="HTML")
            elif media_type == "document":
                bot.send_document(chat_id, file_id, caption=caption, parse_mode="HTML")
            successful_chat_ids.append(chat_id)
            log_sheet.append_row([chat_id, "Success", caption])
        except Exception as e:
            failed_chat_ids.append(chat_id)
            print(f"Failed to send media to {chat_id}: {e}")
            log_sheet.append_row([chat_id, "Failed", str(e)])
            

    # Notify the admin about the results
    bot.send_message(user_id, "Broadcast media completed successfully!")
    total_successes = len(successful_chat_ids)
    total_failures = len(failed_chat_ids)

    # Append a summary row at the end of the sheet
    log_sheet.append_row(["Total Successes", total_successes])
    log_sheet.append_row(["Total Failures", total_failures])

# Start polling for bot commands
while True:
    try:
        bot.polling(non_stop=True,timeout=100)
    except Exception as e:
        print(e)
        time.sleep(10)
        continue