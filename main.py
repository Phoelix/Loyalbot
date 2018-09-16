from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler
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
    logger.info('User {} start'.format(user.first_name))
    db = SQLite()
    r_nID = 0
    isexistch = db.magic('select tgid from memb where tgid = (?)', (user.id,)).fetchall()
    if not isexistch:
        for i in range(0, 5):  # (1,4):)
            r_nID += int(random.randint(1, 9) * 10 ** i)
        check = db.magic('select nid from memb where nid = (?)', (r_nID,)).fetchall()
        if check:
            r_nID = 0
            for i in range(0, 5):  # (1,4):)
                r_nID += int(random.randint(1, 9) * 10 ** i)
        try:
            db.magic(
                sql='insert into memb (nid, tgid, fname, nname, bal) VALUES (?,?,?,?,?)',
                data=(r_nID,  user.id, user.first_name, user.name, RU.startbonuses))
        except Error as e:
            logger.error('USER Registration ERROR: User: {}\n{}'.format(user.id, e))
        text = update.message.text.split()
        if len(text) == 2:
            db.magic('insert into referals (refer, referal) VALUES (?,?)',
                data=(text[1], r_nID))
            logger.info('User {} was invited by {}'.format(user.first_name, text[1]))
    markup = [[RU.mybal],[RU.refbut]]
    update.message.reply_text(RU.welcome.format(user.first_name, r_nID), reply_markup=ReplyKeyboardMarkup(markup), resize_keyboard=True)


def referal(bot, update):
    db = SQLite()
    user = update.message.from_user
    refer = db.magic('select nid from memb where tgid = (?)', (user.id,)).fetchall()[0][0]
    update.message.reply_text(RU.getref.format(refer))
    logger.info('User {} get referal'.format(user.first_name))


def addpin(bot, update):
    db = SQLite()
    user = update.message.from_user
    bonus_addr = update.message.text.split()
    adm_list = RU.admins.split()

    if user.username in adm_list or user.name in adm_list:
        account = db.magic('select bal, fname from memb where nid = {}'.format(str(bonus_addr[0]))).fetchall()
        bal = int(account[0][0])
        if len(bonus_addr) == 1:
            try:
                bal += 1
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} admin and add 1 POINT to {}'.format(user.first_name, bonus_addr[0]))
            except Error:
                return logger.info('User "%s", error "%s"' % (user.id, Error))
        elif len(bonus_addr) == 2:
            try:
                bal += int(bonus_addr[1])
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} admin and add {} POINTS to {}'.format(user.first_name, bonus_addr[1], bonus_addr[0]))
            except Error:
                return logger.info('User "%s", error "%s"' % (user.id, Error))
        return update.message.reply_text('{} {} {}'.format(str(account[0][1]), str(bonus_addr[0]), str(bal)))                                                #TODO text RU.addbonus
    else:
        logger.info('User {} input {} referal'.format(user.first_name, update.message.text))
        account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
        return update.message.reply_text(RU.balinfo.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))     #TODO +RU.balinfo

def release(bot, update):
    db = SQLite()
    user = update.message.from_user
    bonus_addr = update.message.text.split()
    adm_list = RU.admins.split()
    if user.username in adm_list or user.name in adm_list:
        account = db.magic('select bal, fname from memb where nid = {}'.format(str(bonus_addr[1]))).fetchall()
        bal = int(account[0][0])
        if len(bonus_addr) == 3:
            b = RU.bonuses_to_cup
            c = bonus_addr[2]
            used = int(b)*int(c)
            temp_bal = bal - used
            if temp_bal<0:
                logger.info('User {} has not enouth money'.format(user.first_name))
                return update.message.reply_text(RU.notenothpoints.format(bal))
            else:
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[1])), data=(temp_bal,))
                logger.info('User {} used {} POINTS from {} account '.format(user.first_name, used, bonus_addr[1]))
        else:
            used = int(RU.bonuses_to_cup)
            temp_bal = bal - int(RU.bonuses_to_cup)
            if temp_bal<0:
                logger.info('User {} has not enouth money'.format(user.first_name))
                return update.message.reply_text(RU.notenothpoints.format(bal))
            else:
                db.magic('update memb set bal = (?) where nid = {}'.format(bonus_addr[1]), data=(temp_bal,))
                logger.info('User {} give 1 CUP to {}'.format(user.first_name,bonus_addr[1] ))
        update.message.reply_text(RU.pointsused.format(used, temp_bal))





def balfunc(bot, update):
    user = update.message.from_user
    update.message.reply_text(RU.balinfo)
    db = SQLite()
    account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
    logger.info('User {} open bal'.format(user.first_name))
    return update.message.reply_text('{} {} {}'.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))


def error(bot, update, error):
    logger.info('Update {} caused error {}'.format(update, error), False)

def main():
    updater = Updater(RU.token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.mybal), balfunc))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.refbut), referal))
    updater.dispatcher.add_handler(CommandHandler('use', release))                     #TODO , Filters.user()
    updater.dispatcher.add_handler(RegexHandler('^\d{5}',  addpin))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()