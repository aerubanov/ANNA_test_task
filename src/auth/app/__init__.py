from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = 'postgresql://postgres:postgres@PostgreSQL/pgdb'
app.config["SECRET_KEY"] = "123SECRET_KEY123"