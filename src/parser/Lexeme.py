class Lexeme(object):
    def __init__(self, filename, line, lineno, col=-1, value=''):
        self.value = value
        self.filename = filename
        self.line = line
        self.lineno = lineno
        self.column = col

    @staticmethod
    def new(string):
        token = Lexeme(None, None, None)
        token.set(value=string)
        return token

    def set(self, filename=None, line=None, lineno=None, column=None, value=None):
        if filename:
            self.filename = filename
        if line:
            self.line = line
        if lineno:
            self.lineno = lineno
        if column:
            self.column = column
        if value:
            self.value = value

    def is_empty(self):
        return self.column == -1 or self.value == ''

    def is_rule(self):
        return self.value == '<='

    def is_open(self):
        return self.value == '('

    def is_close(self):
        return self.value == ')'

    def is_not(self):
        return self.value == 'not'

    def is_distinct(self):
        return self.value == 'distinct'

    def is_or(self):
        return self.value == 'or'

    def is_init(self):
        return self.value == 'init'

    def is_true(self):
        return self.value == 'true'

    def is_variable(self):
        return self.value[0] == '?'

    def is_constant(self):
        return self.value[0] not in ('?', '(', ')')

    def copy(self):
        return Lexeme(self.filename, self.line, self.lineno, self.column, self.value)

    def __repr__(self):
        return repr(self.value)
