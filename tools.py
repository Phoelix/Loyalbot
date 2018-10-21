from telegram import InlineKeyboardButton
from SQLite import SQLite
import RU


def HasUserName(user, forDB = None):
    if user.username:  return user.username
    elif forDB:        return user.id
    else:              return user.first_name


def MenuButs():
    return [[InlineKeyboardButton("Видалити Акцію", callback_data='a'), InlineKeyboardButton("Видалити Факт", callback_data='f')],
                [InlineKeyboardButton("Розсилка", callback_data='mailing')],
                [InlineKeyboardButton("Адміністрування", callback_data='adm')],
                [InlineKeyboardButton("Брись!", callback_data='out')]]


def PhrasesButs(tab):
    db = SQLite()
    reply_markup = []
    if tab == 'a':     result = db.magic('select * from sales').fetchall()
    else:              result = db.magic('select * from facts').fetchall()
    for item in result:
        reply_markup.append([InlineKeyboardButton(' {}...'.format(item[1][:15]), callback_data=tab+item[0])])
    reply_markup.append([InlineKeyboardButton("Назад", callback_data='back')])
    return reply_markup


def IsUserAdmin(user, perm=None):
    db = SQLite()
    admList = RU.admins.split()
    if user.username in admList: return '1'
    elif perm is None:
        admBase =db.magic('select tgid from admins')[0]
        if user.id in admBase: return '1'

