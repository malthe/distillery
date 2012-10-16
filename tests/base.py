# -*- coding: utf-8 -*-
from distillery import Set


class CompanySet(Set):
    class my_company:
        name = 'My company'


class UserSet(Set):
    class jeanphix:
        username = 'jeanphix'
        company = CompanySet.my_company


class DistillerySuite():
    def test_init_simple_attribute(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.username, 'defaultuser')

    def test_init_lazy_attribute(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.email_address, 'defaultuser@domain.tld')

    def test_init_relationship(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.company.name, "defaultuser's company")

    def test_init_override_simple_attribute(self):
        user = self.UserDistillery.init(username='myuser')
        self.assertEqual(user.username, 'myuser')

    def test_init_override_lazy_attribute(self):
        user = self.UserDistillery.init(
            email_address='myuser@another-domain.tld')
        self.assertEqual(user.email_address, 'myuser@another-domain.tld')

    def test_init_override_relationship(self):
        company = self.CompanyDistillery.init(name="Another company")
        user = self.UserDistillery.init(company=company)
        self.assertEqual(user.company.name, 'Another company')

    def test_create(self):
        user = self.UserDistillery.create()
        self.assertTrue(user.id is not None)

    def test_save(self):
        user = self.UserDistillery.init()
        self.assertTrue(user.id is None)
        self.UserDistillery.save(user)
        self.assertTrue(user.id is not None)

    def test_invalid_attribute(self):
        self.UserDistillery.wrong = 'invalid attribute'
        self.assertRaises(AttributeError, self.UserDistillery.init)
        del self.UserDistillery.wrong

    def test_sequence(self):
        user1 = self.UserDistillery.init(company=None)
        user2 = self.UserDistillery.init(username="anotheruser")
        self.assertEqual(user1.index + 1, user2.index)


class SetSuite():
    @classmethod
    def setUpClass(cls):
        CompanySet.__distillery__ = cls.CompanyDistillery
        UserSet.__distillery__ = cls.UserDistillery

    def test_cant_be_instanciate_twice(self):
        UserSet()
        self.assertRaises(Exception, UserSet)

    def test_does_not_duplicate_fixture_instance(self):
        user_set = UserSet()
        self.assertEqual(user_set.jeanphix.id, user_set.jeanphix.id)

    def test_simple_attribute_override(self):
        user_set = UserSet()
        self.assertEqual(user_set.jeanphix.username, 'jeanphix')

    def test_foreign_set_fixture(self):
        user_set = UserSet()
        self.assertEqual(user_set.jeanphix.company.name,
            "My company")

    def test_foreign_set_already_instanciate_fixture(self):
        company_set = CompanySet()
        my_company = company_set.my_company
        user_set = UserSet()
        self.assertEqual(user_set.jeanphix.company.id,
            my_company.id)

    def test_set_callable_member(self):
        class NewUserSet(UserSet):
            admin = lambda s: self.UserDistillery.create(username="admin")

        self.assertEqual(NewUserSet().admin.username, 'admin')
