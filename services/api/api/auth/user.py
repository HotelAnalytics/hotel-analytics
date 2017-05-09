import bcrypt
import hashlib
import base64
import psycopg2
import re

from flask import Blueprint, jsonify, current_app
from datetime import date, datetime, timedelta
from random import getrandbits
from sqlalchemy.exc import IntegrityError

import appcfg
from lib.utils import json_response
from orm.core import UserAccount

from webargs import fields
from webargs.flaskparser import use_kwargs

user_app = Blueprint('user_app', __name__)


@user_app.errorhandler(422)
def handle_bad_request(err):
    data = getattr(err, 'data')
    if data:
        messages = data['exc'].messages
    else:
        messages = ['Invalid Request']
    return jsonify({
        'messages': messages
    }), 422


@user_app.route('/register/', methods=['POST'])
@use_kwargs({
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'email_confirmation': fields.String(required=True),
    'phone': fields.String(required=True),
    'password': fields.String(required=True),
    'password_confirmation': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'title': fields.String(missing=None)
}, locations=('json',))
def register_user_account(username, email, email_confirmation, phone, password, password_confirmation, first_name, last_name, title):
    try:
        # Make sure email and password confirmations match
        if email == email_confirmation:
            if password == password_confirmation:
                # Make sure the password is complex enough
                if re.match(r'^(?=.*[A-Z])(?=.*[-!@#$&*_^%()+=?<>])(?=.*[0-9])(?=.*[a-z]).{8,}$', password):
                    # Hash the password first. The bcrypt algorithm only handles passwords up to 72 characters, so we
                    # base64 encode a sha256 hash of the password before checking with bcrypt. Also, character encoding
                    # is stupid in python3
                    prehashed_password = base64.b64encode(hashlib.sha256(password.encode('utf-8', 'strict')).digest()).decode('utf-8')
                    hashed_password = bcrypt.hashpw(prehashed_password.encode('utf-8', 'strict'), bcrypt.gensalt()).decode('utf-8')

                    user = UserAccount(
                        username=username,
                        email=email,
                        email_token='%0x' % getrandbits(128 * 4),
                        phone=phone,
                        password=hashed_password,
                        first_name=first_name,
                        last_name=last_name,
                        title=title
                    )

                    # TODO: send rabbit message for email delivery with confirmation link

                    current_app.db.session.add(user)
                    current_app.db.session.commit()

                    return json_response({
                        'success': True,
                        'user': user.as_dict()
                    })

                else:
                    return jsonify({
                        'success': False,
                        'message': 'Password does not meet the minimum complexity requirements',
                        'fields': ['password'],
                        'reason': 'Passwords must be at least 8 characters long and contain at least 1 uppercase letter, 1 lowercase letter, 1 special character, and 1 number.'
                    }), 409

            else:
                return jsonify({
                    'success': False,
                    'message': 'Passwords do not match',
                    'fields': ['password', 'password_confirmation'],
                    'reason': 'The password confirmation does not match the first password.'
                }), 409
        else:
            return jsonify({
                'success': False,
                'message': 'Emails do not match',
                'fields': ['email', 'email_confirmation'],
                'reason': 'The email address confirmation does not match the first email address.'
            }), 409

    except IntegrityError as e1:
        if isinstance(e1.orig, psycopg2.IntegrityError):
            current_app.db.session.rollback()

            current_app.logger.error(e1.orig.pgerror)

            constraint_name = e1.orig.diag.constraint_name
            constraint_info = {x.name: x.info for x in UserAccount.__table_args__}

            return jsonify({
                'success': False,
                'message': e1.orig.diag.message_primary,
                'fields': constraint_info[constraint_name]['fields'],
                'reason': constraint_info[constraint_name]['description']
            }), 409

        else:
            raise e1

    except Exception as e2:
        current_app.logger.error('Unable to register new user - {}: {}'.format(type(e2).__name__, e2))

        current_app.db.session.rollback()

        return jsonify({'success': False, 'message': 'Unable to register new user - {}: {}'.format(type(e2).__name__, e2)}), 500


