from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine
import jwt
from datetime import datetime, timedelta
from functools import wraps
from random import randrange
from flask_restx import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


database_name = 'API'
DB_URL = "________ReuiresMOGODB________"
app.config['MONGODB_HOST'] = DB_URL
app.config['SECRET_KEY'] = 'thisisthesecretkey'

db = MongoEngine()
db.init_app(app)


"""
{
    "pan": "ANRPM2537K",
    "name": "Dinesh Kumar",
    "dob": "1990-10-25",
    "father_name": "Hari Kumar",
    "client_id": "4feb601e-2316-4dda-8d91-28c89cdb2335"
}
"""


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


class BackendError(Exception):
    def __init__(self, message="There is a Error From our Side please try again"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
        # return make_response('Not found', 500)


class PAN_card(db.Document):

    pan = db.StringField()
    name = db.StringField()
    dob = db.StringField()
    father_name = db.StringField()
    client_id = db.StringField()

    def to_json(self):

        return {
            "pan": self.pan,
            "name": self.name,
            "dob": self.dob,
            "father_name": self.father_name,
            "client_id": self.client_id
        }


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'secret':
        token = jwt.encode({'user': auth.username, 'exp': datetime.now(
        ) + timedelta(seconds=15)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/api/pan/pan_no=<pan_no>', methods=['GET'])
@limiter.limit("10 per day")
@token_required
def get_client_id(pan_no):
    num = randrange(10)
    if num in (8, 9):
        raise BackendError()

    if request.method == 'GET':
        # pan_card_obj = PAN_card.objects(pan=pan_no)  # .first()

        pan_card_obj = PAN_card.objects.get(pan=pan_no)

        if pan_card_obj:
            output = {'client_id': pan_card_obj.client_id}
            # return make_response(jsonify(pan_card_obj.json['client_id']), 200)
            return make_response(output, 200)
        else:
            return make_response('Not found', 404)


@ app.route('/api/pan/client_id=<client_id>', methods=['GET'])
def get_pan_data(client_id):
    num = randrange(10)
    if num in (8, 9):
        raise BackendError()

    if request.method == 'GET':
        pan_card_obj = PAN_card.objects(client_id=client_id)  # .first()

        if pan_card_obj:
            return make_response(jsonify(pan_card_obj), 200)
        else:
            return make_response('Client_id Does not Exist', 404)


if __name__ == '__main__':
    app.run(debug=True)
