# Проект Foodgram
[![Main Foodgram workflow](https://github.com/deltabobkov/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/deltabobkov/foodgram-project-react/actions/workflows/main.yml)

![Python](https://img.shields.io/badge/Python-313131?style=flat&logo=Python&logoColor=white&labelColor=306998)
![Django](https://img.shields.io/badge/Django-313131?style=flat&logo=django&labelColor=092e20)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-313131?style=flat&logo=PostgreSQL&logoColor=ffffff&labelColor=336791)
![NGINX](https://img.shields.io/badge/NGINX-313131?style=flat&logo=nginx&labelColor=009639)
![React](https://img.shields.io/badge/React-313131?style=flat&logo=React&logoColor=ffffff&labelColor=61DBFB)
![Docker](https://img.shields.io/badge/Docker-313131?style=flat&logo=docker&logoColor=ffffff&labelColor=1D63ED)
![Github Actions](https://img.shields.io/badge/Github%20Actions-313131?style=flat&logo=Github-Actions&logoColor=ffffff&labelColor=4a7ebf)
![Visual Studio](https://img.shields.io/badge/VS%20Code-313131?style=flat&logo=visualstudiocode&logoColor=ffffff&labelColor=0098FF)

## Проект создан для публикации рецептов блюд с возможностью подписи на авторов рецептов и добавлением рецептов в избранное.

### Локальный запуск c Docker:
1. Клонировать данный репозиторий: 
```bash
git clone https://github.com/deltabobkov/foodgram-project-react
```
2. Создать .env файл в корневой папке проекта, в котором должны содержаться следующие переменные:
```bash
POSTGRES_USER=  #пользователь БД
POSTGRES_PASSWORD= #пароль БД
DB_NAME=foodgram  #название БД
DB_HOST=db
DB_PORT=5432

SECRET_KEY='' #ключ джанго
DEBUG='' #True или False
HOSTS='' #список хостов 
CSRF = '' #полный url сайта при деплое на уделённом сервере
```

**Для выполнения следующего шага должен быть установлен [docker](https://docs.docker.com/get-docker/)**  

3. В директории infra выполнить команду для создания и запуска контейнеров:
```bash
cd infra
docker compose up -d --build
```
  
4. Выполнить миграции, создать суперпользователя и собрать статику в контейнере backend:
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --no-input 
```

5. Загрузить в базу данных ингридиетны из с помощью команды:
```bash
docker compose exec backend python manage.py add_ingredients
```

**Проект будет досупен по адресу:**  
http://127.0.0.1/  
**Документация к API:**  
http://localhost/api/docs/redoc.html
