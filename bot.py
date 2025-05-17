import asyncio
import base64
import aiohttp
import datetime
from functools import wraps
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    UserIdInvalid,
    UsernameNotOccupied
)
from pymongo.errors import ConnectionFailure
from config import ADMIN_IDS
from core import (
    users_collection,
    numbers_collection,
    authorized_users_collection
)
from utils import LOGGER
from app import bot

# Load authorized users from MongoDB
def load_authorized_users():
    authorized_users = set()
    try:
        for user in authorized_users_collection.find():
            if "user_id" in user:
                authorized_users.add(user["user_id"])
            else:
                LOGGER.warning(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - Skipping invalid authorized user document: {user}")
    except ConnectionFailure:
        LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to connect to MongoDB")
    return authorized_users

# Save authorized user to MongoDB
def auth_user(user_id):
    authorized_users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Authorized user_id {user_id}")

# Remove authorized user from MongoDB
def unauth_user(user_id):
    authorized_users_collection.delete_one({"user_id": user_id})
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Unauthorized user_id {user_id}")

# Load data from MongoDB
def load_data():
    twilio_users = {}
    twilio_numbers = {}
    try:
        for user in users_collection.find():
            if "user_id" in user and "sid" in user and "token" in user:
                twilio_users[user["user_id"]] = (user["sid"], user["token"])
            else:
                LOGGER.warning(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - Skipping invalid user document: {user}")
        for number in numbers_collection.find():
            if "user_id" in number and "numbers" in number:
                twilio_numbers[number["user_id"]] = number["numbers"]
            else:
                LOGGER.warning(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - Skipping invalid numbers document: {number}")
    except ConnectionFailure:
        LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to connect to MongoDB")
    return twilio_users, twilio_numbers

# Save data to MongoDB
def save_user(user_id, sid, token):
    if not sid or not token:
        LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Attempted to save invalid SID or token for user_id {user_id}")
        return
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "sid": sid, "token": token}},
        upsert=True
    )
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Saved user data for user_id {user_id}")

def save_numbers(user_id, numbers):
    numbers_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "numbers": numbers}},
        upsert=True
    )
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Saved numbers for user_id {user_id}")

def delete_user_data(user_id):
    users_collection.delete_one({"user_id": user_id})
    numbers_collection.delete_one({"user_id": user_id})
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Deleted data for user_id {user_id}")

twilio_users, twilio_numbers = load_data()
authorized_users = load_authorized_users()

# Helper function to resolve username or user ID to user ID
async def resolve_identifier(client, identifier):
    try:
        if identifier.startswith("@"):
            username = identifier[1:]  # Remove "@"
            user = await client.get_users(username)
            LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Resolved username {identifier} to user_id {user.id}")
            return user.id
        else:
            user_id = int(identifier)
            return user_id
    except (UserIdInvalid, UsernameNotOccupied, ValueError) as e:
        LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to resolve identifier {identifier}: {str(e)}")
        return None

# Decorator to restrict commands to authorized users or admins
def restrict_to_authorized(func):
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id in ADMIN_IDS or user_id in authorized_users:
            return await func(client, message, *args, **kwargs)
        else:
            buttons = [[InlineKeyboardButton("Contact Owner", user_id=5991909954)]]
            await client.send_message(
                message.chat.id,
                "**Sorry Bro Unauthorized User Kindly Contact @Ruhulxr For Auth**",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN
            )
    return wrapper

