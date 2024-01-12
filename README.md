# Foodgram - инстаграм для рецептов
### Создавайте свои рецепты и сохраняйте рецепты других пользователей
--
### Адрес сайта:

https://foodanton.bounceme.net/

### IP сервера:

84.201.164.17

### Функционал сайта:
- создание собственных рецептов;
- поиск и фильтрация рецептов других пользователей;
- добавление рецептов в "избранное";
- добавление рецептов в список покупок и выгрузка в текстовый файл;
- возможность подписки на других пользователей

### Технологии:
- Django
- Docker
- Python

### Запуск проекта:
1. Клонируйте проект:

git clone https://github.com/antonidasrus/foodgram-project-react.git

2. Подготовьте сервер:

scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/

3. Установите docker и docker-compose:

sudo apt install docker.io 
sudo apt install docker-compose

4. Соберите контейнер и выполните миграции:

sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate

5. Создайте суперюзера и соберите статику:

sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input

7. Данные для проверки работы приложения и входа в админ-зону:
Суперпользователь:

username: konovali@mail.ru
password: F07d05d1992D

