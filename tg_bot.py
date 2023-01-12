import os
from enum import Enum
import re
import random

import redis
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Actions(Enum):
    CHOOSING = 1
    TYPING_ANSWER = 2


quiz_elements = {}
redis_client = None


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Привет! Я бот для викторин', reply_markup=reply_markup)
    return Actions.CHOOSING.value


def handle_new_question_request(bot, update):
    chat_id = update.message.from_user.id
    new_question = random.choice(list(quiz_elements.keys()))
    redis_client.set(chat_id, new_question)
    update.message.reply_text(new_question)
    return Actions.CHOOSING.value


def handle_solution_attempt(bot, update):
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


def handle_capitulate(bot, update):
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
    path_quiz_files = os.environ['QUIZ_FILES_PATH']
    tg_token = os.environ['TG_TOKEN']
    redis_pswd = os.environ['REDIS_PASSWORD']
    redis_client = redis.Redis(
        host='redis-14680.c302.asia-northeast1-1.gce.cloud.redislabs.com',
        port=14680,
        password=redis_pswd)

    for filename in os.listdir(path_quiz_files):
        with open(os.path.join(path_quiz_files, filename), 'r', encoding='koi8-r') as f:
            content = f.read()
            content_splitted = re.split("\n{2}", content)
            question_re = re.compile(r'(\n?Вопрос\s\d+:\n)(.)')
            answer_re = re.compile(r'(Ответ:\n)(.)')
            question = ''
            answer = ''
            for content_item in content_splitted:
                question_match = question_re.match(content_item)
                answer_match = answer_re.match(content_item)
                question_idx = 0
                answer_idx = 0
                if question_match:
                    question_idx = question_match.start(2)
                    question = content_item[question_idx:]
                if answer_match:
                    answer_idx = answer_match.start(2)
                    answer = content_item[answer_idx:]
                if question and answer:
                    quiz_elements[question] = answer
                    question = ''
                    answer = ''

        updater = Updater(tg_token)

        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                Actions.CHOOSING.value: [RegexHandler('^(Новый вопрос)$',
                                                      handle_new_question_request),
                                         RegexHandler('^Сдаться$',
                                                      handle_capitulate),
                                         MessageHandler(Filters.text, handle_solution_attempt)]
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
