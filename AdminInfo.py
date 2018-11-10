# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, ParseMode
from sqlite3 import Error, IntegrityError
from SQLite import SQLite
from tools import *
import random
import string
import RU
import re

@restricted('Admin Menu')
def adminMenu(bot, update):
    db = SQLite()
    query = update.effective_message
    head_btns = [["Список адміністраторів", 'alist']]
    bttn_list = [["Гра", 'game'], ["Додати адміна", 'addadm']]
    foot_btns = [["На головну", 'back']]
    markup = build_menu(bttn_list,1,head_btns,foot_btns)
    bot.edit_message_text(text="Вітаємо в Адмін Панелі",
                          chat_id=query.chat_id,
                          message_id=query.message_id,
                          reply_markup=InlineKeyboardMarkup(markup))


def aList(bot, update):
    db = SQLite()
    alist = db.magic('select nid, fname from memb where tgid in (select tgid from admins)').fetchall()[0]


def addadm(bot, update):
    db = SQLite()