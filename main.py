import os
import re

import redis

import vk_bot
import tg_bot


if __name__ == '__main__':
  path_quiz_files = os.environ['QUIZ_FILES_PATH']
  tg_token = os.environ['TG_TOKEN']
  redis_pswd = os.environ['REDIS_PASSWORD']

  quiz_elements = {}

  # init Redis
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
  vk_bot.main(quiz_elements, redis_client)
  tg_bot.main(quiz_elements, redis_client)
