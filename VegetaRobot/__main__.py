import importlib
import random
import time
import html
import re

from sys import argv, version_info
from typing import Optional
from pyrogram import filters

from VegetaRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,UPDATES_CHANNEL,
    dispatcher,
    StartTime,
    pgram, telethn,
    updater)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from VegetaRobot.modules import ALL_MODULES
from VegetaRobot.modules.helper_funcs.chat_status import is_user_admin
from VegetaRobot.modules.helper_funcs.misc import paginate_modules
from VegetaRobot.modules.misc import markdown_help_sender
from VegetaRobot.modules.disable import DisableAbleCommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.utils.helpers import mention_html
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown

from VegetaRobot.utils.fonts import Fonts
from VegetaRobot.modules.misc import MARKDOWN_HELP



TextFont = Fonts.san

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """ 
*┗► What's Up, Earthling! ◄┛*

~~ *I am the Prince of All Saiyans, Vegeta!* ~~

~ *Prepare yourself for my commands! ~
Click the help button below if you dare* [❗]({})

──『 *You better be ready to train hard!* 』──
""" 

buttons = [
    [
        InlineKeyboardButton(
                            text=f"{TextFont('𝐀ᴅᴅ 𝐍ᴇx 𝐓ᴏ 𝐘ᴏᴜʀ 𝐂ʜᴀᴛ')}",
                            url=f"t.me/{BOT_USERNAME}?startgroup=true"),
                    ],
                     [
                       InlineKeyboardButton(text=f"{TextFont('𝐒ᴜᴘᴘᴏʀᴛ')}", url=f"https://t.me/{SUPPORT_CHAT}"),
                       InlineKeyboardButton(text=f"{TextFont('𝐔ᴘᴅᴀᴛᴇ')}",  url=f"https://t.me/{UPDATES_CHANNEL}"),
                    ],
                   [
                       InlineKeyboardButton(text=f"{TextFont('𝐀ʙᴏᴜᴛ')}", url=f"https://t.me/where_lucy"),
                       InlineKeyboardButton(text=f"{TextFont('𝐆ʀᴀʙs')}", url=f"https://t.me/the_losthope"),
                ],[ InlineKeyboardButton(text=f"{TextFont('𝐂ᴏᴍᴍᴀɴᴅs & 𝐇ᴇʟᴘ')}", callback_data="help_back"
         ),
    ],
] 

HELP_STRINGS = """ *Hello There! Here you can get all of the help commands!
- /donate - Steps to Donate Bot Owner 
- /help (modulename): you also get the about the module.
- /settings - in this work group only chat!
Below Click the module you know about module commands!*
"""

HELP_MSG = "Click the button below to get help manu in your pm."
DONATE_STRING = """*don't need donate I'm free for everyone add your group's in @VegetaRobot this is my donate🙂*"""
HELP_IMG= "https://telegra.ph/file/5bae82bd14bc76339a465.jpg"
GROUPSTART_IMG= "https://telegra.ph/file/657742596a8babedb8a44.mp4"

