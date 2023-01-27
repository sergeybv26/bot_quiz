import os
import re

from environs import Env


def file_parser(dir_path):
    """
    Выполняет парсинг файлов с вопросами и ответами викторины и возвращает словарь вида {вопрос: ответ}
    :param dir_path: Путь к файлам вопросов викторины
    """
    quiz_elements = {}

    for filename in os.listdir(dir_path):
        with open(os.path.join(dir_path, filename), 'r', encoding='koi8-r') as f:
            content = f.read()
            content_splitted = re.split(r"\n{2}", content)
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

    return quiz_elements


if __name__ == '__main__':
    env = Env()
    env.read_env()
    path_quiz_files = env('QUIZ_FILES_PATH')

    print(file_parser(path_quiz_files))
