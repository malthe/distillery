# -*- coding: utf-8 -*-
import unittest

from distillery import lazy, SQLAlchemyDistillery

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


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
    company_id = Column(Integer, ForeignKey(Company.id))

    company = relationship(Company)


class CompanyDistillery(SQLAlchemyDistillery):
    __session__ = session
    __model__ = Company


class UserDistillery(SQLAlchemyDistillery):
    __session__ = session
    __model__ = User

    username = "defaultuser"

    @lazy
    def email_address(cls, instance):
        return "%s@domain.tld" % instance.username

    @lazy
    def company(cls, instance):
        return CompanyDistillery.create(name="My company")


class SQLAlchemyDistilleryTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)
        #session.remove()

    def test_init_simple_attribute(self):
        user = UserDistillery.init()
        self.assertEqual(user.username, 'defaultuser')

    def test_init_lazy_attribute(self):
        user = UserDistillery.init()
        self.assertEqual(user.email_address, 'defaultuser@domain.tld')

    def test_init_relationship(self):
        user = UserDistillery.init()
        self.assertEqual(user.company.name, 'My company')

    def test_init_override_simple_attribute(self):
        user = UserDistillery.init(username='myuser')
        self.assertEqual(user.username, 'myuser')

    def test_init_override_lazy_attribute(self):
        user = UserDistillery.init(email_address='myuser@another-domain.tld')
        self.assertEqual(user.email_address, 'myuser@another-domain.tld')

    def test_init_override_relationship(self):
        company = CompanyDistillery.init(name="Another company")
        user = UserDistillery.init(company=company)
        self.assertEqual(user.company.name, 'Another company')

    def test_create(self):
        user = UserDistillery.create()
        self.assertTrue(user.id is not None)

    def test_save(self):
        user = UserDistillery.init()
        self.assertTrue(user.id is None)
        UserDistillery.save(user)
        self.assertTrue(user.id is not None)


if __name__ == '__main__':
    unittest.main()
