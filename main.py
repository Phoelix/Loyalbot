# -*- coding: utf-8 -*-
# CREATED BY PhoelixSky
from setupcon import setup_console
setup_console('utf-8', False)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove, ParseMode
from tools import IsUserAdmin, userInfo, logger
from sqlite3 import Error, IntegrityError
from MagicPanel import mainmenu, button
from datetime import datetime
from SQLite import SQLite
import random
import RU
import re





def start(bot, update):
    db    = SQLite()
    text  = update.message.text.split()
    user  = update.message.from_user
    logger.debug('User {} start'.format(userInfo(user)))
    exist = db.magic('select tgid from memb where tgid = (?)', (user.id,)).fetchall()
    if not exist:
        mnid = int(db.magic('select max(nid) from memb').fetchall()[0][0])
        mnid += 1
        startBonuses = db.magic('select val from temp where name = "sBonus"').fetchall()[0][0]
        try:
            db.magic(
                sql='insert into memb (nid, tgid, fname, nname, bal) VALUES (?,?,?,?,?)',
                data=(mnid,  user.id, user.first_name, user.username, startBonuses))
        except Error as e:
            logger.critical('USER Registration ERROR: User: {}\n{}'.format(userInfo(user), e))
        if len(text) == 2:
            db.magic('insert into referals (refer, referal) VALUES (?,?)',
                data=(text[1], mnid))
            logger.info('User {} was invited by {}'.format(userInfo(user), text[1]))
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
    logger.debug('User {} get referal'.format(userInfo(user)))


def addpin(bot, update):
    db = SQLite()
    user = update.message.from_user
    if IsUserAdmin(user):
        bonus_addr = update.message.text.split()
        text = RU.clientmesaddpin1
        try: account = db.magic('select bal, fname, tgid from memb where nid = {}'.format(str(bonus_addr[0]))).fetchall()[0]
        except: return bot.send_photo(user.id, RU.error404)
        bal = int(account[0])
        if len(bonus_addr) == 1:
            try:
                bal += 1
                mes=1
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} add 1 POINT to {}'.format(userInfo(user), bonus_addr[0]))
            except Error:
                return logger.error('User {}, error {}'.format(userInfo(user), Error))
        elif len(bonus_addr) >= 2:
            try: bal += int(bonus_addr[1])
            except TypeError:
                return bot.send_message(user.id, RU.valerror.format(bonus_addr[1]), parse_mode=ParseMode.HTML)
            try:
                mes = bonus_addr[1]
                text = random.choice(RU.clientmesaddpins)
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[0])),
                         data=(bal,))
                logger.info('User {} add {} POINTS to {}'.format(userInfo(user), bonus_addr[1], bonus_addr[0]))
            except Error:
                return logger.error('User {}, error {}'.format(userInfo(user), Error))
        try:
            refer = db.magic('select refer, used from referals where referal = {}'.format(bonus_addr[0])).fetchall()
            if refer[0][1] is None:
                rfr_acc = db.magic('select bal, fname, tgid from memb where nid = {}'.format(refer[0][0])).fetchall()
                try:
                    rbal = int(rfr_acc[0][0])
                    rbal += 1
                    db.magic('update memb set bal = (?) where nid = {}'.format(str(refer[0][0])),
                             data=(rbal,))
                    db.magic('update referals set used=1 where refer = (?) and referal = (?)', (refer[0][0],bonus_addr[0]))
                    logger.info('Account {} REFER and get 1 POINT for {}'.format(refer[0][0], bonus_addr[0]))
                except Error:
                    return logger.error('User {}, error {}'.format(userInfo(user), Error))
                bot.send_message(rfr_acc[0][3], RU.refrused, parse_mode=ParseMode.HTML)
        except: pass
        bot.send_message(account[2], text.format(account[1], mes))
        return update.message.reply_text(RU.addpin.format(
            str(account[1]),
            str(bonus_addr[0]).zfill(4),
            str(mes)),
            parse_mode=ParseMode.HTML)
    else:
        logger.info('NOT ADM {} input {}'.format(userInfo(user), update.message.text))
        return balfunc(bot, update)

def admcheckbal(bot, update):
    db = SQLite()
    user = update.message.from_user
    bal = update.message.text.split()
    del bal[0]
    if IsUserAdmin(user):
        account = []
        for i in bal:
            try: account.append(db.magic('select nid, fname, bal  from memb where nid = {}'.format(i)).fetchall()[0])
            except: return bot.send_photo(update.message.from_user.id, RU.error404, caption=RU.error404text.format(i))
        logger.info('Admin {} open bal {}'.format(userInfo(user), bal))
        answer = RU.manybalinfo
        for item in account:
            answer += '{}||{}{}\n'.format(str(item[0]).zfill(4), item[1].ljust(25, '_'), item[2])
        return update.message.reply_text(answer, parse_mode=ParseMode.HTML)
    else:
        logger.warning('NOT ADM {} open bal USE COMMAND /b {}'.format(userInfo(user), bal))
        return balfunc(bot,update)


