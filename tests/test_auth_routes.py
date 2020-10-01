import pytest
import json
import base64

from src.auth.app import app, routes
from src.data.model import User


@pytest.fixture()
def test_client():
    app.config['DEBUG'] = True
    app.config['DATABASE'] = 'sqlite:///test_db.db'
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


def test_registration(test_client, database_session):
    resp = test_client.post('/registration',
                            json={'username': 'user', 'password': 'qwerty'},
                            content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'token' in data
    assert len(data['token']) > 0


def test_registration_missed_param(test_client, database_session):
    resp = test_client.post('/registration',
                            json={'username': 'user'},
                            content_type='application/json')
    assert resp.status_code == 400

    resp = test_client.post('/registration',
                            json={'password': 'qwerty'},
                            content_type='application/json')
    assert resp.status_code == 400


def test_registration_exist_user(test_client, database_session):
    test_client.post('/registration',
                     json={'username': 'user', 'password': 'qwerty'},
                     content_type='application/json')
    resp = test_client.post('/registration',
                            json={'username': 'user', 'password': 'qwerty'},
                            content_type='application/json')
    assert resp.status_code == 400


def test_login(test_client, database_session):
    token = '123TOKEN123'
    token_encoded = base64.b64encode(b'123TOKEN123').decode('utf-8')
    user = User(username='user1', auth_token=token)
    user.set_password_hash('qwerty')
    database_session.add(user)
    database_session.commit()

    resp = test_client.post('/login',
                            json={'username': 'user1', 'password': '123'},
                            content_type='application/json')
    assert resp.status_code == 401

    resp = test_client.post('/login',
                            json={'username': 'use', 'password': 'qwerty'},
                            content_type='application/json')
    assert resp.status_code == 401

    resp = test_client.post('/login',
                            json={'username': 'user1'},
                            content_type='application/json')
    assert resp.status_code == 400

    resp = test_client.post('/login',
                            json={'username': 'user1', 'password': 'qwerty'},
                            content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'token' in data
    assert data['token'] == token

    other_token_encoded = base64.b64encode(b"123").decode('utf-8')
    resp = test_client.get('/about_me', headers={'Authorization': f'Basic {other_token_encoded}'})
    assert resp.status_code == 401

    resp = test_client.get('/about_me', headers={'Authorization': f'Basic {token_encoded}'})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'id' in data
    assert data['username'] == 'user1'

