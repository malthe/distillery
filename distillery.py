# -*- coding: utf-8 -*-
import weakref


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
        cls._sequence = cls.get_next_sequence()
        def set(instance, attr, value):
            if not hasattr(instance, attr):
                raise AttributeError("`%s` has no attribute `%s`." \
                    % (instance.__class__.__name__, attr))
            setattr(instance, attr, value)

        instance = cls.__model__()
        #  kwargs
        for key in kwargs:
            set(instance, key, kwargs.get(key))

        def get_counter((k, m)):
            return m.counter if hasattr(m, 'counter') else 0

        #  Class members
        #  Sets basic attributes then lazy ones by creation order
        for key, member in sorted([(k, getattr(cls, k)) for k in dir(cls)],
                key=get_counter):
            if not key in Distillery.__dict__ and not key.startswith('_') \
                    and not key in kwargs:
                if callable(member):
                    value = member(instance, cls._sequence)
                else:
                    value = member
                set(instance, key, value)
        return instance

    @classmethod
    def save(cls, instance):
        """Saves given object instance.
        """
        raise NotImplementedError()

    @classmethod
    def get_next_sequence(cls):
        if not hasattr(cls, '_sequence'):
            return 0
        return cls._sequence + 1


class SetMeta(type):
    """Adds a `_set_class` property to all fixtures class in a set.
    """
    def __new__(meta, name, bases, dict_):
        new = type.__new__(meta, name, bases, dict_)
        for key in dict_:
            if not key.startswith('_'):
                setattr(getattr(new, key), '_set_class', new)
        return new


class Set(object):
    """Fixtures dataset.
    """
    __metaclass__ = SetMeta
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if Set._instances.get(cls):
            raise Exception("Can't create more than one `%s` instance." \
                % cls)
        new = super(Set, cls).__new__(cls, *args, **kwargs)
        Set._instances[cls] = weakref.ref(new)
        return new

    def __init__(self):
        if not hasattr(self, '__distillery__'):
            raise AttributeError('A Set must have a `__distillery__` member.')
        self._fixtures = {}

    def __getattribute__(self, attr):
        if attr.startswith('_'):
            return super(Set, self).__getattribute__(attr)
        elif not attr in dir(self):
            raise AttributeError('Invalid fixture `%s`.' % attr)
        elif not attr in self._fixtures:
            fixture = super(Set, self).__getattribute__(attr)
            kwargs = {}
            for key in dir(fixture):
                if not key.startswith('_'):
                    member = getattr(fixture, key)
                    if hasattr(member, '_set_class'):
                        member = getattr(member._set_class._get_instance(),
                            member.__name__)
                    kwargs[key] = member
            self._fixtures[attr] = self.__distillery__.create(**kwargs)
        return self._fixtures[attr]

    def __del__(self):
        del Set._instances[self.__class__]

    @classmethod
    def _get_instance(cls):
        if cls in Set._instances:
            return Set._instances[cls]()
        return cls()


class DjangoDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        instance.save()
        return instance


class SQLAlchemyDistillery(Distillery):
    @classmethod
    def save(cls, instance):
        cls.__session__.add(instance)
        cls.__session__.commit()
        return instance