@user_app.route('/change-password/', methods=['POST'])
@use_kwargs({
    'username': fields.String(missing=None),
    'old_password': fields.String(missing=None),
    'password': fields.String(required=True),
    'password_confirmation': fields.String(required=True),
    'password_reset_token': fields.String(missing=None)
}, locations=('json',))
def change_password(username, old_password, password, password_confirmation, password_reset_token):
    # Fetch the target user either by username/email or password_reset_token, depending on how the user
    # reached this endpoint
    user = None
    if password_reset_token is None:
        user = current_app.db.session.query(UserAccount)\
                .filter((UserAccount.username == username) | (UserAccount.email == username))\
                .one_or_none()

    elif username:
        user = current_app.db.session.query(UserAccount)\
                .filter((UserAccount.email == username) & (UserAccount.password_reset_token == password_reset_token))\
                .one_or_none()

    else:
        return jsonify({'success': False, 'message': 'Missing user identification parameters'}), 400

    if user:
        now = datetime.utcnow()

        if user.active:
            # Reset the failed attempts counter if the last attempt was more than FAILED_PASSWORD_LOCKOUT_DURATION
            # seconds ago
            if password_reset_token is None and\
                    user.failed_attempts >= appcfg.MAX_FAILED_PASSWORD_ATTEMPTS and\
                    (now - user.failed_attempt_ts).seconds > appcfg.FAILED_PASSWORD_LOCKOUT_DURATION:
                user.failed_attempts = 0

            # Make sure the user isn't locked out before checking the password
            if user.failed_attempts < appcfg.MAX_FAILED_PASSWORD_ATTEMPTS or password_reset_token is not None:
                if password == password_confirmation:
                    # Make sure the password is complex enough
                    if re.match(r'^(?=.*[A-Z])(?=.*[-!@#$&*_^%()+=?<>])(?=.*[0-9])(?=.*[a-z]).{8,}$', password):
                        # Hash the password first. The bcrypt algorithm only handles passwords up to 72 characters, so we
                        # base64 encode a sha256 hash of the password before checking with bcrypt. Also, character encoding
                        # is stupid in python3
                        prehashed_password = base64.b64encode(hashlib.sha256(password.encode('utf-8', 'strict')).digest()).decode('utf-8')
                        hashed_password = bcrypt.hashpw(prehashed_password.encode('utf-8', 'strict'), bcrypt.gensalt()).decode('utf-8')

                        if password_reset_token is not None:
                            # Make sure the password reset token hasn't expired
                            if (now - user.password_reset_ts).seconds <= appcfg.PASSWORD_RESET_DURATION_MINUTES * 60:
                                user.password = hashed_password
                                user.password_ts = now
                                user.password_reset_token = None
                                user.failed_attempts = 0

                                current_app.db.session.commit()

                                return json_response({'success': True, 'user': user.as_dict()})

                            else:
                                return jsonify({
                                    'success': False,
                                    'message': 'Unable to reset password due to exceeded time limit. Submit another password reset request to receive a new token'
                                }), 403

                        else:
                            # The bcrypt algorithm only handles passwords up to 72 characters, so we base64 encode
                            # a sha256 hash of the password before checking with bcrypt. Also, character encoding is stupid
                            # in python3
                            prehashed_old_password = base64.b64encode(hashlib.sha256(old_password.encode('utf-8', 'strict')).digest()).decode('utf-8')

                            if bcrypt.checkpw(prehashed_old_password.encode('utf-8', 'strict'), user.password.encode('utf-8', 'strict')):
                                user.password = hashed_password
                                user.password_ts = now
                                user.failed_attempts = 0

                                current_app.db.session.commit()

                                return json_response({'success': True, 'user': user.as_dict()})

                            else:
                                # Increment the failed attempts counter and update the failed attempt timestamp after failure
                                user.failed_attempts += 1
                                user.failed_attempt_ts = now

                                current_app.db.session.commit()

                                return jsonify({'success': False, 'message': 'Invalid username and password combination'}), 401

                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Password does not meet the minimum complexity requirements',
                            'fields': ['password'],
                            'reason': 'Passwords must be at least 8 characters long and contain at least 1 uppercase letter, 1 lowercase letter, 1 special character, and 1 number.'
                        }), 409

                else:
                    return jsonify({
                        'success': False,
                        'message': 'Passwords do not match',
                        'fields': ['password', 'password_confirmation'],
                        'reason': 'The password confirmation does not match the first password.'
                    }), 409

            else:
                if current_app.db.session.dirty:
                    current_app.db.session.commit()

                # Locked out users cannot authenticate
                return jsonify({
                    'success': False,
                    'message': 'User must wait at least {} minutes for account to unlock'.format((appcfg.FAILED_PASSWORD_LOCKOUT_DURATION - (now - user.failed_attempt_ts).seconds) / 60)
                }), 401

        else:
            # This user is not active right now, therefore cannot authenticate
            return jsonify({'success': False, 'message': 'Unable to authenticate with username and password combination'}), 403

    else:
        return jsonify({'success': False, 'message': 'Invalid username/password combination or password reset token'}), 404
