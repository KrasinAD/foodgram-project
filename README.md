# FOODGRAM (продуктовый помощник)

## **Описание проекта**
Cайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Сайт проекта - https://foodgram.krasindomain.ru/

## Технологии
- Python 3.10
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL
- Djoser
- Yandex Cloud
- Nginx
- Qunicorn 20.1
- Docker
- CI/CD

## Как запустить проект локально:

1. Клонирование проекта с GitHub на локальный компьютер
```
git clone git@github.com/KrasinAD/foodgram-project
```
2. В директории проекта перейдите в директорию infra/.
3. Создайте файл .env в директории infra/ и заполните его. Переменные для работы проекта перечислены в файле .env.example, находящемся в директории infra/.
3. Запустите в терминале контейнеры Docker внутри папки infra:
```
docker compose up
``` 
4. Выполните миграции в другом терминале:
```
docker compose exec backend python manage.py migrate
```
5. Создайте администратора:
```
docker compose exec backend python manage.py createsuperuser
```
6. Соберите статику backend:
```
docker compose exec backend python manage.py collectstatic
```
7. Загрузите в базу данных ингредиенты и теги:
```
docker compose exec backend python manage.py load_data
```
8. Перейдите на сайт:
```
https://localhost:8888
```

## Запустить проект на удаленном сервере:

1. Установить на сервере Docker, Docker Compose:
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
2. Скопировать на сервер файлы docker-compose.production.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):
```
scp docker-compose.yml nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

3. Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение

DB_ENGINE               - django.db.backends.postgresql
DB_NAME                 - postgres
POSTGRES_USER           - postgres
POSTGRES_PASSWORD       - postgres
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```

4. Создать и запустить контейнеры Docker, выполнить команду на сервере:
```
sudo docker compose up -d
```
5. Выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```
6. Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic
```
7. Загрузите в базу данных ингредиенты и теги:
```
sudo docker compose exec backend python manage.py load_data 
```
8. Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```
9. Для остановки контейнеров Docker:
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```

### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Автор проекта:

- [@KrasinAD](https://github.com/KrasinAD)