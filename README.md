# ANNA_test_task
[![Build Status](https://travis-ci.org/aerubanov/ANNA_test_task.svg?branch=master)](https://travis-ci.org/aerubanov/ANNA_test_task)
[![codecov](https://codecov.io/gh/aerubanov/ANNA_test_task/branch/master/graph/badge.svg)](https://codecov.io/gh/aerubanov/ANNA_test_task)

Приложение представляет собой task manager. Доступен Docker-образ приложения, который может загружен
 с dockerhub-а. Сборка образа осуществляется с помощью github-actions при каждом релизе.
  Для приложения выполните
```bash
$ docker-compose pull
$ docker-compose up
```
Взаимодействие с приложением осуществляется через http-API, функционал
которого описан в таблице. В скобках указаны опциональные параметры
|  url  |  метод  |  json-параметры  |  действие  | возвращает |
| ----- | -------- | ---------------- | -----------| ----- |
| /registration | POST | username, password | добавление нового пользователя | --- |
| /login | POST |username, password | авторизация пользователя в системе | token - токен доступа |
| /about_me | GET | | --- | получение информации о текущем пользователе | id - идентификатор пользователя, username - имя пользователя |
| /task| POST | name, description, status, <end_date> | добовление задачи для текущего пользователя с названием| task_id - идентификатор задачи |
| /tasks | GET | <filter_by_status>, <filter_by_end_date> | получение задач пользователя с возможностью фильтрации по статусу и времени завершения| created - дата создания, description - описание, end_date - дата завершения, name - название, status - статус, task_id - идентификатор задачи, user_id - идентификатор пользователя|
|/task| PUT | task_id, <new_name>, <new_description>, <new_status>, <new_end_date| измение существующей задачи| --- |
|/task_changes| GET | task_id | просмотр изменений задачи | field_changed - что изменено, id - идентификатор измения, new_value - новое значение, task_id - идентификатор задачи |

# Описание работы
Для храния данных используется PostrgeSQL, взаимодействие с БД осуществляется с помощью sqlalchemy. В базе данных хранятся три таблицы - users, tasks, task_changes - для информации о пользователе, задачах и истории измений задач соответственно.

В качестве web-framework-a служит flask, валидация данных выполняется с marshmalow. Приложение состоит из двух сервисов - auth для авторизации и taskboard - API для работы с задачами. Веб сервром для запуска flask-приложений выступает gunicorn, для проксирования запросов используется nginx. Запуск сервисов осуществляется с помощью docker-compose.

При регистрации пользователя в системе в БД создается соответсвующая запись в таблице users с его именем, хэшем пароля, присвоенным токеном. При авторизации пользователя ему возвращается токен, который он при дальнейшей работе должен передавать в заголовке Authorization. По этому заголовку с помощью запроса к /about_me приложение может устоновить, от какого пользователя пришел тот или иной запрос. При добавлении задачи пользователем создается запись в таблице tasks, а при измении - в таблице task_changes. Если изменяется сразу несколько переменных задачи в одном запросе к API, то для каждой изменяемой переменной создается своя запись в task_changes.
