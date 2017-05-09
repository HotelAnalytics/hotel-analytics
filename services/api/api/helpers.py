import dateutil.parser
from flask import request


def iso_date(val):
    """Parses a string into a datetime"""
    return dateutil.parser.parse(val)


def get_query_params():
    """Converts a query string from the request into an ASCII-encoded dict"""
    query_params = {}

    for k, v in request.args.items():
        query_params[k] = v.encode('ASCII')

    return query_params
