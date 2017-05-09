from os import getenv

# This is where application configuration values go. Typically, these are
# pulled from environment variables, but defaults that can be used during dev /
# testing can be included here as well.
APP_NAME = getenv('APP_NAME', 'hotel-analytics-api')

ENGINE_ENV = getenv('ENGINE_ENV', 'dev')

POSTGRES_URI = getenv('POSTGRES_URI', "postgresql://db_admin:cMbTV2zZt4Zt2vb56xs@hotel-analytics.ccstulxwpbvn.us-west-2.rds.amazonaws.com:5432/hotel_analytics?client_encoding=utf8")
SQLALCHEMY_DATABASE_URI = POSTGRES_URI

LOG_ENABLED = bool(int(getenv('LOG_ENABLED', '1')))
LOG_LOCAL = bool(int(getenv('LOG_LOCAL', '1')))
LOG_REMOTE = bool(int(getenv('LOG_REMOTE', '0')))

SQLALCHEMY_RECORD_QUERIES = bool(int(getenv('RECORD_QUERIES', '0')))
LONG_QUERY_THRESHOLD = float(getenv('LONG_QUERY_THRESHOLD', 1.0))
SQLALCHEMY_TRACK_MODIFICATIONS = bool(int(getenv('SQLALCHEMY_TRACK_MODIFICATIONS', '0')))

ES_USER = getenv('ES_USER', 'devuser')
ES_PASSWORD = getenv('ES_PASSWORD', 'p@ssw0rd!')
ES_HOST = getenv('ES_HOST', 'search-hotel-analytics-ewfvepr34ldl4ig2kjraxdtklu.us-west-2.es.amazonaws.com')
ES_PORT = getenv('ES_PORT', '9200')
ES_USE_SSL = bool(int(getenv('ES_USE_SSL', '0')))

MONGO_URI = getenv('MONGO_URI', 'mongodb://hotel_analytics_api:8hWDzcnxaQwGNyZxJS7rM6S84KfMP@mongo-dev.simpleltc.local:27017/redux')

AMQP_HOST = getenv('AMQP_HOST', 'rabbit.hotel-analytics.com')
AMQP_HOST_FALLBACK = getenv('AMQP_HOST_FALLBACK', 'rabbit.hotel-analytics.com')

REDUX_AMQP_EXCHANGE = getenv('REDUX_AMQP_EXCHANGE', 'logs.redux')
UI_AMQP_QUEUE = getenv('UI_AMQP_QUEUE', 'logs.ui')

TIMESTAMP_FORMAT = getenv('TIMESTAMP_FORMAT', '%Y-%m-%d %H:%M:%S')

MAX_FAILED_PASSWORD_ATTEMPTS = getenv('MAX_FAILED_PASSWORD_ATTEMPTS', 5)
FAILED_PASSWORD_LOCKOUT_DURATION = getenv('FAILED_PASSWORD_LOCKOUT_DURATION', 300)

EMAIL_CONFIRMATION_DURATION_HOURS = getenv('EMAIL_CONFIRMATION_DURATION_HOURS', 24)

PASSWORD_EXPIRATION_DAYS = getenv('PASSWORD_EXPIRATION_DAYS', 120)

PASSWORD_RESET_DURATION_MINUTES = getenv('PASSWORD_RESET_DURATION_MINUTES', 30)
