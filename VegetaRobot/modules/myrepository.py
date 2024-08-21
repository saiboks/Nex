
import requests 

from VegetaRobot import pgram, aiohttpsession as session
from pyrogram import filters
from pyrogram.types import *




@pgram.on_message(filters.command("repo"))
async def repo(client, message):
    await message.reply_photo(
        photo=AVISHA,
        caption=f"""𖣐 ʜᴇʏ {message.from_user.mention()}, ᴡᴇʟᴄᴏᴍᴇ ʙᴀʙʏ ♥︎\n\n⬤ ɪғ ʏᴏᴜ ᴡᴀɴᴛ [{dispatcher.bot.first_name}](t.me/{dispatcher.bot.username}) ʙᴏᴛ ʀᴇᴘᴏ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʀᴇᴘᴏ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ.\n\n𖣐 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ [{dispatcher.bot.first_name}](t.me/{dispatcher.bot.username}) """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴏᴡɴᴇʀ",user_id=OWNER_ID
                    ),
                    InlineKeyboardButton(
                        "ʀᴇᴘᴏ",
                        callback_data="gib_source",
                    ),
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex("gib_source"))
async def gib_repo_callback(_, callback_query):
    await callback_query.edit_message_media(
        media=InputMediaVideo("https://telegra.ph/file/9235d57807362b4e227a3.mp4", has_spoiler=True),
        reply_markup=InlineKeyboardMarkup(
            [
                [close_button]
            ]
        ),
        )
close_button = InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")