def balfunc(bot, update):
    user = update.message.from_user
    db = SQLite()
    account = db.magic('select bal, fname, nid from memb where tgid = {}'.format(str(user.id))).fetchall()[0]
    return update.message.reply_text(RU.balinfo.format(
                                            str(account[1]),
                                            str(account[2]).zfill(4),
                                            str(account[0])),
                                            parse_mode=ParseMode.HTML)


def usebal(bot, update):
    db          = SQLite()
    user        = update.message.from_user
    bonus_addr  = update.message.text.split()
    if IsUserAdmin(user):
        if len(bonus_addr)>1:
            try:        account = db.magic('select bal, fname, tgid from memb where nid = {}'.format(str(bonus_addr[1]))).fetchall()[0]
            except:     return bot.send_photo(user.id, RU.error404, caption=RU.error404text.format(bonus_addr[1]))
            bal = int(account[0])
            if len(bonus_addr) == 3:
                    c = bonus_addr[2]
            else:   c = 1
            b = db.magic('select val from temp where name = "cupPrice"').fetchall()[0][0]
            used = int(b)*int(c)
            temp_bal = bal - used
            if temp_bal<0:
                logger.warning('Admin {} try to use bonuses but account {} has not enouth money'.format(userInfo(user), bonus_addr[1]))
                return update.message.reply_text(RU.notenothpoints.format(bal), parse_mode=ParseMode.HTML)
            else:
                db.magic('update memb set bal = (?) where nid = {}'.format(str(bonus_addr[1])), data=(temp_bal,))
                logger.info('User {} used {} POINTS from {} account '.format(userInfo(user), used, bonus_addr[1]))
            update.message.reply_text(RU.pointsused.format(used, temp_bal),
                                        parse_mode=ParseMode.HTML)
            bot.send_message(account[2], RU.clientpointsused.format(account[1], used, temp_bal),
                             parse_mode=ParseMode.HTML)
        else: return update.message.reply_text(RU.usehelp, parse_mode=ParseMode.HTML)
    else: return logger.warning('NOT ADM {} input /use'.format(userInfo(user)))


def sales(bot, update):                 # Sales output f-n
    db = SQLite()
    text = db.magic('select text from sales LIMIT 1').fetchall()[0][0]
    update.message.reply_text(text, parse_mode=ParseMode.HTML)


def fact(bot, update):                  # Fact output f-n
    db = SQLite()
    d = datetime.now().day
    request = db.magic('select lastfact, activity from memb where tgid = {}'.format(
        update.message.from_user.id)).fetchall()[0]
    if int(request[0])!=int(d):
        text = db.magic('select text from facts order by random() LIMIT 1').fetchall()[0][0]
        db.magic('update memb set lastfact = (?), activity = (?) where tgid = (?)', (d, int(request[1])+1, update.message.from_user.id))
        answer = text
    else:
        answer = RU.notToday
    update.message.reply_text(answer, parse_mode=ParseMode.HTML)


def addtotab(bot, update):              # /a or /f Adding 'a'ction or 'f'act to DB
    db = SQLite()
    data = update.message.text
    user=update.message.from_user
    if IsUserAdmin(user):
        if data[:2] == '/f':
            into = 'facts'
        else:               # text[:2] == '/a':
            into = 'sales'
        text = data[2:]
        sql = 'insert into {}(text) values ("{}")'.format(into, text)
        db.magic(sql)
        update.message.reply_text(RU.addaction)
        logger.info('User {} ADD ACTION({}...)!'.format(userInfo(user),text[:15]))
    else:
        logger.warning('NOT ADM {} use /f or /a'.format(userInfo(user)))


def helpF(bot, update):                         # /help command
    if IsUserAdmin(update.message.from_user):
        return update.message.reply_text(
            RU.adminhelp.format(update.message.from_user.first_name),
            parse_mode=ParseMode.HTML)
    else: return update.message.reply_text(RU.how, parse_mode=ParseMode.HTML)


def error(bot, update, error):
    logger.critical('Update {} caused error {}'.format(update, error))


def main():
    updater = Updater(RU.token)
    # Buttons
    updater.dispatcher.add_handler(RegexHandler   ('^{}$'.format(RU.mybal),   balfunc))
    updater.dispatcher.add_handler(RegexHandler   ('^{}$'.format(RU.refbut),  referal))
    updater.dispatcher.add_handler(RegexHandler   ('^{}$'.format(RU.howbut),  helpF))
    updater.dispatcher.add_handler(RegexHandler   ('^{}$'.format(RU.factbut), fact))
    updater.dispatcher.add_handler(RegexHandler   ('^{}$'.format(RU.salebut), sales))
    # Commands
    updater.dispatcher.add_handler(CommandHandler ('start',     start))
    updater.dispatcher.add_handler(CommandHandler ('help',      helpF))
    updater.dispatcher.add_handler(CommandHandler ('use',       usebal,      Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(CommandHandler ('b',         admcheckbal, Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(RegexHandler   ('^\d{1,4}',  addpin))
    updater.dispatcher.add_handler(CommandHandler ('m',         mainmenu,    Filters.user(username=RU.admins.split())))
    updater.dispatcher.add_handler(CommandHandler (('a','f'),   addtotab))
    # Inline Buttons
    updater.dispatcher.add_handler(CallbackQueryHandler(button, pass_user_data=True))
    # System
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
