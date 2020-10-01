from sqlalchemy import Column, DateTime, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    token = Column(String, unique=True)
    password_hash = Column(String)

    def __repr__(self):
        return f'user: {self.username} token: {self.user_id}'

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    status = Column(String)
    created = Column(DateTime)
    end_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('User', back_populates='tasks')

    @property
    def serialize(self):
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created': self.created,
            'end_date': self.end_date,
            'user_id': self.user_id,
        }


class TaskChange(Base):
    __tablename__ = 'task_changes'

    id = Column(Integer, primary_key=True)
    field_changed = Column(String)
    new_value = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    task = relationship('Task', back_populates='task_changes')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'field_chenged': self.field_changed,
            'new_value': self.new_value,
            'task_id': self.task_id,
        }
