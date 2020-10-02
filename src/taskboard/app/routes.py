from flask import request, g, abort, jsonify, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import json
from marshmallow import ValidationError

from src.taskboard.app import app
from src.taskboard.app.validation import TaskSchema, GetTasksSchema, ChangeTaskSchema, TaskChangesSchema
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


@app.route('/task', methods=['POST'])
def post_task():
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
    session.flush()
    session.commit()
    return app.response_class(
        response=json.dumps({'task_id': task.task_id}),
        status=201,
        mimetype='application/json')


@app.route('/tasks', methods=['GET'])
def get_tasks():
    resp = requests.get('http://auth:8000/about_me', headers=request.headers)
    if resp.status_code != 200:
        abort(403)
    user_data = json.loads(resp.text)
    user_id = user_data['id']

    try:
        args = GetTasksSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return

    session = get_db()
    result = session.query(Task).filter(Task.user_id == user_id)
    if args['filter_by_status'] is not None:
        result = result.filter(Task.status == args['filter_by_status'])
    if args['filter_by_end_date'] is not None:
        result = result.filter(Task.end_date == args['filter_by_end_date'])
    result = [i.serialize for i in result.all()]
    return jsonify(result)


@app.route('/task', methods=['PUT'])
def put_task():
    resp = requests.get('http://auth:8000/about_me', headers=request.headers)
    if resp.status_code != 200:
        abort(403)
    user_data = json.loads(resp.text)
    user_id = user_data['id']

    try:
        args = ChangeTaskSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return

    session = get_db()
    obj = session.query(Task).get(args['task_id'])

    if obj is None:
        abort(404, 'Task not exist')
    if obj.user_id != user_id:
        abort(403)

    changes = []
    if args['new_name'] is not None:
        obj.name = args['new_name']
        changes.append(TaskChange(field_changed='name', new_value=args['new_name'], task_id=obj.task_id))
    if args['new_description'] is not None:
        obj.description = args['new_description']
        changes.append(TaskChange(field_changed='description', new_value=args['new_description'], task_id=obj.task_id))
    if args['new_end_date'] is not None:
        obj.end_date = args['new_end_date']
        changes.append(TaskChange(field_changed='end_date', new_value=args['new_end_date'], task_id=obj.task_id))
    session.commit()
    session.add_all(changes)
    session.commit()
    return 'OK'


@app.route('/task_changes')
def get_changes():
    resp = requests.get('http://auth:8000/about_me', headers=request.headers)
    if resp.status_code != 200:
        abort(403)
    user_data = json.loads(resp.text)
    user_id = user_data['id']

    try:
        args = TaskChangesSchema().load(request.json)
        task_id = args['task_id']
    except ValidationError as e:
        abort(400, str(e))
        return

    session = get_db()
    task = session.query(Task).get(task_id)
    if task is None:
        abort(404)
    if task.user_id != user_id:
        abort(403)
    result = session.query(TaskChange).filter(TaskChange.task_id == task_id).all()
    result = [i.serialize for i in result]
    return jsonify(result)


@app.teardown_appcontext
def teardown_db(args):
    db = g.pop('db', None)

    if db is not None:
        db.close()
