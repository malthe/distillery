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

    def test_init_callable_kwarg(self):
        company = self.CompanyDistillery.init(name=lambda i: "My company")
        self.assertEqual(company.name, "My company")

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

    def test_after_create(self):
        class NewUserDistillery(self.UserDistillery):
            @classmethod
            def _after_create(cls, instance):
                instance.username = "newusername"

        user = NewUserDistillery.create()
        self.assertEqual(user.username, "newusername")

    def test_bulk_insert_format(self):
        users = self.UserDistillery.bulk(10, username='user_%(i)s')
        self.assertEqual(len(users), 10)
        self.assertEqual(users[0].username, 'user_0')
        self.assertEqual(users[6].username, 'user_6')

    def test_bulk_insert_default(self):
        users = self.UserDistillery.bulk(1)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'defaultuser')

    def test_bulk_insert_non_string(self):
        company = self.CompanyDistillery.create(name='another company')
        users = self.UserDistillery.bulk(1, company=company)
        self.assertEqual(users[0].company, company)


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
            user = lambda s: self.UserDistillery.create(username="user")

        users = NewUserSet()
        self.assertEqual(users.admin.username, 'admin')
        self.assertEqual(users.user.username, 'user')

    def test_set_callable_member_invalid_type(self):
        class NewUserSet(UserSet):
            invalid = lambda s: 'invalid type'

        self.assertRaises(NewUserSet)

    def test_embedded_set(self):
        class Super(Set):
            Users = UserSet

        self.assertEqual(Super().Users.jeanphix.username, 'jeanphix')

    def test_after_create(self):
        class NewUserSet(UserSet):
            class admin:
                username = 'admin'

                @classmethod
                def _after_create(cls, instance):
                    instance.username = 'modified'

        self.assertEqual(NewUserSet().admin.username, 'modified')

    def test_set_fixture_callable_member(self):
        class NewUserSet(UserSet):
            class admin:
                username = 'admin'
                company = classmethod(lambda c: CompanySet.my_company)

        self.assertEqual(NewUserSet().admin.company.name, 'My company')
