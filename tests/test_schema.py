import pytest

from canopy.canopy import Canopy, List, Is, SchemaParseException

schema = int
cases = [
    (schema, 1, 1),
    (schema, "1", 1),
    (schema, "1.1", SchemaParseException),
]

schema = Is(int)
cases += [
    (schema, "1", "1"),
]

schema = {"a": int}
cases += [
    (schema, {"a": 1}, {"a": 1}),
    (schema, {"a": 1, "b": 1}, {"a": 1}),
    (schema, {"a": "hello"}, SchemaParseException),
]

schema = {"a": {"b": {"c": None}}}
cases += [
    (schema, {"a": {"b": {"c": "hello"}}}, {"a": {"b": {"c": "hello"}}}),
    (schema, {"a": {"b": {"c": "hello", "d": "there"}}}, {"a": {"b": {"c": "hello"}}}),
    (schema, {"a": "b"}, SchemaParseException),
]

schema = List({"a": int})
cases += [
    (schema, [], []),
    (schema, [{"a": 1}], [{"a": 1}]),
    (schema, [{"a": 1}, {"a": 2}], [{"a": 1}, {"a": 2}]),
    (schema, {"a": 1}, SchemaParseException),
]


@pytest.mark.parametrize("schema,input_data,output", cases)
def test_schema(schema, input_data, output):
    s = Canopy(schema)
    if isinstance(output, type) and issubclass(output, Exception):
        with pytest.raises(output):
            s.parse_or_raise(input_data)
    else:
        assert s.parse_or_raise(input_data) == output
