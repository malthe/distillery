# -*- coding: utf-8 -*-
from django.utils.unittest import TestCase

from distillery import lazy, DjangoDistillery
from ...base import Suite, CompanySet, UserSet

from models import Company, User


class DjangoDistilleryTest(TestCase, Suite):
    @classmethod
    def setUpClass(cls):
        super(DjangoDistilleryTest, cls).setUpClass()
        CompanySet.__distillery__ = cls.CompanyDistillery
        UserSet.__distillery__ = cls.UserDistillery

    def setUp(self):
        super(DjangoDistilleryTest, self).setUp()
        Company.objects.all().delete()
        User.objects.all().delete()

    class CompanyDistillery(DjangoDistillery):
        __model__ = Company

    class UserDistillery(DjangoDistillery):
        __model__ = User

        username = "defaultuser"

        @lazy
        def email_address(cls, instance):
            return "%s@domain.tld" % instance.username

        @lazy
        def company(cls, instance):
            return DjangoDistilleryTest\
                .CompanyDistillery.create(name="My company")
