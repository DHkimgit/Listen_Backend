from sqlalchemy import Column, BigInteger, SmallInteger, String, DateTime, Boolean, Enum, func, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Unit(Base):
    __tablename__ = 'unit'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(length=200), nullable=False)
    member = Column(BigInteger, nullable=False, default=0)

    user = relationship("User", back_populates="unit")


class User(Base):
    __tablename__ = 'user'
    service_number = Column(String(length=15, collation='utf8'), primary_key=True, nullable=False)
    pw = Column(String(length=2000), nullable=False)
    name = Column(String(length=255, collation='utf8'), nullable=False)
    rank = Column(String(length=10, collation='utf8'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'))
    authority = Column(String(length=10, collation='utf8'), nullable=False)

    unit = relationship("Unit", back_populates="user")

# https://app.quickdatabasediagrams.com/#/d/q2wtwj
