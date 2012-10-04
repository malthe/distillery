# -*- coding: utf-8 -*-


#  Stores all lazy attributes for counter creation
_lazies = []


def lazy(f):
    """Stores the method creation counter and sets it as a classmethod.
    """
    _lazies.append(f)
    f.counter = len(_lazies)
    return classmethod(f)


class Distillery(object):
    """Base class for ORM dependent distilleries.
    """
    @classmethod
    def create(cls, **kwargs):
        """Inits, populates and saves a object instance.
        """
        instance = cls.init(**kwargs)
        return cls.save(instance)

    @classmethod
    def init(cls, **kwargs):
        """Inits and populate object instance.
        """
        instance = cls.__model__()
        #  kwargs
        for key in kwargs:
           setattr(instance, key, kwargs.get(key))

        def get_counter((k, m)):
            return m.counter if hasattr(m, 'counter') else 0

        #  Class members
        #  Sets basic attributes then lazy ones by creation order
        for key, member in sorted([(k, getattr(cls, k)) for k in cls.__dict__],
                key=get_counter):
            if not key in Distillery.__dict__ and not key.startswith('_') \
                    and not key in kwargs:
                value = member(instance) if callable(member) else member
                setattr(instance, key, value)
        return instance

    @classmethod
    def save(cls, instance):
        """Saves given object instance.
        """
        raise NotImplementedError()


class DjangoDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        instance.save()


class SQLAlchemyDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        cls.__session__.add(instance)
        cls.__session__.commit()
        return instance
