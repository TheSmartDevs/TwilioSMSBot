# 🌟 TᴡɪʟɪᴏSMSBᴏᴛ 💥

A modern Telegram bot for managing Twilio phone numbers and retrieving OTPs, built with **Pʏᴛʜᴏɴ 3.8+** and **Pʏʀᴏɢʀᴀᴍ**. This bot allows users to purchase phone numbers, receive OTP messages, and manage their Twilio accounts directly through Telegram with a sleek and intuitive interface. ❄️

![Pʏᴛʜᴏɴ](https://img.shields.io/badge/Python-3.8%2B-blue) ![Pʏʀᴏɢʀᴀᴍ](https://img.shields.io/badge/Pyrogram-2.0.106-orange)

## ✨《 Fᴇᴀᴛᴜʀᴇs 👀 》

- **Uꜱᴇʀ Aᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ**: Secure login and logout with Twilio SID and Token. ⭐️  
- **Nᴜᴍʙᴇʀ Mᴀɴᴀɢᴇᴍᴇɴᴛ**: Purchase, list, and delete phone numbers (Puerto Rico numbers supported). 💫  
- **OTP Rᴇᴛʀɪᴇᴠᴀʟ**: Fetch and display the latest OTP messages. 🌐  
- **Aᴅᴍɪɴ Cᴏɴᴛʀᴏʟꜱ**: Authorize/unauthorize users via commands. ✅  
- **Cᴜꜱᴛᴏᴍ Nᴜᴍʙᴇʀ Sᴇʟᴇᴄᴛɪᴏɴ**: Choose numbers by area code for personalized purchases. 💀  
- **MᴏɴɢᴏDB Iɴᴛᴇɢʀᴀᴛɪᴏɴ**: Persistent storage for user data and numbers. ☠️  
- **Mᴏᴅᴇʀɴ UI**: Markdown-based messages with inline keyboards for a seamless user experience. ⭐️  
- **Eʀʀᴏʀ Hᴀɴᴅʟɪɴɢ**: Robust logging and user-friendly error messages. 💫  
- **Aꜱʏɴᴄʜʀᴏɴᴏᴜꜱ Dᴇꜱɪɢɴ**: Built with Pyrogram and aiohttp for high performance. ❄️  

## 🌟《 PʀᴇʀᴇQᴜɪꜱɪᴛᴇꜱ ✨ 》

- **Pʏᴛʜᴏɴ 3.8+**: Ensure Python is installed.  
- **MᴏɴɢᴏDB**: A running MongoDB instance (local or cloud-based, e.g., MongoDB Atlas).  
- **Tᴇʟᴇɢʀᴀᴍ Bᴏᴛ**: A bot token from [BᴏᴛFᴀᴛʜᴇʀ](https://t.me/BotFather).  
- **Tᴡɪʟɪᴏ Aᴄᴄᴏᴜɴᴛ**: Twilio SID and Token for number purchasing and OTP retrieval.  
- **VPS (Oᴘᴛɪᴏɴᴀʟ)**: For deployment (e.g., Ubuntu 20.04+).  

## 💥《 Sᴇᴛᴜᴘ Tᴜᴛᴏʀɪᴀʟ ❄️ 》

### 1. Cʟᴏɴᴇ ᴛʜᴇ Rᴇᴘᴏꜱɪᴛᴏʀʏ

```bash
git clone https://github.com/TheSmartDevs/TwilioSMSBot.git
cd TwilioSMSBot
```

### 2. Iɴꜱᴛᴀʟʟ Dᴇᴘᴇɴᴅᴇɴᴄɪᴇꜱ

Create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Cᴏɴꜰɪɢᴜʀᴇ Eɴᴠɪʀᴏɴᴍᴇɴᴛ

Edit `config.py` with your credentials:

```python
API_ID = YourAPIID  # From https://my.telegram.org
API_HASH = "YourAPIHash"  # From https://my.telegram.org
BOT_TOKEN = "YourBotToken"  # From BotFather
ADMIN_IDS = [7303810912, 5991909954, 6249257243]  # Your Telegram user IDs
MONGO_URI = "Your_Mongo_Url"  # MongoDB connection string
```

- **API_ID** and **API_HASH**: Obtain from [Tᴇʟᴇɢʀᴀᴍ'ꜱ API ᴘᴀɢᴇ](https://my.telegram.org).  
- **BOT_TOKEN**: Create a bot via [BᴏᴛFᴀᴛʜᴇʀ](https://t.me/BotFather).  
- **MONGO_URI**: Use MongoDB Atlas or a local MongoDB instance (`mongodb://localhost:27017`).  
- **ADMIN_IDS**: Add Telegram user IDs of admins who can authorize users.  

### 4. Rᴜɴ Lᴏᴄᴀʟʟʏ

Start the bot:

```bash
python3 bot.py
```

The bot will log its status and respond to commands in Telegram. ✅  

## 💫《 Dᴇᴘʟᴏʏɪɴɢ ᴛᴏ ᴀ VPS ⭐️ 》

### 1. Sᴇᴛ Uᴘ VPS

- Use a provider like DigitalOcean, AWS, or Linode.
- Recommended: Ubuntu 20.04+ with at least 1GB RAM.

### 2. Iɴꜱᴛᴀʟʟ Dᴇᴘᴇɴᴅᴇɴᴄɪᴇꜱ ᴏɴ VPS

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git screen mongodb -y
```

If using MongoDB Atlas, skip local MongoDB installation.

### 3. Cʟᴏɴᴇ ᴀɴᴅ Cᴏɴꜰɪɢᴜʀᴇ

```bash
git clone https://github.com/TheSmartDevs/TwilioSMSBot.git
cd TwilioSMSBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy and edit `config.py` as described in the setup section.

### 4. Rᴜɴ ᴡɪᴛʜ Sᴄʀᴇᴇɴ

Use `screen` to keep the bot running in the background:

```bash
screen -S twilio_bot
source venv/bin/activate
python3 bot.py
```

Detach from the screen session by pressing `Ctrl+A` then `D`. To reattach:

```bash
screen -r twilio_bot
```

## 🌟《 Uꜱᴀɢᴇ 💥 》

### Cᴏᴍᴍᴀɴᴅꜱ

- `/start`: Welcome message with bot instructions.  
- `/login <SID> <TOKEN>`: Log in to your Twilio account.  
- `/buy`: Purchase a phone number (supports custom area codes).  
- `/get`: Retrieve OTP messages.  
- `/del <PhoneNumber>`: Delete a purchased number.  
- `/my`: List your active numbers.  
- `/logout`: Log out from your Twilio account.  
- `/auth <useridOrusername>`: (Admin only) Authorize a user.  
- `/unauth <useridOrusername>`: (Admin only) Unauthorize a user.  

### ⭐️ Eᴜᴀᴍᴘʟᴇ Wᴏʀᴋꜰʟᴏᴡ

1. Start the bot: `/start`  
2. Log in: `/login ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx YourTwilioToken`  
3. Buy a number: `/buy` (follow prompts to select a number).  
4. Get OTPs: `/get`  
5. Delete a number: `/del +1234567890`  

## 💀《 Pʀᴏᴊᴇᴄᴛ Sᴛʀᴜᴄᴛᴜʀᴇ ☠️ 》

```
TwilioSMSBot/
├── bot.py              # Main bot logic
├── app.py              # Bot client setup
├── config.py           # Configuration file
├── core/               # MongoDB collections
│   ├── __init__.py
│   └── mongo.py
├── utils/              # Logger and utilities
│   ├── __init__.py
│   └── LOGGING.py
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## 🌐《 Cᴏɴᴛʀɪʙᴜᴛɪɴɢ ✨ 》

Contributions are welcome! Please:

1. Fork the repository.  
2. Create a new branch (`git checkout -b feature/your-feature`).  
3. Commit your changes (`git commit -m 'Add your feature'`).  
4. Push to the branch (`git push origin feature/your-feature`).  
5. Open a Pull Request.  

## ⭐️《 Sᴜᴘᴘᴏʀᴛ 🌟 》

For issues or questions, contact the developer:

- Tᴇʟᴇɢʀᴀᴍ: [@TʜᴇSᴍᴀʀᴛDᴇᴠ](https://t.me/TheSmartDev)  
- GɪᴛHᴜʙ: [TʜᴇSᴍᴀʀᴛDᴇᴠꜱ](https://github.com/TheSmartDevs)  

Rᴇᴘᴏꜱɪᴛᴏʀʏ: [https://github.com/TheSmartDevs/TwilioSMSBot](https://github.com/TheSmartDevs/TwilioSMSBot)