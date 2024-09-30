import os
import textwrap
import time
from datetime import datetime
from time import time

from PIL import Image, ImageChops, ImageDraw
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from VIPMUSIC import app
from VIPMUSIC.mongo.imgwelcome_db import dwelcome_off, dwelcome_on, is_dwelcome_on
from VIPMUSIC.utils.vip_ban import admin_filter

SUDO_USERS = ["7078181502", "6346273488"]
BOT_USERNAME = "Baby_dark_music_rebot"
LOG_CHANNEL = (-1002009280180)

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    


def circle(pfp, size=(259, 259)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


def draw_multiple_line_text(image, text, font, text_start_height):
    """
    From unutbu on [python PIL draw multiline text on image](https://stackoverflow.com/a/7698300/395857)
    """
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=50)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(
            ((image_width - line_width) / 2, y_text), line, font=font, fill="black"
        )
        y_text += line_height


def welcomepic(pic, user, chat, user_id):
    background = Image.open(
        "VIPMUSIC/assets/Goku.png"
    )  # <- Background Image (Should be PNG)
    background = background.resize(
        (background.size[0], background.size[1]), Image.ANTIALIAS
    )
    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp, size=(259, 259))  # Adjust the size of the circle pfp here
    pfp_x = 55  # Adjust the X coordinate to position the profile picture on the left
    pfp_y = (background.size[1] - pfp.size[1]) // 2 + 38
    background.paste(
        pfp, (pfp_x, pfp_y), pfp
    )  # Pastes the Profilepicture on the Background Image
    welcome_image_path = f"downloads/welcome_{user_id}.png"
    background.save(
        welcome_image_path
    )  # Saves the finished Image in the folder with the filename
    return welcome_image_path


@app.on_chat_member_updated(filters.group)
async def member_has_joined(client, member: ChatMemberUpdated):
    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return
    user = member.new_chat_member.user if member.new_chat_member else member.from_user
    if user.id in SUDO_USERS:
        await client.send_message(member.chat.id, "**Global Admins Joined The Chat!**")
        return
    elif user.is_bot:
        return  # ignore bots
    else:
        chat_id = member.chat.id
        welcome_enabled = await is_dwelcome_on(chat_id)
        if not welcome_enabled:
            return  # Welcome message is disabled for this chat

        if f"welcome-{chat_id}" in temp.MELCOW:
            try:
                await temp.MELCOW[f"welcome-{chat_id}"].delete()
            except:
                pass
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        joined_date = datetime.fromtimestamp(time.time()).strftime("%Y.%m.%d %H:%M:%S")
        first_name = (
            f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        )
        user_id = user.id
        dc = user.dc_id
        try:
            pic = await client.download_media(
                user.photo.big_file_id, file_name=f"pp{user_id}.png"
            )
        except AttributeError:
            pic = "Curse/extras/profilepic.png"
        try:
            welcomeimg = welcomepic(pic, user.first_name, member.chat.title, user_id)
            temp.MELCOW[f"welcome-{chat_id}"] = await client.send_photo(
                member.chat.id,
                photo=welcomeimg,
                caption=f"""Hᴇʟʟᴏ {mention}, Wᴇʟᴄᴏᴍᴇ Tᴏ {member.chat.title} Gʀᴏᴜᴘ.\n
    ┏━━━━━━━♛━━━━━━━┓
⍟ Nᴀᴍᴇ : {first_name}
⍟ Iᴅ : {user.id}
⍟ Dᴀᴛᴇ ᴊᴏɪɴᴇᴅ : {joined_date}
┗━━━━━━━♛━━━━━━━┛
""",
            )
        except Exception as e:
            print(e)
        try:
            os.remove(f"downloads/welcome_{user_id}.png")
            os.remove(f"downloads/pp{user_id}.png")
        except Exception:
            pass


@app.on_message(filters.command("dwelcome on") & admin_filter)
async def enable_welcome(_, message: Message):
    chat_id = message.chat.id
    welcome_enabled = await is_dwelcome_on(chat_id)
    if welcome_enabled:
        await message.reply_text("Default welcome is already enabled")
        return
    await dwelcome_on(chat_id)
    await message.reply_text("New default welcome message enabled for this chat.")


@app.on_message(filters.command("dwelcome off") & admin_filter)
async def disable_welcome(_, message: Message):
    chat_id = message.chat.id
    welcome_enabled = await is_dwelcome_on(chat_id)
    if not welcome_enabled:
        await message.reply_text("Default welcome is already disabled")
        return
    await dwelcome_off(chat_id)
    await message.reply_text("New default welcome disabled for this chat.")

