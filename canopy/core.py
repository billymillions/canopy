from abc import ABC
from functools import reduce
from .error import SchemaConstructionException, SchemaParseException, ParseError, CheckFailed


class CanopySchema(ABC):
    def parse(self, data):
        pass


def Canopy(schema_like):
    return Root(_prepare_schema(schema_like))


def _prepare_schema(schema_like):
    if isinstance(schema_like, CanopySchema):
        return schema_like
    if isinstance(schema_like, dict):
        return Object(_prepare_object(schema_like))
    if callable(schema_like):
        return As(schema_like)
    if type(schema_like) in (list, tuple, set):
        return And(*schema_like)
    if schema_like is None:
        return Anything()
    raise SchemaConstructionException()


def _prepare_object(obj):
    try:
        return {k: _prepare_schema(v) for k, v in obj.items()}
    except (TypeError, AttributeError, ValueError) as e:
        raise SchemaConstructionException() from e


def _prepare_list(lst):
    try:
        assert type(lst) in (list, tuple, set)
        return [_prepare_schema(v) for v in lst]
    except (TypeError, AttributeError, ValueError, AssertionError) as e:
        raise SchemaConstructionException() from e


class Root(CanopySchema):
    def __init__(self, inner):
        self._inner = inner

    def parse(self, data):
        return self._inner.parse(data)

    def parse_or_raise(self, data):
        val, errors = self.parse(data)
        if errors:
            raise SchemaParseException(errors)
        return val


class Object(CanopySchema):
    def __init__(self, schema_dictionary):
        self._schema_dictionary = schema_dictionary

    def parse(self, data):
        result = {}
        errors = []
        for (k, v) in self._schema_dictionary.items():
            try:
                r, es = v.parse(data[k])
                errors.extend([ParseError(k, e) for e in es])
                result[k] = r
            except (AttributeError, TypeError, ValueError, KeyError) as e:
                errors += [ParseError(k, e)]
        return result, errors


class List(CanopySchema):
    def __init__(self, item_schema):
        self._item_schema = _prepare_schema(item_schema)

    def parse(self, data):
        try:
            iterable = iter(data)
        except TypeError as e:
            return None, [e]

        errors = []
        result = []
        for (i, v) in enumerate(iterable):
            r, es = self._item_schema.parse(v)
            result.append(r)
            errors.extend([ParseError(i, e) for e in es])
        return result, errors


class And(CanopySchema):
    def __init__(self, *schema_list):
        self._schema_list = schema_list

    def parse(self, data):
        def one_pass(s, v, errors):
            v, new_errors = s.parse(v)
            errors += new_errors
        return reduce(lambda result, s: one_pass(s, result[0], result[1]), self._schema_list, (data, []))


class Or(CanopySchema):
    def __init__(self, *schema_list):
        self._schema_list = schema_list

    def parse(self, value):
        v = value
        for s in self._schema_list:
            v, errors = s.parse(v)
            if len(errors) == 0:
                return v, []
        return v, errors


class As(CanopySchema):
    def __init__(self, fn):
        self._fn = fn

    def parse(self, value):
        try:
            return self._fn(value), []
        except Exception as e:
            return None, [e]


class Is(CanopySchema):
    def __init__(self, fn):
        self._fn = fn

    def parse(self, value):
        try:
            if self._fn(value):
                return value, []
            else:
                return value, [CheckFailed(self._fn, value)]
        except Exception as e:
            return value, [e]


def Anything():
    return Is(lambda x: True)
