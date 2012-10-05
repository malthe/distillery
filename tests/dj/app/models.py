# -*- coding: utf-8 -*-
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=80, unique=True)


class User(models.Model):
    username = models.CharField(max_length=80, unique=True)
    email_address = models.CharField(max_length=80)
    index = models.IntegerField(unique=True)

    company = models.ForeignKey('Company', null=True, blank=True)
