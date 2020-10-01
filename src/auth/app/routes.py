from flask import request, g, abort, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow import ValidationError
import base64

from src.auth.app import app
from src.auth.app.validation import RegistrationSchema, AuthSchema
from src.data.model import Base, User

login_manager = LoginManager()
login_manager.init_app(app)


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


@login_manager.user_loader
def load_user(user_id):
    session = get_db()
    return session.query(User).get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        session = get_db()
        user = session.query(User).filter(User.token == api_key).first()
        if user:
            return user

    return None


@app.route('/registration', methods=['POST'])
def registration():
    try:
        data = RegistrationSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return

    session = get_db()
    if session.query(User).filter(User.username == data['username']).first():
        abort(400, 'User exist')
    user = User(username=data['username'], token=data['token'])
    user.set_password(data['password'])

    session.add(user)
    session.commit()

    response = {'token': data['token']}
    return jsonify(response)


@app.route('/login')
def login():
    try:
        data = AuthSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db()
    user = session.query(User).filter(User.username == data['username']).first()
    if not user or not user.check_password(data['password']):
        abort(401)
    login_user(user)
    response = {'token': user.token}
    return jsonify(response)


@app.route('/check')
@login_required
def check():
    return 'OK'


@app.route('/about_me')
@login_required
def about_me():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'token': current_user.token,
    })


@app.teardown_appcontext
def teardown_db(args):
    db = g.pop('db', None)

    if db is not None:
        db.close()
