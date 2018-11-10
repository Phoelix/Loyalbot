# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, ParseMode
from sqlite3 import Error, IntegrityError
from AdminInfo import adminMenu
from SQLite import SQLite
from tools import *
import random
import string
import RU
import re


def mainmenu(bot, update):
    query = update.effective_message
    try: update.callback_query.data
    except:
        bot.send_message(query.chat_id, 'Вітаю вас!')
        query.message_id += 1
    keyboard = MenuButs()
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text('Вітаю вас!\n 🔮 Я — магічна панель 🔮 ',
                          chat_id=query.chat_id,
                          message_id=query.message_id,
                          reply_markup=reply_markup)
    logger.debug('User {} start Magic Panel'.format(userInfo(query.from_user)))


def button(bot, update, user_data):
    query = update.callback_query
    res = query.data
    for case in switch(res):
        if case('adm'):
            adminMenu(bot, update)
            break
        if case('a', 'f'):
            selAction(bot, update)
            break
        if case('back'):
            mainmenu(bot, update)
            break
        if case('out'):
            outfunc(bot, update)
            break
        if case('mailing'):
            mailing(bot, update)
            break
        if case():
            delfunction(bot, update, res)
            break


def adminManage(bot, update):
    db = SQLite()
    query = update.callback_query
    user = update.callback_query.from_user
    if IsUserAdmin(user, perm=1):



        admBase = db.magic('select nid, fname from memb where tgid in (select tgid from admins)')[0]
        reply_markup = [[InlineKeyboardButton("", callback_data='del')]]


@restricted('Mailing')
def mailing(bot, update):
    db = SQLite()
    query = update.callback_query
    user = update.callback_query.from_user

def selAction(bot, update):
    db = SQLite()
    query = update.callback_query
    if query.data == 'a':
        reply_markup = PhrasesButs('a')
    else:
        reply_markup = PhrasesButs('f')
    bot.edit_message_text(text="Оберіть елемент для видалення",
                          reply_markup=InlineKeyboardMarkup(reply_markup),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    logger.info('User {} go to DELETE PAGE'.format(userInfo(query.from_user)))


def delfunction(bot, update, user_data):
    db = SQLite()
    query = update.callback_query
    delID = query.data[1:]
    if query.data[:1] == 'a':
        deletefrom = 'sales'
        answText = '</b>АКЦІЮ ВИДАЛЕНО</b>'
    else:
        deletefrom = 'facts'
        answText = '</b>ФАКТ ВИДАЛЕНО</b>'
    sql = 'select * from {} where id = {}'.format(deletefrom, delID)
    result = db.magic(sql).fetchall()
    sql = 'delete from {} where id = {}'.format(deletefrom, delID)
    db.magic(sql)
    bot.edit_message_text(text='{}\n\n'.format(result[0][1])+answText,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    logger.warning('User {} DELETE {}'.format(userInfo(query.from_user), result[0][1]))


def outfunc(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="Все, без питань. Ухожу! 🤗",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    logger.debug('User {} close Magic Tab'.format(userInfo(query.from_user)))

