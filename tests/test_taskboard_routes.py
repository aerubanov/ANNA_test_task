import json
import pytest
import datetime

from src.taskboard.app import app, routes
from src.data.model import Task, TaskChange, User


@pytest.fixture()
def test_client():
    app.config['DEBUG'] = True
    app.config['DATABASE'] = 'sqlite:///test_db.db'
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


def test_post_task(test_client, database_session, requests_mock):
    user_data = '{"id": 1, "username": "user1"}'

    requests_mock.get('http://auth:8000/about_me', text=user_data)

    resp = test_client.post('/task',
                            json={
                                'name': 'task1',
                                'description': 'some description',
                                'status': 'Новая',
                                'end_date': str(datetime.datetime(2020, 10, 3)),
                            },
                            content_type='application/json')
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert 'task_id' in data

    # post without end_date
    resp = test_client.post('/task',
                            json={
                                'name': 'task1',
                                'description': 'some description',
                                'status': 'Новая',
                            },
                            content_type='application/json')
    assert resp.status_code == 201

    # invalid status
    resp = test_client.post('/task',
                            json={
                                'name': 'task1',
                                'description': 'some description',
                                'status': 'Invalid',
                            },
                            content_type='application/json')
    assert resp.status_code == 400

    # missing name
    resp = test_client.post('/task',
                            json={
                                'description': 'some description',
                                'status': 'Новая',
                            },
                            content_type='application/json')
    assert resp.status_code == 400


def test_get_tasks(test_client, database_session, requests_mock):
    user_data = '{"id": 1, "username": "user1"}'

    requests_mock.get('http://auth:8000/about_me', text=user_data)

    task1 = Task(name='task1', description='description1', status='Новая', created=datetime.datetime(2020, 10, 2),
                 user_id=1, end_date=datetime.datetime(2020, 10, 5))
    task2 = Task(name='task2', description='description2', status='Завершённая', created=datetime.datetime(2020, 9, 20),
                 user_id=1)
    task3 = Task(name='task3', description='description3', status='Новая', created=datetime.datetime(2020, 10, 2),
                 user_id=3)
    database_session.add_all([task1, task2, task3])
    database_session.commit()

    # without filters
    resp = test_client.get('/tasks', json={})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    names = [item['name'] for item in data]
    assert 'task1' in names
    assert 'task2' in names
    assert 'task3' not in names

    # filter by status
    resp = test_client.get('/tasks',
                           json={
                               'filter_by_status': 'Новая',
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    names = [item['name'] for item in data]
    assert 'task1' in names
    assert len(data) == 1

    # filter by end_date
    resp = test_client.get('/tasks',
                           json={
                               'filter_by_end_date': str(datetime.datetime(2020, 10, 5)),
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    names = [item['name'] for item in data]
    assert 'task1' in names
    assert len(data) == 1

    # filter by both
    resp = test_client.get('/tasks',
                           json={
                               'filter_by_end_date': str(datetime.datetime(2020, 10, 5)),
                               'filter_by_status': 'Новая',
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    names = [item['name'] for item in data]
    assert 'task1' in names
    assert len(data) == 1


def test_put_task(test_client, database_session, requests_mock):
    user_data = '{"id": 1, "username": "user1"}'

    requests_mock.get('http://auth:8000/about_me', text=user_data)

    task = Task(task_id=1, name='task1', description='description1', status='Новая',
                created=datetime.datetime(2020, 10, 2),
                user_id=1, end_date=datetime.datetime(2020, 10, 5))
    database_session.add(task)
    database_session.commit()

    # change task name
    resp = test_client.put('/task',
                           json={
                               'task_id': 1,
                               'new_name': 'task2'
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    changes = database_session.query(TaskChange).all()
    assert len(changes) == 1
    assert changes[0].field_changed == 'name'
    assert changes[0].new_value == 'task2'

    # change description and end_date
    resp = test_client.put('/task',
                           json={
                               'task_id': 1,
                               'new_description': 'description2',
                               'new_end_date': str(datetime.datetime(2020, 10, 6))
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    changes = database_session.query(TaskChange).all()
    assert len(changes) == 3
    change2 = database_session.query(TaskChange).filter(TaskChange.field_changed == 'description').first()
    assert change2.new_value == 'description2'
    change2 = database_session.query(TaskChange).filter(TaskChange.field_changed == 'end_date').first()
    assert change2.new_value == '2020-10-06 00:00:00'


def test_get_changes(test_client, database_session, requests_mock):
    user_data = '{"id": 1, "username": "user1"}'
    token = '123TOKEN123'
    user = User(id=1, username='user1', auth_token=token)
    user.set_password_hash('qwerty')

    requests_mock.get('http://auth:8000/about_me', text=user_data)
    task1 = Task(task_id=1, name='task1', description='description1', status='Новая',
                 created=datetime.datetime(2020, 10, 2),
                 user_id=1, end_date=datetime.datetime(2020, 10, 5))
    task2 = Task(task_id=2, name='task2', description='description2', status='Новая',
                 created=datetime.datetime(2020, 10, 2),
                 user_id=3)
    change_1 = TaskChange(field_changed='description', new_value='description1', task_id=1)
    change_2 = TaskChange(field_changed='description', new_value='description2', task_id=2)
    database_session.add_all([user, task1, task2, change_1, change_2])
    database_session.commit()

    # get changes
    resp = test_client.get('/task_changes',
                           json={
                               'task_id': 1,
                           },
                           content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['new_value'] == 'description1'

    # missing task_id
    resp = test_client.get('/task_changes',
                           json={},
                           content_type='application/json')
    assert resp.status_code == 400

    # other user
    resp = test_client.get('/task_changes',
                           json={
                               'task_id': 2,
                           },
                           content_type='application/json')
    assert resp.status_code == 403

    # task not exist
    resp = test_client.get('/task_changes',
                           json={
                               'task_id': 3,
                           },
                           content_type='application/json')
    assert resp.status_code == 404
