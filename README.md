# FOODGRAM (продуктовый помощник)

## **Описание проекта**
Cайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Как запустить проект локально на Windows:

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Cоздайте файл .env в директории /infra/ с содержанием:

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DB_NAME
DB_HOST
DB_PORT
SECRET_KEY           
ALLOWED_HOSTS
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Загрузите тестовые данные в БД:

```
python manage.py load_data
```

Запустить проект:

```
python manage.py runserver
```

## Запустить проект на удаленном сервере:

После проверке выложу на сервер проект.

### Автор проекта:

- [@KrasinAD](https://github.com/KrasinAD)