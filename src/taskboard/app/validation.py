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
