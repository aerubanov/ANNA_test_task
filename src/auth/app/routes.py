from flask import request, g, abort, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow import ValidationError

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


@app.route('/registration', methods=['POST'])
def registration():
    try:
        schema = RegistrationSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        abort(400, str(e))
        return

    session = get_db()
    if session.query(User).filter(User.username == data['username']).first():
        abort(400, 'User exist')
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['token'])

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
    if not user or not user.check_password(data['token']):
        abort(401)
    login_user(user, remember=True)
    return '', 204


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return '', 204


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
    })


@app.teardown_appcontext
def teardown_db(args):
    db = g.pop('db', None)

    if db is not None:
        db.close()
