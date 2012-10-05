# -*- coding: utf-8 -*-


class Suite():
    def test_init_simple_attribute(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.username, 'defaultuser')

    def test_init_lazy_attribute(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.email_address, 'defaultuser@domain.tld')

    def test_init_relationship(self):
        user = self.UserDistillery.init()
        self.assertEqual(user.company.name, 'My company')

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
