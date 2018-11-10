# -*- coding: utf-8 -*-
import setupcon
setupcon.setup_console()
from telegram import InlineKeyboardButton
from functools import wraps
from SQLite import SQLite
import logging
import RU

if setupcon.ansi:
    logging.getLogger().addHandler(setupcon.ColoredHandler())

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',#   filename="WORKLOG.log",
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def build_menu(center,
               n_cols,
               header=None,
               footer=None):
    buttons = []
    header_buttons = []
    footer_buttons = []
    for item in center:
        buttons.append(InlineKeyboardButton(str(item[0]),callback_data=str(item[1])))
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header:
        for item in header:
            header_buttons.append(InlineKeyboardButton(str(item[0]), callback_data=str(item[1])))
        menu.insert(0, header_buttons)
    if footer:
        for item in footer:
            footer_buttons.append(InlineKeyboardButton(str(item[0]), callback_data=str(item[1])))
        menu.append(footer_buttons)
    return menu


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
        reply_markup.append([InlineKeyboardButton(' {}...'.format(item[1][:15]), callback_data=tab+str(item[0]))])
    reply_markup.append([InlineKeyboardButton("На головну", callback_data='back')])
    return reply_markup


def IsUserAdmin(user, perm=None):
    db = SQLite()
    admList = RU.admins.split()
    if user.username in admList: return '1'
    elif perm is None:
        admBase =db.magic('select tgid from admins')[0]
        if user.id in admBase: return '1'


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def userInfo(from_user):#f-n get info about user. :attr:`type` `0` - id, `1` - id+nname/name, `2` - name+nname/id
    template = str(from_user.id)
    if from_user.username: template += '::{}'.format(from_user.username)
    else: template += '::{}'.format(from_user.first_name)
    return template



def restricted(fname):
    def wrap(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            user = update.effective_user
            if user.username not in RU.admins.split():
                logger.warning("{} -- Unauthorized access to {} DENIED.".format(userInfo(user), fname))
                return
            return func(bot, update, *args, **kwargs)
        return wrapped
    return wrap
