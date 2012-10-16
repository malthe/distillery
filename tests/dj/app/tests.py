# -*- coding: utf-8 -*-
from django.utils.unittest import TestCase

from distillery import lazy, DjangoDistillery
from ...base import DistillerySuite, SetSuite, CompanySet, UserSet

from models import Company, User


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        CompanySet.__distillery__ = cls.CompanyDistillery
        UserSet.__distillery__ = cls.UserDistillery

    def setUp(self):
        super(BaseTestCase, self).setUp()
        Company.objects.all().delete()
        User.objects.all().delete()

    class CompanyDistillery(DjangoDistillery):
        __model__ = Company

    class UserDistillery(DjangoDistillery):
        __model__ = User

        username = "defaultuser"

        @lazy
        def email_address(cls, instance, sequence):
            return "%s@domain.tld" % instance.username

        @lazy
        def index(cls, instance, sequence):
            return sequence

        @lazy
        def company(cls, instance, sequence):
            return BaseTestCase\
                .CompanyDistillery.create(name="%s's company" % \
                    instance.username)


class DistilleryTest(BaseTestCase, DistillerySuite):
    pass


class SetTest(BaseTestCase, SetSuite):
    pass
