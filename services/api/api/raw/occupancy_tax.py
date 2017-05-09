from flask import Blueprint, jsonify, current_app
from datetime import date, timedelta
from lib.utils import json_response

from webargs import fields
from webargs.flaskparser import use_kwargs

raw_occupancy_tax_app = Blueprint('raw_occupancy_tax_app', __name__)


@raw_occupancy_tax_app.errorhandler(422)
def handle_bad_request(err):
    data = getattr(err, 'data')
    if data:
        messages = data['exc'].messages
    else:
        messages = ['Invalid Request']
    return jsonify({
        'messages': messages
    }), 422


@raw_occupancy_tax_app.route('/occupancy-tax/', methods=['POST'])
@use_kwargs({
    'month': fields.Int(required=True),
    'year': fields.Int(required=True),
    'quarter': fields.Str(required=True),
    'taxpayer_number': fields.Str(required=True),
    'taxpayer_name': fields.Str(required=True),
    'taxpayer_address': fields.Str(required=True),
    'taxpayer_city': fields.Str(required=True),
    'taxpayer_state': fields.Str(required=True),
    'taxpayer_zip': fields.Str(required=True),
    'taxpayer_county_code': fields.Str(required=True),
    'taxpayer_county': fields.Str(missing=''),
    'taxpayer_latitude': fields.Decimal(missing=None),
    'taxpayer_longitude': fields.Decimal(missing=None),
    'hotel_location_number': fields.Str(required=True),
    'hotel_name': fields.Str(required=True),
    'hotel_address': fields.Str(required=True),
    'hotel_city': fields.Str(required=True),
    'hotel_state': fields.Str(required=True),
    'hotel_zip': fields.Str(required=True),
    'hotel_inside_city_limits': fields.Boolean(required=True),
    'hotel_county_code': fields.Str(required=True),
    'hotel_county': fields.Str(missing=''),
    'hotel_latitude': fields.Decimal(missing=None),
    'hotel_longitude': fields.Decimal(missing=None),
    'hotel_rooms': fields.Int(required=True),
    'hotel_total_room_receipts': fields.Decimal(required=True),
    'hotel_taxable_room_receipts': fields.Decimal(required=True)
}, locations=('json',))
def mds_late_submissions(month, year, quarter, taxpayer_number, taxpayer_name, taxpayer_address,
        taxpayer_city, taxpayer_state, taxpayer_zip, taxpayer_county_code, taxpayer_county,
        taxpayer_latitude, taxpayer_longitude, hotel_location_number, hotel_name, hotel_address,
        hotel_city, hotel_state, hotel_zip, hotel_inside_city_limits, hotel_county_code, hotel_county,
        hotel_latitude, hotel_longitude, hotel_rooms, hotel_total_room_receipts,
        hotel_taxable_room_receipts):

    now = date.today()

    json_results = {
        'totals': total,
        'days': days,
        'providers': providers,
        'residents': residents
    }

    return json_response(json_results)
