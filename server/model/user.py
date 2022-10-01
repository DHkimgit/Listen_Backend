from sqlalchemy import Column, BigInteger, SmallInteger, String, DateTime, Boolean, Enum, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(BigInteger, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  service_number = Column(String, nullable=False)
  email = Column(String(20), unique=True, index=True)
  is_admin = Column(Boolean, default=False)

class Users(Base):
  __tablename__ = "users"
  id = Column(BigInteger, primary_key=True, index=True)
  status = Column(Enum("admin", "normal"), default="active")
  email = Column(String(length=255), nullable=True)
  pw = Column(String(length=2000), nullable=True)
  name = Column(String(length=255), nullable=True)
  phone_number = Column(String(length=20), nullable=True, unique=True)
  created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
  updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

# class User_real(Base):
#   __tablename__ = 'user'
#   service_number = Column(String(length=15, collation='utf8'), primary_key=True, nullable=False)