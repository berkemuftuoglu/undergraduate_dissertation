class GameError(Exception):
    NO_PLAYERS = "Players must be defined with 'role/1'"
    NO_SUCH_PLAYER = "No such player: '%s'"
    DOUBLE_MOVE = "'%s' has already moved this turn"
    ILLEGAL_MOVE = "Not a legal move: '(does %s %s)'"
    NO_TRUE_ALLOWED = "'true' facts are not allowed.  Use 'init/1' instead."
    NO_MOVES = 'The following players have not moved: %s.'
