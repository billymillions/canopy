

class SchemaConstructionException(Exception):
    def __init__(self, claz):
        self.cls = claz


class SchemaParseException(Exception):
    def __init__(self, errors):
        self.errors = errors


class ParseError(object):
    def __init__(self, path, inner):
        self.path = path
        self.inner = inner


class CheckFailed(object):
    def __init__(self, check_fn, failed_value):
        self.check_fn = check_fn
        self.failed_value = failed_value
