
import requests 

from VegetaRobot import pgram, aiohttpsession as session
from pyrogram import filters
from pyrogram.types import *




@pgram.on_message(filters.command("repo"))
async def repo(_, m):
    chat_id = m.chat.id
    users = requests.get("https://api.github.com/repos/NandhaxD/VegetaRobot/contributors").json()
    list_of_users = ""
    count = 1
    for user in users:
        list_of_users += (f"**{count}.** [{user['login']}]({user['html_url']})\n")
        count += 1
        total = count-1
    text = f"""
[ Contributors in @VegetaRobot ]

{list_of_users}
[`Contributors: {total}`]"""
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("𝐆ʀᴏᴜᴘ",url="t.me/PhoenixXsupport"),
InlineKeyboardButton(text="Rᴇᴘᴏ", callback_data="Rᴇᴘᴏ_"
),]]) 