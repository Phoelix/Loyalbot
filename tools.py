from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from sqlite3 import Error, IntegrityError
from SQLite import SQLite
from main import logger
import logging
import random
import RU
import re


def magicpanel():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('m', mmainmenu, Filters.user(username=RU.admins.split()))],

        states={},

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    return conv_handler


def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    logger.info("User %s canceled the conversation.", user.first_name)
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def mmainmenu(bot, update):
    keyboard = [[InlineKeyboardButton("Удалить Акцию", callback_data='a')],
                [InlineKeyboardButton("Удалить Факт", callback_data='f')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Menu', reply_markup=reply_markup)
    logger.info('User {}:{} start Magic Panel'.format(update.message.from_user.id, update.message.from_user.username))


def button(bot, update):
    db = SQLite()
    query = update.callback_query
    res = query.data
    if res == 'a':
        reply_markup =[]
        result = db.magic('select * from sales').fetchall()
        for item in result:
            reply_markup.append([InlineKeyboardButton(str(item[1][:10]), callback_data='a{}'.format(item[0]))])
        reply_markup.append([InlineKeyboardButton("Назад", callback_data='back')])
        bot.edit_message_text(text="Выберите акцию для удаления",
                              reply_markup=InlineKeyboardMarkup(reply_markup),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
        logger.info('User {}:{} go to SALES DELETE PAGE'.format(query.from_user.id, query.from_user.username))
    elif res == 'f':
        reply_markup = []
        result = db.magic('select * from facts').fetchall()
        for item in result:
            reply_markup.append([InlineKeyboardButton(str(item[1][:10]), callback_data='f{}'.format(item[0]))])
        reply_markup.append([InlineKeyboardButton("Назад", callback_data='back')])
        bot.edit_message_text(text="Выберите факт для удаления",
                              reply_markup=InlineKeyboardMarkup(reply_markup),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        logger.info('User {}:{} go to FACTS DELETE PAGE'.format(query.from_user.id, query.from_user.username))
    elif re.match(r'^a\d+', query.data):
        delID = query.data[1:]
        result = db.magic('select * from sales where id = {}'.format(delID)).fetchall()
        db.magic('delete from sales where id = {}'.format(delID))
        bot.edit_message_text(text='{}\n\nАКЦИЯ УДАЛЕНА'.format(result[0][1]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        logger.info('User {}:{} DELETE SALE {}'.format(query.from_user.id, query.from_user.username,result[0][1]))
        return ConversationHandler.END
    elif re.match(r'^f\d+', query.data):
        delID = query.data[1:]
        result = db.magic('select * from facts where id = {}'.format(delID)).fetchall()
        db.magic('delete from facts where id = {}'.format(delID))
        bot.edit_message_text(text='{}\n\nФАКТ УДАЛЕН'.format(result[0][1]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        logger.info('User {}:{} DELETE FACT {}'.format(query.from_user.id, query.from_user.username,result[0][1]))
        return ConversationHandler.END
    elif res == 'back':
        reply_markup = [[InlineKeyboardButton("Удалить Акцию", callback_data='a')],
                    [InlineKeyboardButton("Удалить Факт", callback_data='f')]]
        bot.edit_message_text(text="Выберите факт для удаления",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(reply_markup))
        logger.info('User {}:{} go to main page'.format(query.from_user.id,query.from_user.username))