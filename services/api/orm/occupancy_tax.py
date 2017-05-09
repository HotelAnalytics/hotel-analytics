from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, text, SmallInteger, CHAR, DECIMAL, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

from orm.base import Base, PG_Base


class OccupancyTaxReport(Base, PG_Base):
    __tablename__ = 'occupancy_tax_report'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    month = Column('month', Integer, nullable=False)
    year = Column('year', Integer, nullable=False)
    quarter = Column('quarter', String, nullable=False)
    taxpayer_number = Column('taxpayer_number', String(64), nullable=False)
    taxpayer_name = Column('taxpayer_name', String(512), nullable=False)
    taxpayer_address = Column('taxpayer_address', String(512), nullable=False)
    taxpayer_city = Column('taxpayer_city', String(256), nullable=False)
    taxpayer_state = Column('taxpayer_state', String(2), nullable=False)
    taxpayer_zip = Column('taxpayer_zip', String(32), nullable=False)
    taxpayer_county_code = Column('taxpayer_county_code', String(16))
    taxpayer_county = Column('taxpayer_county', String(256))
    taxpayer_latitude = Column('taxpayer_latitude', DECIMAL)
    taxpayer_longitude = Column('taxpayer_longitude', DECIMAL)
    hotel_location_number = Column('hotel_location_number', String, nullable=False)
    hotel_name = Column('hotel_name', String(512), nullable=False)
    hotel_address = Column('hotel_address', String(512), nullable=False)
    hotel_city = Column('hotel_city', String(256), nullable=False)
    hotel_state = Column('hotel_state', String(2), nullable=False)
    hotel_zip = Column('hotel_zip', String(32), nullable=False)
    hotel_inside_city_limits = Column('hotel_inside_city_limits', Boolean, nullable=False, server_default='True')
    hotel_county_code = Column('hotel_county_code', String(16))
    hotel_county = Column('hotel_county', String(256))
    hotel_latitude = Column('hotel_latitude', DECIMAL)
    hotel_longitude = Column('hotel_longitude', DECIMAL)
    hotel_rooms = Column('hotel_rooms', Integer, nullable=False)
    hotel_total_room_receipts = Column('hotel_total_room_receipts', DECIMAL, nullable=False)
    hotel_taxable_room_receipts = Column('hotel_taxable_room_receipts', DECIMAL, nullable=False)

    property_uid = Column('property_uid', BigInteger, ForeignKey('property.uid'))
