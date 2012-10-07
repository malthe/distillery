# -*- coding: utf-8 -*-
import unittest

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from distillery import lazy, SQLAlchemyDistillery

from base import DistillerySuite, SetSuite, CompanySet, UserSet


engine = create_engine('sqlite://', echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
Base = declarative_base()


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email_address = Column(String(80), unique=True, nullable=False)
    index = Column(Integer, unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey(Company.id))

    company = relationship(Company)


class BaseTestCase(unittest.TestCase):
    class CompanyDistillery(SQLAlchemyDistillery):
        __session__ = session
        __model__ = Company

    class UserDistillery(SQLAlchemyDistillery):
        __session__ = session
        __model__ = User

        username = "defaultuser"

        @lazy
        def email_address(cls, instance, sequence):
            return "%s@domain.tld" % instance.username

        @lazy
        def company(cls, instance, sequence):
            return BaseTestCase\
                .CompanyDistillery.create(name="My company")

        @lazy
        def index(cls, instance, sequence):
            return sequence

    @classmethod
    def setUpClass(cls):
        CompanySet.__distillery__ = cls.CompanyDistillery
        UserSet.__distillery__ = cls.UserDistillery

    def setUp(self):
        Base.metadata.create_all(engine)

    def tearDown(self):
        session.rollback()
        Base.metadata.drop_all(engine)


class DistilleryTest(DistillerySuite, BaseTestCase):
    pass


class SetTest(SetSuite, BaseTestCase):
    pass


if __name__ == '__main__':
    unittest.main()
