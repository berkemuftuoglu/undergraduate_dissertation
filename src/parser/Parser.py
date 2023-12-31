from src.parser.ASTNode import *
from src.parser.error.ParseError import *


class Parser(object):
    RESERVED = {
        'base': 1,
        'distinct': 2,
        'does': 2,
        'goal': 2,
        'init': 1,
        'input': 2,
        'legal': 2,
        'next': 1,
        'not': 1,
        'or': [2, 3, 4, 5, 6, 7, 8, 9],
        'role': 1,
        'terminal': 0,
        'true': 1,
    }

    def __init__(self):
        self.head = ASTNode()

    @staticmethod
    def run_parse(tokens):
        return Parser().parse(tokens)

    def parse(self, tokens):
        new_sentence = False
        curr = self.head
        parents = []
        for token in tokens:
            if new_sentence:
                if not token.is_constant():
                    raise ParseError(GDLError.EXPECTED_CONSTANT, token)
                parents.append(curr)
                curr = curr.create_child(token)
                if curr.is_not() and parents and parents[-1].is_not():
                    raise ParseError(GDLError.DOUBLE_NOT, token)
                new_sentence = False
            elif token.is_open():
                new_sentence = True
            elif token.is_close():
                try:
                    popped = parents.pop()
                except IndexError:
                    raise ParseError(GDLError.UNEXPECTED_CLOSE, token)
                self._validate_node(curr)
                curr = popped
            else:
                curr.create_child(token)
        if parents:
            raise ParseError(GDLError.MISSING_CLOSE, tokens[-1])
        return self.head.children

    def _validate_node(self, node):
        if type(self.RESERVED.get(node.term, node.arity)) == int:
            if self.RESERVED.get(node.term, node.arity) != node.arity:
                raise ParseError(GDLError.BAD_PREDICATE % node.predicate, node.token)
        elif type(self.RESERVED.get(node.term, node.arity)) == list:
            if node.arity not in self.RESERVED.get(node.term, node.arity):
                raise ParseError(GDLError.BAD_PREDICATE % node.predicate, node.token)
