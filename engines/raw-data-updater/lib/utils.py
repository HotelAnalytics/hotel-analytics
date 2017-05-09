import json
import math
from datetime import datetime, date, timedelta
from dateutil.parser import parse

def row2dict(r):
    return dict(zip(r.keys(), r))

def tryparse(IgnoreException=Exception):
    def dec(func):
        def _dec(target, mutator=None, default=None):
            try:
                return mutator(func(target)) if hasattr(mutator, '__call__') else func(target)
            except IgnoreException:
                return default
        return _dec
    return dec

tryparseint = tryparse((ValueError, TypeError))(int)
tryparsefloat = tryparse((ValueError, TypeError))(float)


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d")
    else:
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))


def parsedate(tgt):
    if isinstance(tgt, datetime):
        return tgt.date()
    if isinstance(tgt, date):
        return tgt
    return parse(tgt).date() if tgt is not None else None


def parsedatetime(tgt):
    return parse(tgt) if tgt is not None else None


def tojson(obj, sort_keys=False):
    return json.dumps(obj, default=json_date_handler, sort_keys=sort_keys)


# Merges 2 dictionaries by mutating the first dictionary. Values in the second dictionary will override values in the first
# To merge multiple dictionaries - reduce(merge, [dict1, dict2, dict3...])
def merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                a[key] = merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def percentile(vals, percent):
    if not vals:
        return None
    k = (len(vals) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    d0 = vals[int(f)] * (c - k)
    d1 = vals[int(c)] * (k - f)
    return d0 + d1


def get_quarter(q):
    if type(q) is str or type(q) is unicode:
        year = int(str(q).strip()[0:4])
        quarter = int(str(q).strip()[-1])

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


def get_quarter_start(q):
    start, end, year, qrtr = get_quarter(q)
    return start


def get_previous_quarter(q_date, skip=0):
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


def get_next_quarter(q_date, skip=0):
    if q_date.month in [1, 2, 3]:
        next_start, next_end, next_year, next_qrtr = date(q_date.year, 4, 1), date(q_date.year, 6, 30), q_date.year, 'Q2'
    elif q_date.month in [4, 5, 6]:
        next_start, next_end, next_year, next_qrtr = date(q_date.year, 7, 1), date(q_date.year, 9, 30), q_date.year, 'Q3'
    elif q_date.month in [7, 8, 9]:
        next_start, next_end, next_year, next_qrtr = date(q_date.year, 10, 1), date(q_date.year, 12, 31), q_date.year, 'Q4'
    else:
        next_start, next_end, next_year, next_qrtr = date(q_date.year + 1, 1, 1), date(q_date.year + 1, 3, 31), q_date.year + 1, 'Q1'

    if skip <= 0:
        return next_start, next_end, next_year, next_qrtr
    else:
        return get_next_quarter(next_end, skip - 1)
