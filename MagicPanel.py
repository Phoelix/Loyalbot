from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from sqlite3 import Error, IntegrityError
from SQLite import SQLite
from main import logger
from tools import *
import random
import RU
import re


def mmainmenu(bot, update):
    keyboard = MenuButs()
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Вітаю вас!\n 🔮 Я — магічна панель 🔮 ', reply_markup=reply_markup)
    logger.info('User {}:{} start Magic Panel'.format(update.message.from_user.first_name, HasUserName(update.message.from_user, forDB='1')))


def button(bot, update):
    query = update.callback_query
    res = query.data
    switch = {
        'a': selaction,
        'f': selaction,
        'back': mmainmenu,
        'out': outfunc,
        r'^a\d+|^f\d+': delfunction
    }
    if res in switch:
        task = switch[res]



def delfunction(bot, update):
    db = SQLite()
    query = update.callback_query
    delID = query.data[1:]
    if query.data[:1] == 'a':
        deletefrom = 'sales'
        answText = '</b>АКЦІЮ ВИДАЛЕНО</b>'
    else:
        deletefrom = 'facts'
        answText = '</b>ФАКТ ВИДАЛЕНО</b>'
    result = db.magic('select * from (?) where id = (?)', (deletefrom, delID)).fetchall()
    db.magic('delete from {} where id = {}'.format(deletefrom, delID))
    bot.edit_message_text(text='{}\n\n'.format(result[0][1])+answText,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.HTML)
    logger.info('User {}:{} DELETE {}'.format(query.from_user.first_name, HasUserName(query.from_user, forDB='1'), result[0][1]))
    return ConversationHandler.END


def selaction(bot, update):
    db = SQLite()
    query = update.callback_query
    if query.data == 'a':   reply_markup = PhrasesButs('a')
    else:                   reply_markup = PhrasesButs('f')
    bot.edit_message_text(text="Оберіть елемент для видалення",
                          reply_markup=InlineKeyboardMarkup(reply_markup),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    logger.warn('User {}:{} go to DELETE PAGE'.format(query.from_user.first_name, HasUserName(query.from_user, forDB='1')))


def outfunc(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="Все, без питань, я ухожу! 🤗",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    logger.info('User {}:{} close Magic Tab'.format(query.from_user.first_name, HasUserName(query.from_user, forDB='1')))