VEGETA_IMG = ( "https://telegra.ph/file/aedb9922d1ad2988cf2da.jpg",
"https://telegra.ph/file/2fff68e983ab8e591953f.jpg",
"https://telegra.ph/file/63eef7850f058e5e39303.jpg",
"https://telegra.ph/file/461ba242d7040cd5421d2.jpg",
"https://telegra.ph/file/01589a9974ff335d27e07.jpg",
"https://telegra.ph/file/60b963b4fd4fa4e87bf04.jpg",
"https://telegra.ph/file/60b963b4fd4fa4e87bf04.jpg",
"https://telegra.ph/file/ad48a7f5159f2f72f2ec5.jpg",
"https://telegra.ph/file/9d228392a017444cb203d.jpg",
"https://telegra.ph/file/63641b082942ff7f6ca30.jpg",
"https://telegra.ph/file/5593144a615f04dca1740.jpg",
"https://telegra.ph/file/f91acb526c8c40a795eaa.jpg",
"https://telegra.ph/file/1099f0c3141d8f159a30d.jpg",
"https://telegra.ph/file/5515cf3334ab4c0e73279.jpg",
"https://telegra.ph/file/9e20200a21278f8ef46cb.jpg",
"https://telegra.ph/file/ffd418fac46e0f42e1130.jpg",
"https://telegra.ph/file/360620d151f57535fa6a8.jpg",
"https://telegra.ph/file/11d695b01f53de44bd9f5.jpg",
"https://telegra.ph/file/7b0c25d53126214c3267c.jpg",
"https://telegra.ph/file/0f59bac5422318ab2ef20.jpg",
"https://telegra.ph/file/c6d2a96cc5932a99a047b.jpg",
"https://telegra.ph/file/bc69eecfe94a4de05fcd4.jpg",
"https://telegra.ph/file/d7d5e19988475a8c6f7c1.jpg",
"https://telegra.ph/file/87408610f6355a72eba13.jpg",
"https://telegra.ph/file/2af7dbbf5e1abe96f125d.jpg",
"https://telegra.ph/file/a6e9900416f0a5dfc9940.jpg",
"https://telegra.ph/file/6b33f40bee8e4d4f1bd44.jpg",
"https://telegra.ph/file/ed4cdf0b344c2824c36dc.jpg",
"https://telegra.ph/file/82821a3198403c5592328.jpg",
"https://telegra.ph/file/c4fc8ba932e4f71e0c519.jpg",
"https://telegra.ph/file/a71df585c11b99356d9a7.jpg",
"https://telegra.ph/file/636d6a4baac6990535f81.jpg",
"https://telegra.ph/file/2f386500da74a2f0fc090.jpg",
"https://telegra.ph/file/c0445b96646417bd6bb91.jpg",
"https://telegra.ph/file/27865f4b42b1e20ddb22a.jpg",
"https://telegra.ph/file/885791722cb9fffea25cc.jpg",
"https://telegra.ph/file/8491932520f606dd3445e.jpg",
"https://telegra.ph/file/42fd8e8720535cd97724b.jpg",
"https://telegra.ph/file/3be69fda78ff5192456c9.jpg",
"https://telegra.ph/file/aca473c2478cc065a5a8b.jpg",
"https://telegra.ph/file/b2726578826d2b4549897.jpg",
"https://telegra.ph/file/9ba4bb6e20961c841a2ef.jpg",
"https://telegra.ph/file/06c5cd5ddf72cd27bb36e.jpg",
"https://telegra.ph/file/43214e3b8b9d8b3255115.jpg",
"https://telegra.ph/file/04aba46c146fc97161fe4.jpg",
"https://telegra.ph/file/ec3ebb6532bc1ba595940.jpg",
"https://telegra.ph/file/61fbf7cc7706aa5832575.jpg",
"https://telegra.ph/file/df7ddb9ac429fe3169084.jpg",
"https://telegra.ph/file/a7ece586d7f563905cfae.jpg",
"https://telegra.ph/file/0038bffc1ef00daa52066.jpg",
"https://telegra.ph/file/5d1516b85b9750ff47112.jpg",
"https://telegra.ph/file/5854a00c4f6bdc9490806.jpg",
"https://telegra.ph/file/f184b0b3dd9d7b5abc267.jpg",
"https://telegra.ph/file/3f4a972a3d563030450ae.jpg",
"https://telegra.ph/file/efcc8c9eb7530ed2ba8e3.jpg",
"https://telegra.ph/file/b8dc22f144de509fa113d.jpg",
"https://telegra.ph/file/1eb37932e18d03870f222.jpg",
"https://telegra.ph/file/10f8703bf4b400aee5e71.jpg",
"https://telegra.ph/file/ef70d561b72b90f221c00.jpg",
"https://telegra.ph/file/ffc57b32df52f700a77af.jpg",
"https://telegra.ph/file/fc9500a0f0dd7a66e131b.jpg",
"https://telegra.ph/file/a0507048aa14c89af3198.jpg",
"https://telegra.ph/file/0e72c666535adde455213.jpg",)       

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("VegetaRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)



def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower() == "markdownhelp":
                return update.effective_message.reply_text(MARKDOWN_HELP)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text=f"{TextFont('⬅Back')}", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            image = random.choice(VEGETA_IMG)
            update.effective_message.reply_text(PM_START_TEXT.format(image),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        first_name = update.effective_user.first_name
        update.effective_message.reply_animation(
             GROUPSTART_IMG, 
             caption="*Greetings!\n ┗► {} ◄┛,\nSaiyan Warrior reporting\nEnergy level now : {} *".format(
             first_name, uptime
            ),
            parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
                [
                  [
                  InlineKeyboardButton(text=f"{TextFont('SUPPORT')}", url=f"https://telegram.dog/{SUPPORT_CHAT}"),
                  InlineKeyboardButton(text=f"{TextFont('UPDATES')}", url=f"t.me/{UPDATES_CHANNEL}"),
                  ]
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(
      chat_id=OWNER_ID, 
      text=message, 
      parse_mode=ParseMode.HTML
    )


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors



def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            message = update.effective_message
            text = (
                "\nᴍᴏᴅᴜʟᴇ ɴᴀᴍᴇ - *{}*\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=f"{TextFont('⬅ back')}", callback_data="help_back"),
                      InlineKeyboardButton(text=f"{TextFont('⬅ Home')}", callback_data="vegeta_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def vegeta_about_callback(update, context):
    query = update.callback_query
    if query.data == "vegeta_back":
        vegeta_img = random.choice(VEGETA_IMG)
        query.message.edit_text(
                PM_START_TEXT.format(vegeta_img),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
        )

 



def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{TextFont('Help')}",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            HELP_MSG,
            reply_markup=InlineKeyboardMarkup(
                
                [
                    [ InlineKeyboardButton(text=f"{TextFont('Open in private')}", url=f"https://t.me/{BOT_USERNAME}?start=help"),
                      ],[  InlineKeyboardButton(
                            text=f"{TextFont('Open here')}",
                            callback_data="help_back"
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=f"{TextFont('Back')}", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )



def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{TextFont('Back')}",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))



def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{TextFont('Settings')}",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)



def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1610284626 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop




def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}","[𝑵𝒆𝒙 𝑺𝒖𝒓𝒗𝒊𝒗𝒊𝒏𝒈...](https://telegra.ph/file/8346a3ddf1f31cbb6c802.jpg)", parse_mode=ParseMode.MARKDOWN) 
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!",
            )
        except BadRequest as e:
            LOGGER.warning(e.message)


    start_handler = DisableAbleCommandHandler("start", start)

    help_handler = DisableAbleCommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(
        vegeta_about_callback, pattern=r"vegeta_", run_async=True
    )
    
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(
          listen="0.0.0.0",
          port=PORT,
          url_path=TOKEN
        )

        if CERT_PATH:
            updater.bot.set_webhook(
               url=URL + TOKEN, 
               certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(
              url=URL + TOKEN
            )

    else:
        LOGGER.info("Vegeta Is Now Alive And Functioning")
      
        updater.start_polling(
             timeout=25, 
             read_latency=4, 
             drop_pending_updates=True
)
        if len(argv) not in (1, 3, 4):
            telethn.disconnect()
        else:
           telethn.run_until_disconnected()
    updater.idle()
    


if __name__ == '__main__':
    telethn.start(bot_token=TOKEN)
    pgram.start()
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()
