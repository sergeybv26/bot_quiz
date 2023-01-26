import os
import re

import redis
from environs import Env

import vk_bot

if __name__ == '__main__':
    env = Env()
    env.read_env()
    path_quiz_files = env('QUIZ_FILES_PATH')
    tg_token = env('TG_TOKEN')
    vk_token = env('VK_TOKEN')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_pswd = env('REDIS_PASSWORD')

    quiz_elements = {}

    # init Redis
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
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
    vk_bot.main(quiz_elements, redis_client)
