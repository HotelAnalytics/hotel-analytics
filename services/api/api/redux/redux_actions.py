from datetime import datetime
from flask import Blueprint, jsonify, current_app
from lib.utils import json_response
from webargs import fields
from webargs.flaskparser import use_kwargs

redux_actions_app = Blueprint('redux_actions_app', __name__)


@redux_actions_app.errorhandler(422)
def handle_bad_request(err):
    data = getattr(err, 'data')
    if data:
        messages = data['exc'].messages
    else:
        messages = ['Invalid Request']
    return jsonify({
        'messages': messages
    }), 422


# Return an InsertOneResult if successfully inserted or None otherwise
def insert_mongo(action, user_uid, timestamp, session_start):

    # Connect to server
    client = current_app.mongo

    # Get database and collection
    try:
        db = client['redux_actions']
        col = db.dashboard
    except:
        print('Could not get database or collection')

    # Now insert a document into our collection
    try:
        return col.insert(
            {
                "action": action,
                "user_uid": user_uid or '',
                "timestamp": timestamp,
                "session_start": session_start or '',
            },
            # Avoid key error when inserting routing action with key $searchBase
            check_keys=False
        )
    except:
        print('Could not insert into collection: ' + str(action['type']))

    return None


@redux_actions_app.route('/redux-actions/', methods=['POST'])
@use_kwargs({
    'user_uid': fields.Int(missing=None),
    'action': fields.Dict(required=True),
    'timestamp': fields.DateTime(missing=datetime.utcnow()),
    'session_start': fields.DateTime(missing=None),
}, locations=('json',))
def redux_actions(user_uid, action, timestamp, session_start):

    result = insert_mongo(action, user_uid, timestamp, session_start)

    if result:
        return json_response({
            'success': 'true',
        })

    return json_response({
        'success': 'false'
    })

if __name__ == '__main__':
    # For testing purpose only, executed when the file is ran directly
    print(insert_mongo({
        'content': 'empty'
    }, 'random'))
