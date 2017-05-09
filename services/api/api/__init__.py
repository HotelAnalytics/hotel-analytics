#!/usr/bin/env python2
import logging
import sys

from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from pymongo import MongoClient
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch

from orm.core import UserAccount, Company, Property, CompanyProperty
from orm.authorization import Role, UserAccountRole, Permission, RolePermission, UserAccountPermission
from orm.occupancy_tax import OccupancyTaxReport
from orm.reports import Report, UserAccountReport, Widget, WidgetParameter, WidgetSetting, ReportWidget

from api.auth import auth_app
from api.auth.user import user_app
from api.raw.occupancy_tax import raw_occupancy_tax_app
from api.redux.redux_actions import redux_actions_app
from api.errors.report import error_reports_app

from lib.simple_queue_service import SimpleQueueService

console_log_format = '%(asctime)s - %(levelname)s - %(message)s'
console_log_level = logging.INFO

api_version = 'v1'


def get_app(cfg=None):
    app = Flask(__name__)
    app.config.from_pyfile('../appcfg.py')
    url_prefix = '/{0}'.format(api_version)

    if (cfg):
        app.config.update(cfg)

    logging.captureWarnings(True)

    # Set up the PostgreSQL db connection
    db = SQLAlchemy(app)

    # Set up CRUD for ORM models
    manager = APIManager(flask_sqlalchemy_db=db)
    manager.init_app(app)

    def create_endpoints(*types):
        for type in types:
            manager.create_api(
                type,
                app=app,
                url_prefix=url_prefix,
                methods=['GET', 'POST', 'PUT', 'DELETE'],
                exclude_columns=type._protected_cols
            )

    create_endpoints(UserAccount, Company, Property, CompanyProperty)
    create_endpoints(Role, UserAccountRole, Permission, RolePermission, UserAccountPermission)
    create_endpoints(OccupancyTaxReport)
    create_endpoints(Report, UserAccountReport, Widget, WidgetParameter, WidgetSetting, ReportWidget)

    app.register_blueprint(auth_app, url_prefix='/{}/auth'.format(api_version))
    app.register_blueprint(user_app, url_prefix='/{}/user'.format(api_version))
    app.register_blueprint(raw_occupancy_tax_app, url_prefix='/{}/raw'.format(api_version))
    app.register_blueprint(redux_actions_app)
    app.register_blueprint(error_reports_app)

    """
    if app.config.get('ENGINE_ENV') == 'prod':
        @app.errorhandler(Exception)
        def unhandled_exception(e):
            app.logger.error('Unhandled exception: %s', (e))
            return jsonify({'error': str(e)}), 500
    """

    app.db = db

    # Set up MongoDB connection
    mongo = MongoClient(app.config.get('MONGO_URI'))
    app.mongo = mongo

    # Set up elastic connection
    es_auth = '{}:{}'.format(app.config.get('ES_USER'), app.config.get('ES_PASSWORD'))
    es_host = '{}:{}'.format(app.config.get('ES_HOST'), app.config.get('ES_PORT'))
    es = Elasticsearch(es_host, use_ssl=app.config.get('ES_USE_SSL'), http_auth=es_auth, timeout=300)
    app.es = es

    # Set up the RabbitMQ connection
    app.queue_service = SimpleQueueService(app, app.logger)

    # Set up logging
    app.logger.setLevel(console_log_level)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=console_log_format))

    app.logger.addHandler(handler)

    return app


app = get_app()
