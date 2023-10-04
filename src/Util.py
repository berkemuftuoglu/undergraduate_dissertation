import os
from os.path import dirname as up

# GDL Keywords
GDL_NO_MOVE = "no_move"
GDL_CONTROL = "control"
GDL_TRUE = "true"
GDL_INIT = "init"

MOVES_TREE_FILE_NAME = "moves_tree"

# Constant for no depth limit
NO_LIMIT = -1

GDL_EXTENSION = "gdl"

BASE_FOLDER = up(__file__)
GAME_FOLDER = os.path.join(BASE_FOLDER, "games")
RESULT_FOLDER = os.path.join(BASE_FOLDER, "results")


def createFoldersWithCheck():
    # Creates games and results folders if they don't exist
    folderList = [GAME_FOLDER, RESULT_FOLDER]
    for folder in folderList:
        if (not os.path.exists(folder)):
            os.mkdir(folder)


def getFullFileNameForGame(fileName):
    return os.path.join(GAME_FOLDER, fileName + "." + GDL_EXTENSION)


def getStateFactsByKey(state, keyName):
    # Returns info from state.db.facts
    keys = list(state.db.facts.keys())
    for key in keys:
        if key[0] == keyName:
            return state.db.facts[key]


def getPlayers(state, playerNames):
    # Returns player names, taking into account whose turn it is
    facts = getStateFactsByKey(state, GDL_TRUE)
    firstPlayer = getControlByFacts(facts)
    secondPlayer = playerNames[(playerNames.index(firstPlayer) + 1) % 2]
    return firstPlayer, secondPlayer


def getPlayerNames(state):
    # Returns player names,using facts from game's initial state
    playerNames = list(state.players)
    facts = getStateFactsByKey(state, GDL_INIT)
    firstPlayer = getControlByFacts(facts)
    secondPlayer = playerNames[(playerNames.index(firstPlayer) + 1) % 2]
    return [firstPlayer, secondPlayer]


def getControlByFacts(facts):
    # Returns whose turn it is
    for fact in facts:
        for v in fact:
            if v.token.value == GDL_CONTROL:
                return str(v.children[0])


def getNotControlByFacts(state):
    # Returns all facts except the Control type in the TRUE field of the State object
    facts = getStateFactsByKey(state, GDL_TRUE)
    stateFacts = []
    for fact in facts:
        for v in fact:
            if v.token.value != GDL_CONTROL:
                stateFacts.append(str(v))
    stateFacts.sort()
    return stateFacts


def getScoreForPlayer(stateMachine, player):
    return stateMachine.score(player)


def getWinner(stateMachine, playerNames):
    # Returns the winning player. Returns 1 when player 1 wins, 2 when player 2 wins, 0 otherwise
    scores = []
    for player in playerNames:
        scores.append(getScoreForPlayer(stateMachine, player))
    if scores[0] > scores[1]:
        return 1
    elif scores[0] < scores[1]:
        return 2
    else:
        return 0


def getWinnerStr(stateMachine, playerNames):
    # Returns win status textually
    win = getWinner(stateMachine, playerNames)
    if win == 0:
        return "It's a tie."
    elif win == 1:
        return playerNames[0] + " wins."
    elif win == 2:
        return playerNames[1] + " wins."


def getLegalMoves(state, playerNames):
    # Returns the legal moves that the player currently in turn can play
    p1, p2 = getPlayers(state, playerNames)
    legalMoves = getLegalMovesForPlayer(state, p1)
    return legalMoves, p1


def getLegalMovesForPlayer(state, player):
    # Returns the legal moves for the given player
    legalMoves = state.legal()
    if player in legalMoves:
        moves = legalMoves[player]
        moves.sort()
        return moves
    return []
