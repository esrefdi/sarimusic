"""
Video + Music Stream Telegram Bot
Copyright (c) 2022-present levina=lab <https://github.com/levina-lab>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/licenses.html>
"""


import asyncio

from datetime import datetime
from sys import version_info
from time import time

from config import (
    ALIVE_IMG,
    ALIVE_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_USERNAME,
    UPDATES_CHANNEL,
)

from program import __version__, LOGS
from pytgcalls import (__version__ as pytover)

from driver.filters import command
from driver.core import bot, me_bot, me_user
from driver.database.dbusers import add_served_user
from driver.database.dbchat import add_served_chat, is_served_chat
from driver.database.dblockchat import blacklisted_chats
from driver.database.dbpunish import is_gbanned_user
from driver.decorators import check_blacklist

from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@Client.on_message(
    command(["start", f"start@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
@check_blacklist()
async def start_(c: Client, message: Message):
    user_id = message.from_user.id
    await add_served_user(user_id)
    await message.reply_text(
        f"""Hi {message.from_user.mention()} ????????\n
???? [{me_bot.first_name}](https://t.me/{me_bot.username}) yeni Telegram video ??atlar?? vasit??sil?? qruplarda musiqi v?? video oynamaq ??????n botdur.

???????? Check out all the **Bot's commands** and how they work by clicking on the ?? ???? **Commands** button!

??????????????? To know how to use this bot, please click on the ?? ??? **Basic Guide** button!
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("??? M??ni Qrupa ??lav?? et ???", url=f"https://t.me/{me_bot.username}?startgroup=true")
                ],[
                    InlineKeyboardButton("??? ??sas B??l??d??i", callback_data="user_guide")
                ],[
                    InlineKeyboardButton("???? ??mrl??r", callback_data="command_list"),
                    InlineKeyboardButton("?????? Ba??????lay??n", url=f"https://t.me/{OWNER_USERNAME}")
                ],[
                    InlineKeyboardButton("???? D??st??k Qrupu", url=f"https://t.me/{GROUP_SUPPORT}"),
                    InlineKeyboardButton("???? D??st??k Kanal??", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],[
                    InlineKeyboardButton("???? M??nb?? kodu", url="https://github.com/levina-lab/video-stream")
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_message(
    command(["alive", f"alive@{BOT_USERNAME}"]) & filters.group & ~filters.edited
)
@check_blacklist()
async def alive(c: Client, message: Message):
    chat_id = message.chat.id
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("??? Group", url=f"https://t.me/{GROUP_SUPPORT}"),
                InlineKeyboardButton(
                    "???? Kanal", url=f"https://t.me/{UPDATES_CHANNEL}"
                ),
            ]
        ]
    )
    text = f"**Salam {message.from_user.mention()}, I'm {me_bot.first_name}**\n\n??????????????? My Master: [{ALIVE_NAME}](https://t.me/{OWNER_USERNAME})\n???? Bot Versiyas??: `v{__version__}`\n???? Pyrogram Version: `{pyrover}`\n???? Python Version: `{__python_version__}`\n??? PyTgCalls Versiyas??: `{pytover.__version__}`\n???? ???? vaxt?? statusu: `{uptime}`\n\n??? **TM??ni buraya ??lav?? etdiyiniz ??????n, Qrupunuzun video ??at??nda video v?? musiqi ifa etdiyiniz ??????n t??????kk??rl??r**"
    await c.send_photo(
        chat_id,
        photo=f"{ALIVE_IMG}",
        caption=text,
        reply_markup=buttons,
    )


@Client.on_message(command(["ping", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def ping_pong(c: Client, message: Message):
    start = time()
    m_reply = await message.reply_text("pinging...")
    delta_ping = time() - start
    await m_reply.edit_text("???? PONG !\n" f"??? `{delta_ping * 1000:.3f} ms`")


@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def get_uptime(c: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        f"??? Uptime: `{uptime}`\n"
        f"??? Start Time: `{START_TIME_ISO}`"
    )


@Client.on_chat_join_request()
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    if not m.from_user:
        return
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
    except FloodWait as e:
        await asyncio.sleep(e.x + 2)
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)


@Client.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    chat_id = m.chat.id
    if await is_served_chat(chat_id):
        pass
    else:
        await add_served_chat(chat_id)
    for member in m.new_chat_members:
        try:
            if member.id == me_bot.id:
                if chat_id in await blacklisted_chats():
                    await m.reply_text(
                        "?????? Bu s??hb??t sudo istifad????isi t??r??find??n qara siyah??ya sal??n??b v?? Siz?? bu s??hb??td?? m??nd??n istifad?? etm??k icaz??niz yoxdur."
                    )
                    return await bot.leave_chat(chat_id)
            if member.id == me_bot.id:
                return await m.reply(
                    "?????? M??ni **Qrupa** ??lav?? etdiyiniz ??????n t??????kk??rl??r !\n\n"
                    "M??ni **Qrupa** administrator t??yin edin, ??ks halda d??zg??n i??l??y?? bilm??y??c??m v?? yazma???? unutmay??n `/userbotjoin` k??m??k??ini d??v??t etm??k ??????n.\n\n"
                     "Bir d??f?? tamamlay??n, sonra yaz??n `/reload`",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("???? Kanal", url=f"https://t.me/{UPDATES_CHANNEL}"),
                                InlineKeyboardButton("???? D??st??k", url=f"https://t.me/{GROUP_SUPPORT}")
                            ],[
                                InlineKeyboardButton("???? Assistant", url=f"https://t.me/{me_user.username}")
                            ]
                        ]
                    )
                )
            return
        except Exception:
            return


chat_watcher_group = 5

@Client.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message: Message):
    userid = message.from_user.id
    suspect = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_gbanned_user(userid):
        try:
            await message.chat.ban_member(userid)
        except ChatAdminRequired:
            LOGS.info(f"qada??an edilmi?? istifad????ini s??hb??td??n sil?? bilm??z: {message.chat.id}")
            return
        await message.reply_text(
            f"???????? (> {suspect} <)\n\n**Qada??an edilmi??** istifad????i a??karland??, h??min istifad????i sudo istifad????isi t??r??find??n bloklan??b v?? bu ??atdan bloklan??b!\n\n???? **S??b??b:** potensial spamer v?? sui-istifad????i."
        )
