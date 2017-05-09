from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, text, SmallInteger, CHAR, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

from orm.base import Base, PG_Base


class Report(Base, PG_Base):
    __tablename__ = 'report'

    _protected_cols = ['users.password', 'created_by.password']

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    draft = Column('draft', Boolean, nullable=False, server_default='True')
    title = Column('title', String(512), nullable=False)
    description = Column('description', Text)
    settings = Column('settings', JSON)

    created_by_uid = Column('created_by_uid', BigInteger, ForeignKey('user_account.uid'), nullable=False)

    users = relationship('UserAccount', secondary='user_account_report', backref='reports')
    created_by = relationship('UserAccount', back_populates='created_reports')
    widgets = relationship('ReportWidget', backref='report')


class UserAccountReport(Base, PG_Base):
    __tablename__ = 'user_account_report'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    user_account_uid = Column('user_account_uid', BigInteger, ForeignKey('user_account.uid'), nullable=False)
    report_uid = Column('report_uid', BigInteger, ForeignKey(Report.uid), nullable=False)

    unique_user_account_report_user_account_uid_report_uid = UniqueConstraint(user_account_uid, report_uid, name='unique_user_account_report_user_account_uid_report_uid')


class Widget(Base, PG_Base):
    __tablename__ = 'widget'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    title = Column('title', String(512), nullable=False)
    description = Column('description', Text)
    parameters = Column('parameters', JSON)
    settings = Column('settings', JSON)

    parameters = relationship('WidgetParameter', backref='widget')
    settings = relationship('WidgetSetting', backref='widget')


class WidgetParameter(Base, PG_Base):
    __tablename__ = 'widget_parameter'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(256), nullable=False)
    description = Column('description', Text, nullable=False)
    data_type = Column('data_type', String(64), nullable=False, server_default='str')
    required = Column('required', Boolean, nullable=False, server_default='False')
    default = Column('default', String(2048), nullable=True)
    options = Column('options', ARRAY(String(512)), nullable=True)
    multi_option = Column('multi_option', Boolean, nullable=False, server_default='False')

    widget_uid = Column('widget_uid', BigInteger, ForeignKey(Widget.uid), nullable=False)


class WidgetSetting(Base, PG_Base):
    __tablename__ = 'widget_setting'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(256), nullable=False)
    description = Column('description', Text, nullable=False)
    data_type = Column('data_type', String(64), nullable=False, server_default='str')
    required = Column('required', Boolean, nullable=False, server_default='False')
    default = Column('default', String(2048), nullable=True)
    options = Column('options', ARRAY(String(512)), nullable=True)
    multi_option = Column('multi_option', Boolean, nullable=False, server_default='False')

    widget_uid = Column('widget_uid', BigInteger, ForeignKey(Widget.uid), nullable=False)


class ReportWidget(Base, PG_Base):
    __tablename__ = 'report_widget'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    path = Column('path', String(1024), nullable=False)
    column = Column('column', Integer, nullable=False)
    order = Column('order', Integer, nullable=False)
    parameters = Column('parameters', JSON)
    settings = Column('settings', JSON)

    report_uid = Column('report_uid', BigInteger, ForeignKey(Report.uid), nullable=False)
