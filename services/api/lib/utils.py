import json
import time
from decimal import Decimal
from flask import make_response, current_app
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

row2dict = lambda r: dict(zip(r.keys(), r))


def tryparse(IgnoreException=Exception):
    def dec(func):
        def _dec(target, default=None):
            try:
                return func(target)
            except IgnoreException:
                return default
        return _dec
    return dec


tryparseint = tryparse(ValueError)(int)
tryparsefloat = tryparse(ValueError)(float)


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d")
    else:
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))


def parsedate(tgt):
    return parse(tgt).date()


def parsedatetime(tgt):
    return parse(tgt)


def tojson(obj):
    return json.dumps(obj, default=json_date_handler)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def json_response(body, status_code=200):
    """Serializes the body object into JSON and returns a response with the proper Content-Type"""
    resp = make_response(json.dumps(body, cls=JsonEncoder))
    resp.headers['Content-Type'] = 'application/json'
    resp.status_code = status_code
    return resp


def json_message(body, status_code=200):
    """Takes the given string and creates a JSON response of the form {"message": body}"""
    resp = json_response({'message': body})
    resp.status_code = status_code
    return resp


def json_error_message(err, status_code=500):
    """Takes the given error string and creates a JSON message response with the given error code"""
    resp = json_message(err)
    resp.status_code = status_code
    # Don't log 400 errors as errors, as those were client request errors. Log as info.
    if status_code / 100 == 4:
        current_app.logger.info(err)
    else:
        current_app.logger.error(err)
    return resp


# Merges 2 dictionaries by mutating the first dictionary. Values in the second dictionary will override values in the first
# To merge multiple dictionaries - reduce(merge, [dict1, dict2, dict3...])
def merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


# Determines the time interval to use for each data point depending on the length of the
# given timeframe
def calculate_data_interval(start, end):
    diff = end - start
    # day
    if diff.days <= 31:
        return 'day'
    # week
    elif diff.days / 7 <= 24:
        return 'week'
    # month
    elif diff.days / 30 <= 48:
        return 'month'
    # default to year
    else:
        return 'year'


def get_quarter(q):
    if type(q) is str or type(q) is unicode:
        year = int(str(q)[0:4])
        quarter = int(str(q)[-1])

        quarters = {
            1: {  # Q1
                'start': date(year, 1, 1),
                'end': date(year, 3, 31),
                'year': year,
                'quarter': 'Q1'
            },
            2: {  # Q2
                'start': date(year, 4, 1),
                'end': date(year, 6, 30),
                'year': year,
                'quarter': 'Q2'
            },
            3: {  # Q3
                'start': date(year, 7, 1),
                'end': date(year, 9, 30),
                'year': year,
                'quarter': 'Q3'
            },
            4: {  # Q4
                'start': date(year, 10, 1),
                'end': date(year, 12, 31),
                'year': year,
                'quarter': 'Q4'
            }
        }

        # Return a tuple of (start_date, end_date) for this quarter
        return quarters[quarter]['start'], quarters[quarter]['end'], quarters[quarter]['year'], quarters[quarter]['quarter']
    elif type(q) is date or type(q) is datetime:
        if q.month in [1, 2, 3]:
            return date(q.year, 1, 1), date(q.year, 3, 31), q.year, 'Q1'
        elif q.month in [4, 5, 6]:
            return date(q.year, 4, 1), date(q.year, 6, 30), q.year, 'Q2'
        elif q.month in [7, 8, 9]:
            return date(q.year, 7, 1), date(q.year, 9, 30), q.year, 'Q3'
        else:
            return date(q.year, 10, 1), date(q.year, 12, 31), q.year, 'Q4'

    return None


def get_previous_quarter(q, skip=0):
    q_date = None

    if type(q) is str or type(q) is unicode:
        year = int(str(q)[0:4])
        quarter = int(str(q)[-1])

        if quarter == 1:
            q_date = date(year, 1, 1)
        elif quarter == 2:
            q_date = date(year, 4, 1)
        elif quarter == 3:
            q_date = date(year, 7, 1)
        elif quarter == 4:
            q_date = date(year, 10, 1)
    else:
        q_date = q

    if q_date.month in [1, 2, 3]:
        prev_start, prev_end, prev_year, prev_qrtr = date(q_date.year - 1, 10, 1), date(q_date.year - 1, 12, 31), q_date.year - 1, 'Q4'
    elif q_date.month in [4, 5, 6]:
        prev_start, prev_end, prev_year, prev_qrtr = date(q_date.year, 1, 1), date(q_date.year, 3, 31), q_date.year, 'Q1'
    elif q_date.month in [7, 8, 9]:
        prev_start, prev_end, prev_year, prev_qrtr = date(q_date.year, 4, 1), date(q_date.year, 6, 30), q_date.year, 'Q2'
    else:
        prev_start, prev_end, prev_year, prev_qrtr = date(q_date.year, 7, 1), date(q_date.year, 9, 30), q_date.year, 'Q3'

    if skip <= 0:
        return prev_start, prev_end, prev_year, prev_qrtr
    else:
        return get_previous_quarter(prev_end, skip - 1)


def get_query_parameters(current_date, timeframe, start, end, providers):
    if timeframe == "last30":
        end = current_date
        start = current_date + timedelta(days=-30)
        return {
            "start": start,
            "end": end,
            "interval": "day",
            "providers": providers
        }
    if timeframe == "last90":
        end = current_date
        start = current_date + timedelta(days=-90)
        return {
            "start": start,
            "end": end,
            "interval": "week",
            "providers": providers
        }
    if timeframe == "last365":
        end = current_date
        start = current_date + timedelta(days=-365)
        return {
            "start": start,
            "end": end,
            "interval": "month",
            "providers": providers
        }
    if timeframe == "year":
        return {
            "start": date(current_date.year, 1, 1),
            "end": date(current_date.year + 1, 1, 1),
            "interval": "month",
            "providers": providers
        }

    if timeframe == "quarter":
        quarter = ((current_date.month - 1) // 3) + 1
        month = ((quarter - 1) * 3) + 1
        start = date(current_date.year, month, 1)
        return {
            "start": start,
            "end": start + relativedelta(months=+3),
            "interval": "week",
            "providers": providers
        }

    if timeframe == 'custom' and start and end:
        return {
            'start': start.date(),
            'end': end.date(),
            'interval': calculate_data_interval(start.date(), end.date()),
            'providers': providers
        }

    start = date(current_date.year, current_date.month, 1)
    return {
        "start": start,
        "end": start + relativedelta(months=+1),
        "interval": "day",
        "providers": providers
    }


class Timer:
    def __init__(self, name='context timer'):
        self.name = name

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        print('{} - took {} sec.'.format(self.name, time.clock() - self.start))
