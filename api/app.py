import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
CORS(app)

load_dotenv()  # Load the environment variables from the .env file

# Initialize JWTManager
app.config['JWT_SECRET_KEY'] = os.environ['SECRET_KEY']  # Replace with your own secret key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['MONGO_URI'] = os.environ['MONGO_URI']
app.config['UPLOAD_FOLDER'] = os.path.join('staticFiles', 'uploads')

mongodb_client = PyMongo(app)
db = mongodb_client.db

"""
    AUTH ROUTES
"""

jwt = JWTManager(app)

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']

@app.route('/google_login', methods=['POST'])
def login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,  # client ID from the credential at google developer console
        'client_secret': GOOGLE_SECRET_KEY,  # client secret from the credential at google developer console
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    """
        check here if user exists in database, if not, add him
    """

    jwt_token = create_access_token(identity=user_info['email'])  # create jwt token
    response = jsonify(user=user_info)
    response.set_cookie('access_token_cookie', value=jwt_token, secure=True)

    return response, 200

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie') # Demonstration how to get the cookie
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


"""
    APP ROUTES
"""

def get_route_handler(route):
    def route_handler(id):
        if request.method == 'GET':
            if id == 'list':
                return dumps(db[route].find({})), 200
            
            return dumps(db[route].find({'id': id})), 200
        
        if request.method == 'POST':
            # this is a silly way of doing security and probably isn't viable
            if os.environ['APP_MODE'] != 'dev':
                return {'message': 'uploads not allowed in production'}, 403
            
            # process the upload
            f = request.files.get('payload')
            data_filename = secure_filename(f.filename)
            data_filepath = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
            f.save(data_filepath)

            # read the file and convert to documents
            df = pd.read_csv(data_filepath, encoding='unicode_escape')
            records = df.to_dict('records')

            # put the documents into the db
            for r in records:
                db[route].insert_one(r)
                
            # delete the file from storage
            if os.path.exists(data_filepath):
                os.remove(data_filepath)

            return {
                'data': dumps(records),
            }, 201
    
    route_handler.__name__ += route
    return route_handler

ROUTES = [
    'ancestries',
    'backgrounds',
    'classes',
    'feats',
    'spells',
    'subclasses'
]

for route in ROUTES:
    app.add_url_rule('/api/'+route+'/<id>', view_func=get_route_handler(route), methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
