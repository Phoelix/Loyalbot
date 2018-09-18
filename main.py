from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove
from sqlite3 import Error, IntegrityError
from SQLite import SQLite
import logging
import random
import tools
import RU
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',   #filename="WORKLOG.log",
                    level=logging.INFO)

logger = logging.getLogger(__name__)



def start(bot, update):
    user = update.message.from_user
    logger.info('User {} start'.format(user.first_name))
    db = SQLite()
    isexistch = db.magic('select tgid from memb where tgid = (?)', (user.id,)).fetchall()
    if not isexistch:
        mnid = int(db.magic('select max(nid) from memb').fetchall()[0][0])
        mnid += 1
        try:
            db.magic(
                sql='insert into memb (nid, tgid, fname, nname, bal) VALUES (?,?,?,?,?)',
                data=(mnid,  user.id, user.first_name, user.username, RU.startbonuses))
        except Error as e:
            logger.error('USER Registration ERROR: User: {}\n{}'.format(user.id, e))
        text = update.message.text.split()
        if len(text) == 2:
            db.magic('insert into referals (refer, referal) VALUES (?,?)',
                data=(text[1], mnid))
            logger.info('User {} was invited by {}'.format(user.first_name, text[1]))
    else:
        mnid = db.magic('select nid from memb where tgid = {}'.format(user.id)).fetchall()[0][0]
    markup = [[RU.mybal], [RU.refbut, RU.salebut], [RU.howbut, RU.factbut]]
    update.message.reply_text(RU.welcome.format(user.first_name, mnid), reply_markup=ReplyKeyboardMarkup(markup),
                              resize_keyboard=True)


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
                mes=1
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} admin and add 1 POINT to {}'.format(user.first_name, bonus_addr[0]))
            except Error:
                return logger.info('User "%s", error "%s"' % (user.id, Error))
        elif len(bonus_addr) == 2:
            try:
                bal += int(bonus_addr[1])
                mes = bonus_addr[1]
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} admin and add {} POINTS to {}'.format(user.first_name, bonus_addr[1], bonus_addr[0]))
            except Error:
                return logger.info('User "%s", error "%s"' % (user.id, Error))
        try:
            refer = db.magic('select refer, used from referals where referal= {}'.format(bonus_addr[0])).fetchall()
            if refer[0][1] is None:
                rfr_acc = db.magic('select bal, fname from memb where nid = {}'.format(refer[0][0])).fetchall()
                try:
                    rbal = int(rfr_acc[0][0])
                    rbal += 1
                    db.magic('update memb set bal = (?) where nid = {}'.format(str(refer[0][0])),
                             data=(rbal,))
                    db.magic('update referals set used=1 where refer = (?) and referal = (?)', (refer[0][0],bonus_addr[0]))
                    logger.info('Account {} REFER and get 1 POINT for {}'.format(refer[0][0], bonus_addr[0]))
                except Error:
                    return logger.info('User "%s", error "%s"' % (user.id, Error))
                sendMessto = db.magic('select tgid from memb where nid = {}'.format(refer[0][0])).fetchall()[0][0]
                bot.send_message(sendMessto, RU.refrused)
        except: pass

        return update.message.reply_text(RU.addpin.format(str(account[0][1]), str(bonus_addr[0]), str(mes)))

        #TODO text RU.addbonus
    else:
        logger.info('User {} input {} NO_ADMIN'.format(user.first_name, update.message.text))
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


def admcheckbal(bot, update):
    db = SQLite()
    user = update.message.from_user
    bal = update.message.text.split()[1]
    adm_list = RU.admins.split()
    if user.username in adm_list or user.name in adm_list:
        account = db.magic('select bal, fname, nid from memb where nid = {}'.format(str(bal))).fetchall()
        logger.info('Admin {} open bal {}'.format(user.first_name, bal))
        return update.message.reply_text(RU.balinfo.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))
    else:
        account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
        logger.info('User {} open bal USE COMMAND /b {}'.format(user.first_name, bal))
        return update.message.reply_text(RU.balinfo.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))

def balfunc(bot, update):
    user = update.message.from_user
    db = SQLite()
    account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
    logger.info('User {} open bal'.format(user.first_name))
    return update.message.reply_text(RU.balinfo.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))


def how(bot, update):
    update.message.reply_text(RU.how)


def sales(bot, update):
    db = SQLite()
    text = db.magic('select min(cou),text, id from sales LIMIT 1').fetchall()
    db.magic('update sales set cou = cou+1 where id = (?)', (text[0][2],))
    update.message.reply_text(text[0][1])


def fact(bot, update):
    db = SQLite()
    text = db.magic('select min(cou),text, id from facts LIMIT 1').fetchall()
    db.magic('update facts set cou = cou+1 where id = (?)', (text[0][2],))
    update.message.reply_text(text[0][1])


def addtotab(bot, update):
    db = SQLite()
    text = update.message.text
    user=update.message.from_user
    instype = str(re.match(r'^\w+', text).group(0))
    if len(instype) == 4:
        db.magic('insert into facts(text) values (?)', (text[4:],))
        update.message.reply_text(RU.addfact)
        logger.info('User {}:{} ADD FACT!'.format(user.id,user.username))
    elif len(instype)>=5:
        db.magic('insert into sales(text) values (?)', (text,))
        update.message.reply_text(RU.addsale)
        logger.info('User {}:{} ADD S A L E!'.format(user.id,user.username))



def error(bot, update, error):
    logger.info('Update {} caused error {}'.format(update, error), False)

def main():
    updater = Updater(RU.token)

    magichandler = tools.magicpanel()

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.mybal), balfunc))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.refbut), referal))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.howbut), how))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.factbut), fact))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.salebut), sales))
    updater.dispatcher.add_handler(CommandHandler('use', release))
    updater.dispatcher.add_handler(CommandHandler('b', admcheckbal))
    updater.dispatcher.add_handler(RegexHandler('^\d{5}',  addpin))
    updater.dispatcher.add_handler(CommandHandler('help', how))
    updater.dispatcher.add_handler(magichandler)
    updater.dispatcher.add_handler(CallbackQueryHandler(tools.button))
    updater.dispatcher.add_handler(MessageHandler(Filters.user(username=RU.admins.split()), addtotab))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()