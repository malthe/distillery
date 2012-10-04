Distillery
==========

``distillery`` is another `fatory_girl <https://github.com/thoughtbot/factory_girl>`_ like for python ORMs.


Installation
------------

``pip install distillery``


Defining distilleries
---------------------

Each distillery has a ``__model__`` and a set of attributes and methods. The ``__model__`` is the ORM model class from which instance will be produced::

    class UserDistillery(MyOrmDistillery):
        __model__ = User


Attributes
~~~~~~~~~~

A distillery class attribute defines default values for specific model field::

    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

All new ``User`` outputted from ``UserDistillery`` will have ``defaultusername`` as ``username`` field value while there's no override.


Methods (a.k.a. "lazy attributes")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A distillery class method allow to build dinamic value for specific field::

    from distillery import lazy


    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

        @lazy
        def email_address(cls, instance):
            return "%s@%s" % (instance.username, instance.company.domain)

All new ``User`` outputted from ``UserDistillery`` will have an ``email_address`` computed from his username and his company domain.


Using distileries
-----------------


Distillery.init()
~~~~~~~~~~~~~~~~~

Inits and populates an instance::

    user = UserDistillery.init()
    assert user.username == "defaultusername"
    assert user.id is None

    user = UserDistillery.create(username="overriddenusername")
    assert user.username == "overriddenusername"
    assert user.id is None


Distillery.create()
~~~~~~~~~~~~~~~~~~~

Inits, populates and persists an instance::

    user = UserDistillery.create()
    assert user.username == "defaultusername"
    assert user.id is not None


ORMs
----

Actually, ``distillery`` only supports SQLAlchemy models::

    from distillery import SQLAlchemyDistillery


    class MyDistillery(SQLAlchemyDistillery):
        #  ...
