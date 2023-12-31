# Проект CookeryBook 
**CookeryBook - сайт для публикации и обмена рецептами**  
Проект состоит из бэкенд-приложения на Django, фронтенд-приложения на React и API.

### Для неавторизованных пользователей:
  1. Доступна главная страница.
  2. Доступна страница отдельного рецепта.
  3. Доступна страница любого пользователя.
  4. Доступна и работает форма авторизации.
  5. Доступна и работает система восстановления пароля.
  6. Доступна и работает форма регистрации.

### Для авторизованных пользователей:
  1. Доступна главная страница.
  2. Доступна страница другого пользователя.
  3. Доступна страница отдельного рецепта.
  4. Доступна страница «Мои подписки»:
      a. можно подписаться и отписаться на странице рецепта;
      b. можно подписаться и отписаться на странице автора;
      c. при подписке рецепты автора добавляются на страницу «Мои подписки» и удаляются оттуда при отказе от подписки.
  5. Доступна страница «Избранное»:
      a. на странице рецепта есть возможность добавить рецепт в список избранного и удалить его оттуда;
      b. на любой странице со списком рецептов есть возможность добавить рецепт в список избранного и удалить его оттуда.
  6. Доступна страница «Список покупок»:
      a. на странице рецепта есть возможность добавить рецепт в список покупок и удалить его оттуда;
      b. на любой странице со списком рецептов есть возможность добавить рецепт в список покупок и удалить его оттуда;
      c. есть возможность выгрузить файл с перечнем и количеством необходимых ингредиентов для рецептов из «Списка покупок»;
      d. ингредиенты в выгружаемом списке не повторяются, корректно подсчитывается общее количество для каждого ингредиента.
  7. Доступна страница «Создать рецепт»:
      a. есть возможность опубликовать свой рецепт;
      b. есть возможность отредактировать и сохранить изменения в своём рецепте;
      c. есть возможность удалить свой рецепт.
  8. Доступна возможность выйти из системы.

## Стек технологий:
- Python 3
- Django 3.2
- DRF
- Docker
- Docker Compose
- NGINX
- Gunicorn
- PostgreSQL

## Как запустить проект в dev-режиме:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Elllym-em/cookery_book_project.git
```
```
cd cookery_book_project
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
* Если у вас Linux/macOS
    ```
    source env/bin/activate
    ```
* Если у вас windows
    ```
    source env/scripts/activate
    ```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить команду импорта данных в БД:
```
python3 manage.py import_data
```
Запустить проект:
```
python3 manage.py runserver
```

## Примеры запросов API:
### Запрос на регистрацию пользователя (POST):
```
/api/users/
```
**Пример запроса:**
```
{
  "email": "string",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "password": "string"
}
```
**Пример ответа:**
```
{
  "email": "string",
  "id": 0,
  "username": "string",
  "first_name": "string",
  "last_name": "string"
}
```

### Запрос на получение списка рецептов (GET):
```
/api/recipes/
```
**Пример ответа:**
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "string",
        "id": 0,
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

### Запрос на создание рецепта (POST):
```
/api/recipes/
```
**Пример запроса:**
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
**Пример ответа:**
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "string",
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

### Запрос на добавление рецепта в список покупок (POST):
```
/api/recipes/{id}/shopping_cart/
```
**Пример ответа:**
```
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```

### Запрос на просмотр своих подписок (GET):
```
/api/users/subscriptions/
```
**Пример ответа:**
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "string",
      "id": 0,
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0
    }
  ]
}
```

### Запрос на подписку на пользователя (POST):
```
/api/users/{id}/subscribe/
```
**Пример ответа:**
```
{
  "email": "string",
  "id": 0,
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```

## Как развернуть проект локально:
1. Установить на локальную машину 'Docker' и 'Docker Compose';
2. Создать в корневой директории файл '.env' (пример создания в файле .env.example в корневой директории);
3. Выполнить команду для запуска контейнеров
```
docker-compose up -d --build
```
4. Выполнить миграции
```
docker-compose exec backend python manage.py migrate
```
5. Запустить команду импорта данных в БД:
```
docker-compose exec backend python manage.py import_data
```
6. Собрать статику
```
docker-compose exec backend python manage.py collectstatic
```
7. Скопировать статику 
```
docker-compose exec backend cp -r /app/collected_static/. /static/static/
```
8. Создать суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
9. Перейти в браузере по ссылке http://localhost:8080/
10. Полная документация API будет доступна по ссылке http://localhost:8080/api/docs/

**Автор (backend, docker-контейнеры, deploy):**
[Элина Мустафаева](https://github.com/Elllym-em)
