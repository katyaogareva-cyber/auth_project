# Backend Authentication & Authorization System

## Описание проекта

Данный проект представляет собой backend-приложение, реализующее собственную систему аутентификации и авторизации пользователей.

Основная цель проекта:
- аутентификации пользователей
- JWT-токенов
- авторизации (RBAC)
- контроля доступа к ресурсам
- ownership-based доступа

---
## Как запустить проект

1. Создать виртуальное окружение:
   python -m venv venv

2. Активировать окружение:
   source venv/bin/activate

3. Установить зависимости:
   pip install django djangorestframework bcrypt pyjwt

4. Запустить сервер:
   python manage.py runserver
   
---

## Технологии

- Python
- Django REST Framework
- bcrypt (хеширование паролей)
- JWT (аутентификация)
- Postman(для проверки работы системы)
- mock data

---

## Роли пользователей

**Administrator**
Администратор имеет полный доступ к системе:
- управление пользователями
- управление заказами (все записи)
- управление правилами доступа
- изменение паролей любых пользователей
- просмотр всех данных системы

**User**
Обычный пользователь:
- доступ только к своим данным
- создание заказов только для себя
- редактирование и удаление только своих заказов
- просмотр только своего профиля
- изменение только своего пароля

---

## Аутентификация

- Регистрация пользователя по email и паролю
- Пароли хранятся в хешированном виде (bcrypt)
- Login возвращает JWT токен
- Logout реализован через blacklist токенов
- Middleware автоматически определяет пользователя по токену

---

## Авторизация

Система основана на двух принципах:

**1. Role-Based Access Control (RBAC)**
Права зависят от роли пользователя (admin/user)

**2. Ownership-based access**
Пользователь может работать только со своими объектами (orders)

---

## Бизнес-сущности

**Users**
- регистрация
- просмотр
- обновление
- мягкое удаление (is_active=False)

**Orders**
- создание
- просмотр
- редактирование
- удаление

**Rules (Access Control)** (только admin) 
- создание
- просмотр
- редактирование
- удаление

---

## Правила доступа

Система использует таблицу правил:

- role
- element
- action
- value
- scope (all / own)

---

## Data model (mock)

**USERS:**
- id
- email
- first_name
- last_name
- password
- role
- is_active

**ORDERS:**
- id
- owner_id
- title

**ACCESS_RULES:**
- role
- element
- action
- value
- scope
---

## API endpoints 

**Auth**
- POST /register/
- POST /login/
- POST /logout/
- GET /me/

**Users**
- GET /users/
- POST /users/
- GET /users/{id}/
- PATCH /users/{id}/
- DELETE /users/{id}/

**Orders**
- GET /orders/
- POST /orders/
- GET /orders/{id}/
- PATCH /orders/{id}/
- DELETE /orders/{id}/

**Rules (admin only)**
- GET /rules/
- POST /rules/
- GET /rules/{id}/
- PATCH /rules/{id}/
- DELETE /rules/{id}/

## Postman

Файл коллекции:
auth_project.postman_collection.json

Используется для тестирования всех API endpoints
