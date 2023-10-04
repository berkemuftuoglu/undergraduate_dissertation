import re

from src.parser.Lexeme import *
from src.parser.error.NoInputError import *


class Lexer(object):
    def __init__(self):
        self.values = []
        self.wsre = re.compile(r'\s')

    @staticmethod
    def run_lex(data=None, file=None, tokens=None):
        if tokens is None:
            return Lexer().lex(data, file)
        else:
            return tokens

    def lex(self, data=None, file=None):
        if file is None:
            if data is None:
                raise NoInputError('no input to valueize')
            self.lines = data.splitlines(True)
            self.filename = None
        else:
            self.lines = file
            self.filename = file.name

        return self._lex_input()

    def _lex_input(self):
        row = 0
        for line in self.lines:
            row += 1
            self._lex_line(line, row)

        if self.values[-1].is_empty():
            self.values.pop()
        return self.values

    def _lex_line(self, line, row):
        col = 0
        for char in line:
            col += 1
            if char == ';':
                break
            self._process_char(char.lower(), line, row, col)

    def _process_char(self, char, line, row, col):
        last_value = self.values[-1] if self.values else None
        if self._is_whitespace(char):
            if last_value is None or not last_value.is_empty():
                self.values.append(Lexeme(self.filename, line, row))
        elif char == '(' or char == ')':
            if last_value is not None and last_value.is_empty():
                last_value.set(value=char, line=line, lineno=row, column=col)
            else:
                self.values.append(Lexeme(self.filename, line, row, col, char))
            self.values.append(Lexeme(self.filename, line, row))
        else:
            if last_value is None:
                last_value = Lexeme(self.filename, line, row, col)
                self.values.append(last_value)
            if last_value.is_empty():
                last_value.set(line=line, lineno=row, column=col)
            last_value.value += char

    def _is_whitespace(self, char):
        return re.match(self.wsre, char) is not None
