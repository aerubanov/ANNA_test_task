from flask import request, g, abort, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import json
from marshmallow import ValidationError

from src.taskboard.app import app
from src.taskboard.app.validation import TaskSchema
from src.data.model import Base, Task, TaskChange


def create_db():
    engine = create_engine(app.config['DATABASE'])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_db():
    if 'db' not in g:
        session = create_db()
        g.db = session

    return g.db


@app.route('/create_task', methods=['POST'])
def create_task():
    resp = requests.get('http://auth:8000/about_me', headers=request.headers)
    if resp.status_code != 200:
        abort(403)
    user_data = json.loads(resp.text)
    user_id = user_data['id']
    try:
        data = TaskSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return
    task_name = data['name']
    task_description = data['description']
    task_created = data['created']
    task_status = data['status']
    task_end_date = data['end_date']
    task = Task(name=task_name, description=task_description, status=task_status, created=task_created,
                end_date=task_end_date, user_id=user_id)
    session = get_db()
    session.add(task)
    session.commit()
    return 201


@app.route('/user_tasks', methods=['GET'])
def get_user_tasks():
    resp = requests.get('http://auth:8000/about_me', headers=request.headers)
    if resp.status_code != 200:
        abort(403)
    user_data = json.loads(resp.text)
    user_id = user_data['id']
