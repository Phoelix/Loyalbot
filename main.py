# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove, ParseMode
from sqlite3 import Error, IntegrityError
from datetime import datetime
from SQLite import SQLite
import logging
import random
import tools
import RU
import re

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',   filename="WORKLOG.log",
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
    update.message.reply_text(RU.welcome.format(user.first_name, str(mnid).zfill(4)), reply_markup=ReplyKeyboardMarkup(markup),
                              resize_keyboard=True, parse_mode=ParseMode.HTML)


def referal(bot, update):
    db = SQLite()
    user = update.message.from_user
    refer = db.magic('select nid from memb where tgid = (?)', (user.id,)).fetchall()[0][0]
    update.message.reply_text(RU.getref.format(refer), parse_mode=ParseMode.HTML)
    #logger.info('User {} get referal'.format(user.first_name))


def addpin(bot, update):
    db = SQLite()
    user = update.message.from_user
    bonus_addr = update.message.text.split()
    adm_list = RU.admins.split()
    text = RU.clientmesaddpin1
    if user.username in adm_list or user.name in adm_list:
        try: account = db.magic('select bal, fname, tgid from memb where nid = {}'.format(str(bonus_addr[0]))).fetchall()[0]
        except: return bot.send_photo(user.id, RU.error404)
        bal = int(account[0])
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
                if int(bonus_addr[1])==2:
                    text = RU.clientmesaddpin2
                else: text = RU.clientmesaddpinmany
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
        bot.send_message(account[2], text.format(account[1], mes))
        return update.message.reply_text(RU.addpin.format(
            str(account[1]),
            str(bonus_addr[0]).zfill(4),
            str(mes)),
            parse_mode=ParseMode.HTML)
    else:
        logger.info('User {} input {} NO_ADMIN'.format(user.first_name, update.message.text))
        return balfunc(bot, update)

def usebal(bot, update):
    db = SQLite()
    user = update.message.from_user
    bonus_addr = update.message.text.split()
    adm_list = RU.admins.split()
    if user.username in adm_list or user.name in adm_list:
        if len(bonus_addr)>1:
            try: account = db.magic('select bal, fname, tgid from memb where nid = {}'.format(str(bonus_addr[1]))).fetchall()[0]
            except: return bot.send_photo(user.id, RU.error404)
            bal = int(account[0])
            if len(bonus_addr) == 3:
                b = RU.bonuses_to_cup
                c = bonus_addr[2]
                used = int(b)*int(c)
                temp_bal = bal - used
                if temp_bal<0:
                    logger.info('User {} has not enouth money'.format(user.first_name))
                    return update.message.reply_text(RU.notenothpoints.format(bal), parse_mode=ParseMode.HTML)
                else:
                    db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[1])), data=(temp_bal,))
                    logger.info('User {} used {} POINTS from {} account '.format(user.first_name, used, bonus_addr[1]))
                update.message.reply_text(RU.pointsused.format(used, temp_bal),
                                            parse_mode=ParseMode.HTML)
            elif len(bonus_addr) == 2:
                used = int(RU.bonuses_to_cup)
                temp_bal = bal - int(RU.bonuses_to_cup)
                if temp_bal<0:
                    logger.info('User {} has not enouth money'.format(user.first_name))
                    return update.message.reply_text(RU.notenothpoints.format(bal), parse_mode=ParseMode.HTML)
                else:
                    db.magic('update memb set bal = (?) where nid = {}'.format(bonus_addr[1]), data=(temp_bal,))
                    logger.info('User {} give 1 CUP to {}'.format(user.first_name,bonus_addr[1] ))
                update.message.reply_text(RU.pointsused.format(used, temp_bal), parse_mode=ParseMode.HTML)
                bot.send_message(account[2], RU.clientpointsused.format(account[1], used, temp_bal), parse_mode=ParseMode.HTML)
        else: return update.message.reply_text(RU.usehelp, parse_mode=ParseMode.HTML)

