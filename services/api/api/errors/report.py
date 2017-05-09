from flask import Blueprint, jsonify, current_app
from lib.utils import json_response
from datetime import datetime
import json

from webargs import fields
from webargs.flaskparser import use_kwargs

error_reports_app = Blueprint('error_reports_app', __name__)


@error_reports_app.errorhandler(422)
def handle_bad_request(err):
    data = getattr(err, 'data')
    if data:
        messages = data['exc'].messages
    else:
        messages = ['Invalid Request']
    return jsonify({
        'messages': messages
    }), 422


@error_reports_app.route('/error-report/?', methods=['POST'])
@use_kwargs({
    'user_id': fields.Int(required=True),
    'username': fields.String(required=True),
    'comments': fields.String(missing=None),
    'actions': fields.List(fields.Dict(), required=True),
    'error': fields.String(required=True),
    'timestamp': fields.DateTime(missing=datetime.utcnow())
}, locations=('json',))
def report_error(user_id, username, comments, actions, error, timestamp):
    body = {
        'user_id': user_id,
        'username': username,
        'comments': comments,
        'actions': actions,
        'error': error,
        'timestamp': timestamp.strftime(current_app.config.get('TIMESTAMP_FORMAT'))
    }

    # Send the error report to a queue for another service to manage
    current_app.queue_service.send(current_app.config.get('REDUX_AMQP_EXCHANGE'), current_app.config.get('UI_AMQP_QUEUE'), json.dumps(body))

    return json_response({'success': True})
