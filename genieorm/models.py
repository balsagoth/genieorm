import json

from genieorm.utils import dict_from_path, join_path


class Field(object):
    def __init__(self, key, proxy_class=lambda x: x):
        self.proxy_class = proxy_class
        self.key = key

    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
        # grab the original value before we proxy
        value = instance.__dict__[self.field_name]
        return value

    def __set__(self, instance, value):
        self.fullpath = join_path(instance._fullpath, self.key)
        v = dict_from_path(value, self.key)
        # save it on instance
        instance.__dict__[self.field_name] = self.proxy_class(v)

    @property
    def path(self):
        return self.key

    def __getattr__(self, attr):
        return getattr(self.proxy_class, attr)


class EmbedField(Field):
    def __set__(self, instance, value):
        self.fullpath = join_path(instance._fullpath, self.path)
        v = dict_from_path(value, self.key)
        instance.__dict__[self.field_name] = self.proxy_class(v, fullpath=self.fullpath)


class ListField(Field):

    def __set__(self, instance, value):
        self.fullpath = join_path(instance._fullpath, self.path)
        inner_dct = dict_from_path(value, self.path)
        result = [
            self.proxy_class(inner_dct[k], fullpath=join_path(self.fullpath, k))
            for k in filter(lambda x: not x.startswith("_"), inner_dct.keys())]
        instance.__dict__[self.field_name] = result


class FieldMeta(type):
    def __new__(cls, name, bases, attrs):
        # find all descriptors, auto-set their labels
        for n, v in attrs.items():
            if isinstance(v, Field):
                v.field_name = n
        return super(FieldMeta, cls).__new__(cls, name, bases, attrs)


class Model(object):

    __metaclass__ = FieldMeta

    def __init__(self, dct, fullpath=""):
        self._fullpath = fullpath
        for k, v in type(self).__dict__.iteritems():
            if isinstance(v, Field):
                setattr(self, k, dct)

    @classmethod
    def get_path(klass, path):
        key = ""
        for p in path.split('.'):
            key = join_path(key, getattr(klass, p).path)
            klass = getattr(klass, p)
        return key

    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    def to_json(self):
        return json.dumps(self, cls=GenieEncoder)


class GenieEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)
