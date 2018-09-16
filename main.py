from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove
from SQLite import SQLite
from sqlite3 import Error, IntegrityError
import random
import logging
import RU

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',   #filename="WORKLOG.log",
                    level=logging.INFO)

logger = logging.getLogger(__name__)



def start(bot, update):
    user = update.message.from_user
    db = SQLite()
    r_nID = 0
    for i in range(0, 5):  # (1,4):)
        r_nID += int(random.randint(1, 9) * 10 ** i)
    check = db.magic('select nid from memb where nid = (?)', r_nID)
    try:
        db.magic(
            sql='insert or ignore into memb (nid, tgid, fname, uname) VALUES (?,?,?,?)',
            data=(r_nID,  user.id, user.name, user.first_name))
    except IntegrityError:
        r_nID = 0
        for i in range(0, 5):  # (1,4):)
            r_nID += int(random.randint(1, 9) * 10 ** i)
            try:db.magic(
                sql='insert or ignore into memb (nid, tgid, fname, uname) VALUES (?,?,?,?)',
                data=(r_nID, user.id, user.name, user.first_name))
            except IntegrityError:
                        user.

    except Error:
        return  logger.info('User "%s", error "%s"' % (user.id, Error))
    markup = [[RU.mybal]]
    update.message.reply_text(RU.welcome, reply_markup=ReplyKeyboardMarkup(markup), resize_keyboard=True)


def addpin(bot, update):                  #TODO split
    user = update.message.from_user
    db = SQLite()
    try:
        db.magic(
            sql='insert or ignore into Memb (tgID, fname, uname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return logger.info('User "%s", error "%s"' % (user.id, Error))


def bal(bot, update):
    user = update.message.from_user
    db = SQLite()
    try:
        db.magic(
            sql='insert or ignore into Memb (tgID, fname, uname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return logger.info('User "%s", error "%s"' % (user.id, Error))

def error(bot, update, error):
    logger.info('Update {} caused error {}'.format(update, error), False)

def main():
    updater = Updater(RU.token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler((Filters.text, Filters.user(username=RU.admins)), addpin))
    updater.dispatcher.add_handler(MessageHandler(RU.mybal, bal))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()