from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, text, SmallInteger, CHAR, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

from orm.base import Base, PG_Base


class Role(Base, PG_Base):
    __tablename__ = 'role'

    _protected_cols = ['users.password']

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(256), nullable=False, unique=True)
    description = Column('description', Text)

    users = relationship('UserAccount', secondary='user_account_role', backref='roles')
    permissions = relationship('Permission', secondary='role_permission', backref='roles')


class UserAccountRole(Base, PG_Base):
    __tablename__ = 'user_account_role'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    user_account_uid = Column('user_account_uid', BigInteger, ForeignKey('user_account.uid'), nullable=False)
    role_uid = Column('role_uid', BigInteger, ForeignKey(Role.uid), nullable=False)

    unique_user_account_role_user_account_uid_role_uid = UniqueConstraint(user_account_uid, role_uid, name='unique_user_account_role_user_account_uid_role_uid')


class Permission(Base, PG_Base):
    __tablename__ = 'permission'

    _protected_cols = ['users.password']

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column('name', String(256), nullable=False, unique=True)
    description = Column('description', Text)

    users = relationship('UserAccount', secondary='user_account_permission', backref='permissions')


class RolePermission(Base, PG_Base):
    __tablename__ = 'role_permission'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    role_uid = Column('role_uid', BigInteger, ForeignKey(Role.uid), nullable=False)
    permission_uid = Column('permission_uid', BigInteger, ForeignKey(Permission.uid), nullable=False)

    unique_role_permission_role_uid_permission_uid = UniqueConstraint(role_uid, permission_uid, name='unique_role_permission_role_uid_permission_uid')


class UserAccountPermission(Base, PG_Base):
    __tablename__ = 'user_account_permission'

    uid = Column('uid', BigInteger, primary_key=True, autoincrement=True, nullable=False)
    user_account_uid = Column('user_account_uid', BigInteger, ForeignKey('user_account.uid'), nullable=False)
    permission_uid = Column('permission_uid', BigInteger, ForeignKey(Permission.uid), nullable=False)
    permit = Column('permit', Boolean, nullable=False, server_default='True')

    unique_user_account_permission_user_account_uid_permission_uid = UniqueConstraint(user_account_uid, permission_uid, name='unique_user_account_permission_user_account_uid_permission_uid')
