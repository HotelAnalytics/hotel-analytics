from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, text, SmallInteger, CHAR,\
        BigInteger, UniqueConstraint, CheckConstraint, Date, DECIMAL
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

from orm.base import Base, PG_Base
from orm.authorization import Role, Permission
from orm.occupancy_tax import OccupancyTaxReport
from orm.reports import Report


class UserAccount(Base, PG_Base):
    __tablename__ = 'user_account'

    _protected_cols = ['password']

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    username = Column('username', String(256), nullable=False, unique=True)
    email = Column('email', String(254), nullable=False, unique=True)
    phone = Column('phone', String(32))
    confirmed = Column('confirmed', Boolean, nullable=False, server_default='False')
    email_token = Column('email_token', String(512), nullable=False, unique=True)
    email_token_ts = Column('email_token_ts', TIMESTAMP, nullable=False, server_default=text("timezone('utc'::text, now())"))
    password = Column('password', String(1024))
    password_ts = Column('password_ts', TIMESTAMP, nullable=False, server_default=text("timezone('utc'::text, now())"))
    active = Column('active', Boolean, nullable=False, server_default='True')
    first_name = Column('first_name', String(256), nullable=False)
    last_name = Column('last_name', String(256), nullable=False)
    title = Column('title', String(128))
    created_by_uid = Column('created_by_uid', Integer, ForeignKey('user_account.uid'), nullable=True)
    mfa_enabled = Column('mfa_enabled', Boolean, nullable=False, server_default='False')
    last_login = Column('last_login', TIMESTAMP)
    password_reset_token = Column('password_reset_token', String(512))
    password_reset_ts = Column('password_reset_ts', TIMESTAMP)
    failed_attempts = Column('failed_attempts', SmallInteger, nullable=False, server_default=text('0'))
    failed_attempt_ts = Column('failed_attempt_ts', TIMESTAMP, nullable=False, server_default=text("timezone('utc'::text, now())"))
    settings = Column('settings', JSON)

    created_by = relationship('UserAccount')
    created_reports = relationship(Report, back_populates='created_by')

    unique_user_account_username = UniqueConstraint(username, name='unique_user_account_username')
    unique_user_account_email = UniqueConstraint(email, name='unique_user_account_email')
    unique_user_account_email_token = UniqueConstraint(email_token, name='unique_user_account_email_token')

    __table_args__ = (
        CheckConstraint(
            "username ~* '^[A-Za-z][-A-Za-z0-9._]{5,}$'",
            name='valid_user_account_username',
            info={
                'description': 'Usernames must be at least 6 characters long and start with a letter followed by any combination of numbers, letters, periods, underscores, or dashes.',
                'fields': ['username']
            }
        ),
        CheckConstraint(
            "email ~* '^[^@\s]+@[^@\s]+\.[^@\s]{2,}$'",
            name='valid_user_account_email',
            info={
                'description': 'Email addresses must be valid.',
                'fields': ['email']
            }
        ),
        CheckConstraint(
            "phone ~* '^(\+?\d{1,2}[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}$'",
            name='valid_user_account_phone',
            info={
                'description': 'Phone numbers must be a valid NANP number with 7 digits preceded by an area code and an optional country code.',
                'fields': ['phone']
            }
        )
    )


class Company(Base, PG_Base):
    __tablename__ = 'company'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(512), nullable=False)
    address_to = Column('address_to', String(64))
    address = Column('address', String(128))
    city = Column('city', String(128))
    state = Column('state', String(32))
    zip = Column('zip', String(16))
    phone = Column('phone', String(16))
    fax = Column('fax', String(16))


class Property(Base, PG_Base):
    __tablename__ = 'property'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(256), nullable=False)
    address = Column('address', String(512), nullable=False)
    city = Column('city', String(256), nullable=False)
    state = Column('state', String(2), nullable=False)
    zip = Column('zip', String(32), nullable=False)
    inside_city_limits = Column('inside_city_limits', Boolean, nullable=False, server_default='True')
    county_code = Column('county_code', String(16))
    county = Column('county', String(256))
    latitude = Column('latitude', DECIMAL)
    longitude = Column('longitude', DECIMAL)
    rooms = Column('rooms', Integer, nullable=False)

    companies = relationship(Company, secondary='company_property', backref='properties')
    occupancy_tax_reports = relationship(OccupancyTaxReport, backref='property')


class CompanyProperty(Base, PG_Base):
    __tablename__ = 'company_property'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    company_uid = Column('company_uid', BigInteger, ForeignKey(Company.uid), nullable=False)
    property_uid = Column('property_uid', BigInteger, ForeignKey(Property.uid), nullable=False)
    start_date = Column('start_date', Date, nullable=False)
    end_date = Column('end_date', Date, nullable=True, server_default=text('Null'))

    unique_company_property_company_uid_property_uid = UniqueConstraint(company_uid, property_uid, name='unique_company_property_company_uid_property_uid')
