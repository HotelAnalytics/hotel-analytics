import bcrypt
import hashlib
import base64

from flask import Blueprint, jsonify, current_app
from datetime import date, datetime, timedelta

import appcfg
from lib.utils import json_response
from orm.core import UserAccount
from random import getrandbits

from webargs import fields
from webargs.flaskparser import use_kwargs

auth_app = Blueprint('auth_app', __name__)


@auth_app.errorhandler(422)
def handle_bad_request(err):
    data = getattr(err, 'data')
    if data:
        messages = data['exc'].messages
    else:
        messages = ['Invalid Request']
    return jsonify({
        'messages': messages
    }), 422


@auth_app.route('/authenticate/', methods=['POST'])
@use_kwargs({
    'username': fields.String(required=True),
    'password': fields.String(required=True)
}, locations=('json',))
def authenticate(username, password):
    # Fetch the target user
    user = current_app.db.session.query(UserAccount)\
            .filter((UserAccount.username == username) | (UserAccount.email == username))\
            .one_or_none()

    if user:
        now = datetime.utcnow()

        if user.active:
            if user.password_reset_token is None:
                # Reset the failed attempts counter if the last attempt was more than FAILED_PASSWORD_LOCKOUT_DURATION
                # seconds ago
                if user.failed_attempts >= appcfg.MAX_FAILED_PASSWORD_ATTEMPTS and\
                        (now - user.failed_attempt_ts).seconds > appcfg.FAILED_PASSWORD_LOCKOUT_DURATION:
                    user.failed_attempts = 0

                # Make sure the user isn't locked out before checking the password
                if user.failed_attempts < appcfg.MAX_FAILED_PASSWORD_ATTEMPTS:
                    # The bcrypt algorithm only handles passwords up to 72 characters, so we base64 encode
                    # a sha256 hash of the password before checking with bcrypt. Also, character encoding is stupid
                    # in python3
                    prehashed_password = base64.b64encode(hashlib.sha256(password.encode('utf-8', 'strict')).digest()).decode('utf-8')

                    if bcrypt.checkpw(prehashed_password.encode('utf-8', 'strict'), user.password.encode('utf-8', 'strict')):
                        # Reset the failed attempts counter to 0 after successful authentication
                        user.failed_attempts = 0
                        user.last_login = now

                        # If the password has expired, do not complete authentication until it has been reset
                        if (now - user.password_ts).seconds > appcfg.PASSWORD_EXPIRATION_DAYS * 24 * 60 * 60:
                            return jsonify({'success': False, 'message': 'Password has expired and needs to be reset for authentication'}), 409

                        else:
                            results = {
                                'success': True,
                                'user': user.as_dict()
                            }

                            current_app.db.session.commit()

                            return json_response(results)
                    else:
                        # Increment the failed attempts counter and update the failed attempt timestamp after failure
                        user.failed_attempts += 1
                        user.failed_attempt_ts = now

                        current_app.db.session.commit()

                        return jsonify({'success': False, 'message': 'Invalid username and password combination'}), 401
                else:
                    if current_app.db.session.dirty:
                        current_app.db.session.commit()

                    # Locked out users cannot authenticate
                    return jsonify({
                        'success': False,
                        'message': 'User must wait at least {} minutes for account to unlock'.format((appcfg.FAILED_PASSWORD_LOCKOUT_DURATION - (now - user.failed_attempt_ts).seconds) / 60)
                    }), 401
            else:
                # Users with a password reset under way cannot authenticate until the reset is completed
                return jsonify({
                    'success': False,
                    'message': 'User must complete the password reset process before authenticating again.'
                }), 403
        else:
            # This user is not active right now, therefore cannot authenticate
            return jsonify({'success': False, 'message': 'Unable to authenticate with username and password combination'}), 403
    else:
        return jsonify({'success': False, 'message': 'Unable to find user with the given username/email'}), 404


@auth_app.route('/confirm-email/', methods=['POST'])
@use_kwargs({
    'token': fields.String(required=True)
}, locations=('json',))
def confirm_email(token):

    user = current_app.db.session.query(UserAccount).filter(UserAccount.email_token == token).one_or_none()

    if user:
        if not user.confirmed:
            now = datetime.utcnow()

            # Make sure the email was confirmed within the allowed timeframe
            if (now - user.email_token_ts).seconds < appcfg.EMAIL_CONFIRMATION_DURATION_HOURS * 60 * 60:
                user.confirmed = True

                current_app.db.session.commit()

                return json_response({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Unable to confirm email address due to exceeded time limit'}), 403
        else:
            return jsonify({'success': False, 'message': 'Email address already confirmed'}), 403
    else:
        return jsonify({'success': False, 'message': 'Invalid email confirmation token'}), 404


@auth_app.route('/reset-password/', methods=['POST'])
@use_kwargs({
    'username': fields.String(required=True)
}, locations=('json',))
def reset_password(username):

    user = current_app.db.session.query(UserAccount)\
        .filter((UserAccount.username == username) | (UserAccount.email == username))\
        .one_or_none()

    if user and user.active:
        if user.confirmed:
            now = datetime.utcnow()

            user.password_reset_token = '%0x' % getrandbits(128 * 4)
            user.password_reset_ts = now

            # TODO: send rabbit message for email delivery with password reset instructions

            current_app.db.session.commit()

            return json_response({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Users cannot reset passwords until an email address is confirmed'}), 403
    else:
        return jsonify({'success': False, 'message': 'Unable to find active user with the given username or email'}), 404
