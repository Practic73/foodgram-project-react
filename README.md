# Продуктовый помощник Foodgram

### Описание
«Фудграм» — сайт, на котором пользователи имеют возможность публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также  доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Стек технологий:
- Python
- Django
- Django Rest Framework
- PosgreSQL
- Docker

# Порядок запуска
## Запуск проекта локально
Клонировать репозиторий и перейти в него:
```
git clone https://github.com/Practic73/foodgram-project-react.git
```

Создать и активировать виртуальное окружение, обновить pip и установить зависимости:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

## Для запуска локально:
```
cd backend
python manage.py runserver
```

Создать базу данных:
```
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Загрузить ингредиенты в базу данных:
```
python manage.py import_data
```

Заупстить сервер:
```
python manage.py runserver
```

# CI/CD workflow
Для запуска CI/CD в репозитории GitHub Actions Settings/Secrets/Actions прописать Secrets:
```
- DOCKER_PASSWORD
- DOCKER_USERNAME
- HOST
- POSTGRES_DB
- POSTGRES_PASSWORD
- POSTGRES_USER
- SECRET_KEY
- ALLOWED_HOSTS
- SSH_KEY
- SSH_PASSPHRASE
- TELEGRAM_TO
- TELEGRAM_TOKEN
- USER
```
Для запуска автодеплоя нужно сделать пуш в репозиторий.



## Проект доступен
- Проект запущен и доступен по https://9foodgram9.sytes.net/
- Админ панель https://9foodgram9.sytes.net/admin/
- Админ логин: admin
- Админ пароль: 123