def admcheckbal(bot, update):
    db = SQLite()
    user = update.message.from_user
    bal = update.message.text.split()[1]
    adm_list = RU.admins.split()
    if user.username in adm_list or user.name in adm_list:
        try: account = db.magic('select bal, fname, nid from memb where nid = {}'.format(str(bal))).fetchall()[0]
        except: return bot.send_photo(update.message.from_user.id, RU.error404)
        logger.info('Admin {} open bal {}'.format(user.first_name, bal))
        return update.message.reply_text(RU.balinfo.format(
            str(account[1]),
            str(account[2]).zfill(4),
            str(account[0])),
            parse_mode=ParseMode.HTML)
    else:
        # account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
        logger.info('User {} open bal USE COMMAND /b {}'.format(user.first_name, bal))
        return balfunc(bot,update)
        # return update.message.reply_text(RU.balinfo.format(str(account[0][1]), str(account[0][2]), str(account[0][0])))

def balfunc(bot, update):
    user = update.message.from_user
    db = SQLite()
    account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()
    #logger.info('User {} open bal'.format(user.first_name))
    return update.message.reply_text(RU.balinfo.format(
        str(account[0][1]),
        str(account[0][2]).zfill(4),
        str(account[0][0])),
        parse_mode=ParseMode.HTML)


def how(bot, update):
    update.message.reply_text(RU.how, parse_mode=ParseMode.HTML)


def sales(bot, update):
    db = SQLite()
    text = db.magic('select min(cou),text, id from sales LIMIT 1').fetchall()
    db.magic('update sales set cou = cou+1 where id = (?)', (text[0][2],))
    update.message.reply_text(text[0][1], parse_mode=ParseMode.HTML)


def fact(bot, update):
    db = SQLite()
    d = datetime.now().day
    last = db.magic('select lastfact from memb where tgid = {}'.format(
        update.message.from_user.id)).fetchall()[0][0]
    if int(last)!=0: #int(d):
        text = db.magic('select text, id from facts LIMIT 1').fetchall() #order by random()
        db.magic('update memb set lastfact = (?) where tgid = (?)', (d,update.message.from_user.id))
        answer = text[0][0]
    else:
        answer = RU.notToday
    update.message.reply_text(answer, parse_mode=ParseMode.HTML)


def addtotab(bot, update):
    db = SQLite()
    text = update.message.text
    adm_list = RU.admins.split()
    user=update.message.from_user
    instype = str(re.match(r'^\w+', text).group(0))
    if user.username in adm_list or user.name in adm_list:
        if len(instype) == 4:
            db.magic('insert into facts(text) values (?)', (text[4:],))
            update.message.reply_text(RU.addfact)
            logger.info('User {}:{} ADD FACT!'.format(user.id,user.username))
        elif len(instype)>=5:
            db.magic('insert into sales(text) values (?)', (text,))
            update.message.reply_text(RU.addsale)
            logger.info('User {}:{} ADD S A L E!'.format(user.id,user.username))
    

def adminhelp(bot, update):
    return update.message.reply_text(
        RU.adminhelp.format(update.message.from_user.first_name),
        parse_mode=ParseMode.HTML)

def error(bot, update, error):
    logger.info('Update {} caused error {}'.format(update, error), False)


def main():
    updater = Updater(RU.token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('imfish', adminhelp, Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.mybal), balfunc))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.refbut), referal))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.howbut), how))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.factbut), fact))
    updater.dispatcher.add_handler(RegexHandler('^{}$'.format(RU.salebut), sales))
    updater.dispatcher.add_handler(CommandHandler('use', usebal, Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(CommandHandler('b', admcheckbal, Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(RegexHandler('^\d{1,4}',  addpin))
    updater.dispatcher.add_handler(CommandHandler('help', how))
    updater.dispatcher.add_handler(CommandHandler('m', tools.mmainmenu, Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(CallbackQueryHandler(tools.button))
    updater.dispatcher.add_handler(MessageHandler(Filters.user(username=RU.admins.split()), addtotab))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
