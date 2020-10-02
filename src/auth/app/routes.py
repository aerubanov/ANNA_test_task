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


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        session = get_db()
        user = session.query(User).filter(User.auth_token == api_key).first()
        if user:
            return user

    return None


@app.route('/registration', methods=['POST'])
def registration():
    try:
        data = RegistrationSchema().load(request.json)
    except (ValidationError, KeyError) as e:
        abort(400, str(e))
        return
    session = get_db()
    if session.query(User).filter(User.username == data['username']).first():
        abort(400, 'User exist')
    user = User(username=data['username'], auth_token=data['token'])
    user.set_password_hash(data['password'])

    session.add(user)
    session.commit()

    return jsonify(token=data['token'])


@app.route('/login', methods=['POST'])
def login():
    try:
        data = AuthSchema().load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return
    session = get_db()
    user = session.query(User).filter(User.username == data['username']).first()
    if not user or not user.check_password_hash(data['password']):
        abort(401)
    login_user(user, remember=False)
    return jsonify(token=user.auth_token)


@app.route('/about_me')
@login_required
def about_me():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
    })


@app.teardown_appcontext
def teardown_db(args):
    db = g.pop('db', None)

    if db is not None:
        db.close()
