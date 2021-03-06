import uuid
import marshmallow as ma


class RegistrationSchema(ma.Schema):
    username = ma.fields.String(required=True)
    password = ma.fields.String(required=True)
    token = ma.fields.Str(dump_only=True)

    @ma.pre_load
    def process_input(self, data, **kwargs):
        data['username'] = data['username'].lower().strip()
        return data

    @ma.post_load
    def make_object(self, data, **kwargs):
        data['token'] = str(uuid.uuid4())
        return data


class AuthSchema(ma.Schema):
    password = ma.fields.Str(required=True)
    username = ma.fields.String(required=True)
