import logging
import logging.config
import random
import re

import redis
import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from file_parser import file_parser
from log.config import log_config

logger = logging.getLogger('bot-quiz')


def handle_new_question_request(event, vk_api, quiz_elements, redis_client):
    user_id = event.user_id
    new_question = random.choice(list(quiz_elements.keys()))
    redis_client.set(user_id, new_question)
    vk_api.messages.send(
        user_id=user_id,
        message=new_question,
        random_id=random.randint(1, 1000)
    )


def handle_solution_attempt(event, vk_api, quiz_elements, redis_client):
    user_id = event.user_id
    user_message = event.text
    question = redis_client.get(user_id).decode('utf-8')
    correct_answer = quiz_elements.get(question)
    correct_answer = re.sub(r'\([^()]*\)', '', correct_answer)
    correct_answer = re.sub(r'\.(?!\w)', '', correct_answer)
    correct_answer = correct_answer.rstrip()
    match = re.fullmatch(user_message, correct_answer, flags=re.IGNORECASE)
    if match:
        vk_api.messages.send(
            user_id=user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=random.randint(1, 1000)
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=random.randint(1, 1000)
        )


def handle_capitulate(event, vk_api, quiz_elements, redis_client):
    user_id = event.user_id
    question = redis_client.get(user_id).decode('utf-8')
    correct_answer = quiz_elements.get(question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ: {correct_answer}',
        random_id=random.randint(1, 1000)
    )

    new_question = random.choice(list(quiz_elements.keys()))
    redis_client.set(user_id, new_question)
    vk_api.messages.send(
        user_id=user_id,
        message=new_question,
        random_id=random.randint(1, 1000)
    )


def main():
    env = Env()
    env.read_env()
    path_quiz_files = env('QUIZ_FILES_PATH')
    vk_token = env('VK_TOKEN')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_pswd = env('REDIS_PASSWORD')

    logging.config.dictConfig(log_config)
    logger.info('ВК-бот запущен')

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_pswd)
    quiz_elements = file_parser(path_quiz_files)

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_api.messages.send(
                user_id=event.user_id,
                message='Привет! Я бот для викторин',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1, 1000)
            )
            if event.text == "Новый вопрос":
                handle_new_question_request(event, vk_api, quiz_elements, redis_client)
            if event.text == "Сдаться":
                handle_capitulate(event, vk_api, quiz_elements, redis_client)
            else:
                handle_solution_attempt(event, vk_api, quiz_elements, redis_client)


if __name__ == "__main__":
    main()
