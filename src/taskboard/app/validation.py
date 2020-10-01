import marshmallow as ma
import datetime


class TaskSchema(ma.Schema):
    name = ma.fields.String(required=True)
    description = ma.fields.String(required=True)
    created = ma.fields.DateTime(dump_only=True)
    status = ma.fields.String(required=True)
    end_date = ma.fields.DateTime(missing=None)

    PERMISSIBLE_STATUS = {'Новая', 'Запланированная', 'В работе', 'Завершённая'}

    @ma.validates('status')
    def validate_status(self, value):
        if value not in self.PERMISSIBLE_STATUS:
            raise ma.ValidationError('Incorrect value of status parameter')

    @ma.pre_load
    def get_date(self, data):
        data['created'] = datetime.datetime.utcnow()


class GetTasksSchema(ma.Schema):
    filter_by_status = ma.fields.String(missing=None)
    filter_by_end_date = ma.fields.DateTime(missing=None)

    PERMISIBLE_STATUS = {'Новая', 'Запланированная', 'В работе', 'Завершённая'}

    @ma.validates('filter_by_status')
    def validate_filter(self, value):
        if value is not None and value not in self.PERMISIBLE_STATUS:
            raise ma.ValidationError('Incorrect value of filter_by_status parameter')


class ChangeTaskSchema(ma.Schema):
    task_id = ma.fields.Integer(required=True)
    new_name = ma.fields.String(missing=None)
    new_description = ma.fields.String(missing=None)
    new_end_time = ma.fields.DateTime(missing=None)

    @ma.validates_schema
    def check_fields(self, data, **kwargs):
        if data['new_name'] is None and data['new_description'] is None and data['new_end_time'] is None:
            raise ma.ValidationError('No parameter specified')


class TaskChangesSchema(ma.Schema):
    task_id = ma.fields.Integer(required=True)
