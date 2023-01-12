# Бот "Проводим викторину"
Проводит викторину на знание истории.
## Основные системные требования:
* Ubuntu 20.04 LTS
* Python 3.9
* Зависимости из файла requirements.txt

## Запуск проекта
### Клонирование репозитория
Для клонирования репозитория необходимо установить git:
```shell
https://git-scm.com/downloads
```
Чтобы выполнить клонирование проекта из репозитория необходимо выполнить команду:
```shell
$ git clone https://github.com/sergeybv26/bot_quiz.git
```
После копирования проекта из репозитория появится директория bot_quiz

### Создание и активация виртуального окружения
```shell
$ cd bot_quiz/
$ python3 -m venv env
$ source env/bin/activate
```
Пример строки-приглашения после выполнения команды:
```shell
(env) user@user-pc:~/bot_quiz
```
### Установка зависимостей
```shell
$ pip3 install poetry
$ poetry install
```

### Получение чувствиетльных данных
Для работы приложения необходимо получить токен телеграм-бота, ссылку и пароль к серверу redis.

Для взаимодействия с API ВКонтакте необходимо получить ключ доступа:
* создать новое сообщество
* в сообществе перейти в Настройки/Работа с API
* создать ключ с правами управление сообществом и доступ к сообщениям сообщества

Для получения токена телеграм-бота необходимо:
* написать боту https://telegram.me/BotFather для создания нового телеграм-бота
* написать ```/start```, затем ```/newbot```
* ввести два имени: первое - как бот будет отбражаться в списке контактов, второе - имя, по которому его можно будет найти в поиске
* в ответном сообщении получаем токен нашего бота и сохраняем его

### Создание файла с переменными окружения
Переменные окружения для настройки проекта:
* ```QUIZ_FILES_PATH``` - Путь к файлам с вопросами и ответами
* ```REDIS_PASSWORD``` - Пароль сервера Redis
* ```TG_TOKEN``` -Токен телеграм-бота
* ```VK_TOKEN``` - Токен API ВКонтакте

Создать переменные окружения выполнив следующие команды:
```shell
$ export QUIZ_FILES_PATH=$HOME/bot_quiz/quiz-questions/
$ export REDIS_PASSWORD=<Enter your Redis password>
$ export TG_TOKEN=<Enter your Telegram token>
$ export VK_TOKEN=<Enter your VK token>
```

### Запуск приложения

Для запуска бота Телеграмм необходимо в командной строке выполнить команду:
```shell
python3 tg_bot.py
```

Для запуска бота ВКонтакте необходимо в командной строке выполнить команду:
```shell
python3 main.py
```

Ознакомиться с функционалом бота-помощника можно:
* Телеграм ```https://t.me/sukhanov_quiz_bot```
* ВКонтакте ```https://vk.com/club217816463```
