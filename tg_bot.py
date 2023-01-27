from enum import Enum
import re
import random
from functools import partial

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
import logging.config

from file_parser import file_parser
from log.config import log_config

logger = logging.getLogger('bot-quiz')


class Actions(Enum):
    CHOOSING = 1
    TYPING_ANSWER = 2


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Привет! Я бот для викторин', reply_markup=reply_markup)
    return Actions.CHOOSING.value


def handle_new_question_request(bot, update, quiz_elements, redis_client):
    chat_id = update.message.from_user.id
    new_question = random.choice(list(quiz_elements.keys()))
    redis_client.set(chat_id, new_question)
    update.message.reply_text(new_question)
    return Actions.CHOOSING.value


def handle_solution_attempt(bot, update, quiz_elements, redis_client):
    chat_id = update.message.from_user.id
    user_message = update.message.text
    question = redis_client.get(chat_id).decode('utf-8')
    correct_answer = quiz_elements.get(question)
    correct_answer = re.sub(r'\([^()]*\)', '', correct_answer)
    correct_answer = re.sub(r'\.(?!\w)', '', correct_answer)
    correct_answer = correct_answer.rstrip()
    match = re.fullmatch(user_message, correct_answer, flags=re.IGNORECASE)
    if match:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')

    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return Actions.CHOOSING.value


def handle_capitulate(bot, update, quiz_elements, redis_client):
    chat_id = update.message.from_user.id
    question = redis_client.get(chat_id).decode('utf-8')
    correct_answer = quiz_elements.get(question)
    update.message.reply_text(f'Правильный ответ: {correct_answer}')

    new_question = random.choice(list(quiz_elements.keys()))
    redis_client.set(chat_id, new_question)
    update.message.reply_text(new_question)

    return Actions.CHOOSING.value


def done(bot, update):
    return ConversationHandler.END


def main():
    env = Env()
    env.read_env()
    path_quiz_files = env('QUIZ_FILES_PATH')
    tg_token = env('TG_TOKEN')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_pswd = env('REDIS_PASSWORD')

    logging.config.dictConfig(log_config)
    logger.info('ТГ-бот запущен')

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_pswd)
    quiz_elements = file_parser(path_quiz_files)
    handler_kwargs = {
        'quiz_elements': quiz_elements,
        'redis_client': redis_client
    }
    handle_new_question_request_partial = partial(handle_new_question_request, **handler_kwargs)
    handle_solution_attempt_partial = partial(handle_solution_attempt, **handler_kwargs)
    handle_capitulate_partial = partial(handle_capitulate, **handler_kwargs)

    updater = Updater(tg_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Actions.CHOOSING.value: [RegexHandler('^(Новый вопрос)$',
                                                  handle_new_question_request_partial),
                                     RegexHandler('^Сдаться$',
                                                  handle_capitulate_partial),
                                     MessageHandler(Filters.text, handle_solution_attempt_partial)]
        },
        fallbacks=[RegexHandler('^Мой счет$', done)]
    )

    dp.add_handler(conv_handler)
    logger.info('Запущен бот для викторин')
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