@bot.on_message(filters.command("auth") & filters.user(ADMIN_IDS))
async def auth_command(client, message: Message):
    try:
        _, identifier = message.text.split(maxsplit=1)
    except ValueError:
        await client.send_message(
            message.chat.id,
            "**✘《 Error ↯ 》 Usage: /auth <useridOrusername>**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    user_id = await resolve_identifier(client, identifier)
    if user_id is None:
        await client.send_message(
            message.chat.id,
            "**✘《 Error ↯ 》 Invalid user ID or username**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if user_id in authorized_users:
        await client.send_message(
            message.chat.id,
            f"**✘《 Error ↯ 》 User ID {user_id} is already authorized**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    authorized_users.add(user_id)
    auth_user(user_id)
    await client.send_message(
        message.chat.id,
        f"**✘《 Success ↯ 》 User ID {user_id} has been authorized**",
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_message(filters.command("unauth") & filters.user(ADMIN_IDS))
async def unauth_command(client, message: Message):
    try:
        _, identifier = message.text.split(maxsplit=1)
    except ValueError:
        await client.send_message(
            message.chat.id,
            "**✘《 Error ↯ 》 Usage: /unauth <useridOrusername>**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    user_id = await resolve_identifier(client, identifier)
    if user_id is None:
        await client.send_message(
            message.chat.id,
            "**✘《 Error ↯ 》 Invalid user ID or username**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if user_id not in authorized_users:
        await client.send_message(
            message.chat.id,
            f"**✘《 Error ↯ 》 User ID {user_id} is not authorized**",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    authorized_users.remove(user_id)
    unauth_user(user_id)
    await client.send_message(
        message.chat.id,
        f"**✘《 Success ↯ 》 User ID {user_id} has been unauthorized**",
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_message(filters.command("start"))
@restrict_to_authorized
async def start(client, message: Message):
    full_name = message.from_user.first_name
    if message.from_user.last_name:
        full_name += f" {message.from_user.last_name}"
    text = (
        f"**Hello, {full_name}! Welcome to the Twilio Bot!**\n\n"
        "Here, you can easily purchase numbers and retrieve OTPs to create WhatsApp or Telegram accounts. Follow the commands below to get started:\n\n"
        "**/login <SID> <TOKEN>** - Log in to your Twilio account\n"
        "**/buy** - Purchase available numbers\n"
        "**/get** - Retrieve OTP messages\n"
        "**/del <PhoneNumber>** - Delete a purchased number\n"
        "**/my** - List your active numbers\n"
        "**/logout** - Log out from your Twilio account\n\n"
        "**Support: @TheSmartDev**"
    )
    buttons = [
        [
            InlineKeyboardButton("✘《 Updates ↯ 》", url="t.me/TheSmartDev"),
            InlineKeyboardButton("✘《 Dev ↯ 》", user_id=7303810912)
        ]
    ]
    await client.send_message(
        message.chat.id,
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_message(filters.command("login"))
@restrict_to_authorized
async def login(client, message: Message):
    loading_message = await client.send_message(message.chat.id, "**✘《 Loading ↯ 》 Processing login...**", parse_mode=ParseMode.MARKDOWN)
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Invalid format")
        _, sid, token = parts
        if not sid.startswith("AC") or len(token) < 32:
            raise ValueError("Invalid SID or token format")
    except ValueError:
        await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 Usage: /login <SID> <TOKEN>**", parse_mode=ParseMode.MARKDOWN)
        return

    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json", headers=headers) as resp:
            if resp.status == 200:
                twilio_users[message.from_user.id] = (sid, token)
                twilio_numbers.setdefault(message.from_user.id, [])
                save_user(message.from_user.id, sid, token)
                save_numbers(message.from_user.id, twilio_numbers[message.from_user.id])
                await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Success ↯ 》 Login successful**", parse_mode=ParseMode.MARKDOWN)
            else:
                await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 Login failed. Check your SID/TOKEN**", parse_mode=ParseMode.MARKDOWN)

@bot.on_message(filters.command("logout"))
@restrict_to_authorized
async def logout(client, message: Message):
    user_id = message.from_user.id
    loading_message = await client.send_message(message.chat.id, "**✘《 Loading ↯ 》 Processing logout...**", parse_mode=ParseMode.MARKDOWN)
    if user_id in twilio_users:
        del twilio_users[user_id]
        if user_id in twilio_numbers:
            del twilio_numbers[user_id]
        delete_user_data(user_id)
        await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Success ↯ 》 Logout successful**", parse_mode=ParseMode.MARKDOWN)
    else:
        await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 You are not logged in**", parse_mode=ParseMode.MARKDOWN)

@bot.on_message(filters.command("buy"))
@restrict_to_authorized
async def buy_numbers(client, message: Message):
    user_id = message.from_user.id
    if user_id not in twilio_users:
        await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Log in first using /login**", parse_mode=ParseMode.MARKDOWN)
        return

    buttons = [
        [
            InlineKeyboardButton("US 🇺🇸", callback_data="country_US"),
            InlineKeyboardButton("CA 🇨🇦", callback_data="country_CA")
        ],
        [
            InlineKeyboardButton("PR 🇵🇷", callback_data="country_PR")
        ]
    ]
    await client.send_message(
        message.chat.id,
        "**✘《 Kindly Choose The Country You Prefer ↯ 》**",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

async def fetch_numbers(client, message: Message, user_id, country_code, custom_prefix=None):
    loading_message = await client.send_message(message.chat.id, f"**✘《 Loading ↯ 》 Fetching {country_code} numbers...**", parse_mode=ParseMode.MARKDOWN)

    sid, token = twilio_users[user_id]
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()
    }

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/AvailablePhoneNumbers/{country_code}/Local.json?PageSize=10"
    if custom_prefix:
        # For Puerto Rico, prefix with 787 as per original logic
        if country_code == "PR":
            url += f"&AreaCode=787"
        else:
            url += f"&AreaCode={custom_prefix}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                await client.edit_message_text(message.chat.id, loading_message.id, f"**✘《 Error ↯ 》 Failed to fetch {country_code} numbers**", parse_mode=ParseMode.MARKDOWN)
                return

            data = await resp.json()
            numbers = data.get("available_phone_numbers", [])
            if country_code == "CA":
                numbers = [num for num in numbers if num['phone_number'].startswith('+1')]
            
            if not numbers:
                await client.edit_message_text(message.chat.id, loading_message.id, f"**✘《 Error ↯ 》 No available {country_code} numbers**", parse_mode=ParseMode.MARKDOWN)
                return

            # Filter numbers by custom prefix if provided
            if custom_prefix and country_code != "PR":
                numbers = [num for num in numbers if num['phone_number'].startswith(f'+1{custom_prefix}')]
            elif custom_prefix and country_code == "PR":
                numbers = [num for num in numbers if num['phone_number'].startswith(f'+1787')]

            if not numbers:
                await client.edit_message_text(message.chat.id, loading_message.id, f"**✘《 Error ↯ 》 No available {country_code} numbers with area code {custom_prefix}**", parse_mode=ParseMode.MARKDOWN)
                return

            numbers_list = "\n".join(num['phone_number'] for num in numbers)
            message_text = f"**Available {country_code} Numbers{' with area code ' + custom_prefix if custom_prefix else ''}:**\n{numbers_list}\n\n**Select a number to purchase:**"

            buttons = []
            row = []
            for i, num in enumerate(numbers):
                phone = num['phone_number']
                row.append(InlineKeyboardButton(phone, callback_data=f"buy_{phone}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []

            if row:
                buttons.append(row)

            await client.edit_message_text(
                message.chat.id,
                loading_message.id,
                message_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN
            )

@bot.on_message(filters.regex(r"^[0-9]{3}$") & filters.reply)
@restrict_to_authorized
async def handle_custom_area_code(client, message: Message):
    user_id = message.from_user.id
    if user_id not in twilio_users:
        await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Log in first using /login**", parse_mode=ParseMode.MARKDOWN)
        return

    area_code = message.text
    # Get the country code from the replied message
    if message.reply_to_message and message.reply_to_message.text:
        # Extract country code from the prompt message
        if "Enter your preferred 3-digit area code for" in message.reply_to_message.text:
            country_code = message.reply_to_message.text.split("for ")[-1].split(" ")[0]
            await fetch_numbers(client, message, user_id, country_code, custom_prefix=area_code)
            return
    await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Please select a country first and reply to the area code prompt**", parse_mode=ParseMode.MARKDOWN)

@bot.on_callback_query()
async def handle_callbacks(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in twilio_users and user_id not in ADMIN_IDS and user_id not in authorized_users:
        await callback_query.answer("Please log in first and ensure you are authorized.", show_alert=True)
        return

    data = callback_query.data
    if data.startswith("country_"):
        country_code = data.split("_")[1]
        buttons = [
            [
                InlineKeyboardButton("✘《 Yes ↯ 》", callback_data=f"custom_{country_code}"),
                InlineKeyboardButton("✘《 No ↯ 》", callback_data=f"all_{country_code}")
            ]
        ]
        await client.edit_message_text(
            callback_query.message.chat.id,
            callback_query.message.id,
            "**✘《 Do You Prefer Custom Area Code ↯ 》**",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    elif data.startswith("all_"):
        country_code = data.split("_")[1]
        await fetch_numbers(client, callback_query.message, user_id, country_code)
    elif data.startswith("custom_"):
        country_code = data.split("_")[1]
        await callback_query.message.reply(f"**Enter your preferred 3-digit area code for {country_code} (e.g., 592):**", parse_mode=ParseMode.MARKDOWN)
    elif data.startswith("buy_"):
        phone = data.replace("buy_", "")
        sid, token = twilio_users[user_id]

        loading_message = await client.send_message(callback_query.message.chat.id, f"**✘《 Loading ↯ 》 Purchasing number `{phone}`...**", parse_mode=ParseMode.MARKDOWN)

        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "PhoneNumber": phone
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json", headers=headers, data=data) as resp:
                if resp.status == 201:
                    twilio_numbers[user_id].append(phone)
                    save_numbers(user_id, twilio_numbers[user_id])
                    await client.edit_message_text(
                        callback_query.message.chat.id,
                        loading_message.id,
                        f"**✘《 Success ↯ 》 Number purchased: `{phone}`**",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await client.edit_message_text(
                        callback_query.message.chat.id,
                        loading_message.id,
                        f"**✘《 Error ↯ 》 Failed to purchase number: `{phone}`**",
                        parse_mode=ParseMode.MARKDOWN
                    )

@bot.on_message(filters.command("my"))
@restrict_to_authorized
async def my_numbers(client, message: Message):
    user_id = message.from_user.id
    loading_message = await client.send_message(message.chat.id, "**✘《 Loading ↯ 》 Fetching your numbers...**", parse_mode=ParseMode.MARKDOWN)
    nums = twilio_numbers.get(user_id, [])
    if not nums:
        await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 No numbers found**", parse_mode=ParseMode.MARKDOWN)
        return
    text = "**Your Active Numbers:**\n\n" + "\n".join(num for num in nums)
    await client.edit_message_text(message.chat.id, loading_message.id, text, parse_mode=ParseMode.MARKDOWN)

@bot.on_message(filters.command("del"))
@restrict_to_authorized
async def delete_number(client, message: Message):
    user_id = message.from_user.id
    if user_id not in twilio_users:
        await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Log in first using /login**", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        _, number = message.text.split()
    except ValueError:
        await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Usage: /del <PhoneNumber>**", parse_mode=ParseMode.MARKDOWN)
        return

    loading_message = await client.send_message(message.chat.id, f"**✘《 Loading ↯ 》 Deleting number `{number}`...**", parse_mode=ParseMode.MARKDOWN)
    sid, token = twilio_users[user_id]
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json", headers=headers) as resp:
            data = await resp.json()
            for record in data.get("incoming_phone_numbers", []):
                if record.get("phone_number") == number:
                    sid_to_delete = record.get("sid")
                    del_url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers/{sid_to_delete}.json"
                    async with session.delete(del_url, headers=headers) as del_resp:
                        if del_resp.status == 204:
                            twilio_numbers[user_id].remove(number)
                            save_numbers(user_id, twilio_numbers[user_id])
                            await client.edit_message_text(message.chat.id, loading_message.id, f"**✘《 Success ↯ 》 Number deleted: `{number}`**", parse_mode=ParseMode.MARKDOWN)
                            return
                        else:
                            await client.edit_message_text(message.chat.id, loading_message.id, f"**✘《 Error ↯ 》 Failed to delete number: `{number}`**", parse_mode=ParseMode.MARKDOWN)
                            return
            await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 Number not found in your account**", parse_mode=ParseMode.MARKDOWN)

@bot.on_message(filters.command("get"))
@restrict_to_authorized
async def get_otp(client, message: Message):
    user_id = message.from_user.id
    if user_id not in twilio_users:
        await client.send_message(message.chat.id, "**✘《 Error ↯ 》 Login required. Use /login**", parse_mode=ParseMode.MARKDOWN)
        return

    loading_message = await client.send_message(message.chat.id, "**✘《 Loading ↯ 》 Fetching OTP messages...**", parse_mode=ParseMode.MARKDOWN)
    sid, token = twilio_users[user_id]
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()
    }

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json?PageSize=10"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 Failed to fetch messages**", parse_mode=ParseMode.MARKDOWN)
                return

            data = await resp.json()
            messages = data.get("messages", [])
            if not messages:
                await client.edit_message_text(message.chat.id, loading_message.id, "**✘《 Error ↯ 》 No messages found**", parse_mode=ParseMode.MARKDOWN)
                return

            text = "**Latest OTP Messages:**\n\n"
            for msg in messages:
                if msg.get("direction") == "inbound":
                    text += f"{msg.get('from')} -> {msg.get('body')}\n"

            await client.edit_message_text(message.chat.id, loading_message.id, text or "**✘《 Error ↯ 》 No OTPs found**", parse_mode=ParseMode.MARKDOWN)

LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Bot Successfully Started! 💥")
bot.run()
