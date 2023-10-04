import os

# Label Types
LABEL_TYPE_TEXT = 1
LABEL_TYPE_GRAPH = 2

# Constants for known games
GAME_TICTACTOE = 1
GAME_NUMBER_TICTACTOE = 2
GAME_NIM = 3
GAME_SUM_15 = 4
GAME_CONNECT_FOUR = 5
GAME_MINICHESS = 6
GAME_SHEEP_AND_WOLF = 7
GAME_PAWN_WHOPPING = 8

# Information for games. Game constant, Game file name, Game full name
GAMES_GDL = [[GAME_TICTACTOE, "tictactoe", "Tic-Tac-Toe"],
             [GAME_NUMBER_TICTACTOE, "numbertictactoe", "Number TicTacToe"],
             [GAME_NIM, "nim1", "Nim"],
             [GAME_SUM_15, "sum15", "Sum 15"],
             [GAME_CONNECT_FOUR, "connectfour", "Connect 4"],
             [GAME_MINICHESS, "minichess", "Mini Chess"],
             [GAME_SHEEP_AND_WOLF, "sheep_and_wolf", "Sheep and Wolf"],
             [GAME_PAWN_WHOPPING, "pawn_whopping", "Pawn Whopping"]]

# The constant used for unknown games
UNKNOWN_GAME = [0, "unknown", "Unknown Game"]


def findGameByFileName(fileName):
    # Finds and returns the appropriate game with the given file name.
    # If the game cannot be found, it returns the unknown game with correct file name and full name
    if fileName is not None:
        head, tail = os.path.split(fileName)
        gameName = tail.split(".")[0]
        for game in GAMES_GDL:
            if game[1] == gameName:
                return game

        UNKNOWN_GAME[1] = gameName
        UNKNOWN_GAME[2] = gameName
        return UNKNOWN_GAME


def getLabelForState(game, facts, move, labelType):
    # Returns the label of the state information for the given game
    if game == GAME_TICTACTOE:
        return getLabelForTictactoe(facts, labelType)
    elif game == GAME_NIM:
        return getLabelForNim(facts, labelType)
    elif game == GAME_CONNECT_FOUR:
        return getLabelForConnectFour(facts, labelType)
    elif game == GAME_SUM_15:
        return getLabelForSum15(facts, labelType)
    elif game == GAME_NUMBER_TICTACTOE:
        return getLabelForNumberTictactoe(facts, labelType)
    elif game == GAME_MINICHESS:
        return getLabelForMiniChess(facts, labelType)
    elif game == GAME_PAWN_WHOPPING:
        return getLabelForPawnWhopping(facts, labelType)
    elif game == GAME_SHEEP_AND_WOLF:
        return getLabelForSheepAndWolf(facts, labelType)

    return getLabelForNoGame(move, labelType)


def getLabelForNoGame(move, labelType):
    # If the given game is unknown, it returns "Not Implemented" for the text label
    # and returns "move" for the graph label
    if labelType == LABEL_TYPE_TEXT:
        return ["--Not implemented--"]
    elif labelType == LABEL_TYPE_GRAPH:
        if move is not None:
            return move
        else:
            return "---"


def removeParantheses(text):
    return text.replace('(', '').replace(')', '')


def getFactParts(text):
    return removeParantheses(text).split(" ")


def getLabelForTictactoe(facts, labelType):
    matrix = [["" for _ in range(3)] for _ in range(3)]
    for fact in facts:
        parts = getFactParts(fact)
        row = int(parts[1])
        column = int(parts[2])
        val = parts[3]
        matrix[row - 1][column - 1] = val
    lines = []
    resultText = ""
    for i in range(3):
        text = ""
        textR = ""
        for j in range(3):
            v = matrix[i][j]
            if v == "b":
                text += "   "
                textR += "-"
            if v == "x":
                text += " X "
                textR += "X"
            if v == "o":
                text += " O "
                textR += "O"
            if j != 2:
                text += "|"
                textR += "|"
        lines.append(text)
        resultText += textR + "\n"
        if i != 2:
            lines.append("-----------")
    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText


def getLabelForNumberTictactoe(facts, labelType):
    matrix = [["" for _ in range(3)] for _ in range(3)]
    for fact in facts:
        parts = getFactParts(fact)
        row = int(parts[1])
        column = int(parts[2])
        val = parts[3]
        matrix[row - 1][column - 1] = val
    lines = []
    resultText = ""
    for i in range(3):
        text = ""
        textR = ""
        for j in range(3):
            v = matrix[i][j]
            if v == "b":
                text += "   "
                textR += "-"
            else:
                text += " " + v + " "
                textR += v
            if j != 2:
                text += "|"
                textR += "|"
        lines.append(text)
        resultText += textR + "\n"
        if i != 2:
            lines.append("-----------")
    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText


def getLabelForNim(facts, labelType):
    vals = []
    for fact in facts:
        parts = getFactParts(fact)
        val = int(parts[2])
        vals.append(val)
    if labelType == LABEL_TYPE_TEXT:
        maxVal = max(vals)
        lines = []
        for i in range(maxVal):
            text = ""
            for val in vals:
                if val >= maxVal - i:
                    text += " X "
                else:
                    text += "   "
            lines.append(text)
        text = ""
        for _ in vals:
            text += "---"
        lines.append(text)
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        text = ""
        for i in range(len(vals)):
            text += str(vals[i])
            if i != len(vals) - 1:
                text += "-"
        return text


def getLabelForConnectFour(facts, labelType):
    matrix = [["" for _ in range(8)] for _ in range(6)]
    for fact in facts:
        parts = getFactParts(fact)
        if parts[0] == "cell":
            row = int(parts[2])
            column = int(parts[1])
            val = parts[3]
            matrix[6 - row][column - 1] = val
    lines = []
    resultText = ""
    for i in range(6):
        text = "|"
        textR = ""
        for j in range(8):
            v = matrix[i][j]
            if v == "":
                text += " "
                textR += "-"
            if v == "red":
                text += "X"
                textR += "X"
            if v == "black":
                text += "O"
                textR += "O"
            text += "|"
        lines.append(text)
        resultText += textR + "\n"
    lines.append("-----------------")

    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText


def getLabelForSum15(facts, labelType):
    whiteList = []
    blackList = []
    availableList = []
    for fact in facts:
        parts = getFactParts(fact)
        if parts[2] == "white":
            whiteList.append(parts[1])
        elif parts[2] == "black":
            blackList.append(parts[1])
        else:
            availableList.append(parts[1])
    if labelType == LABEL_TYPE_TEXT:
        lines = []
        text = "WHITE : "
        for white in whiteList:
            text += white + " "
        lines.append(text)
        text = "BLACK : "
        for black in blackList:
            text += black + " "
        lines.append(text)
        lines.append("")

        text = "Available : "
        for av in availableList:
            text += av + " "
        lines.append(text)
        return lines
    if labelType == LABEL_TYPE_GRAPH:
        resultText = ""
        resultText += getSum15TextFromList(whiteList) + "\n"
        resultText += getSum15TextFromList(blackList)
        return resultText


def getSum15TextFromList(list):
    if len(list) == 0:
        text = "---"
    else:
        text = "("
        for num in list:
            text += num + " "
        text = text.strip()
        text += ")"
    return text


def getLabelForMiniChess(facts, labelType):
    lines = []
    resultText = ""
    columns = ["a", "b", "c", "d"]
    matrix = [["" for _ in range(4)] for _ in range(4)]
    for fact in facts:
        parts = getFactParts(fact)
        if parts[0] == "cell":
            column = columns.index(parts[1])
            row = int(parts[2]) - 1
            matrix[row][column] = parts[3]
    lines.append("  -----------------")
    for i in range(4):
        row = 3 - i
        text = str(row + 1) + " |"
        textR = ""
        for j in range(4):
            column = j
            val = matrix[row][column]
            if val == "b":
                text += " - "
                textR += "-"
            elif val == "bk":
                text += " k "
                textR += "k"
            elif val == "wk":
                text += " K "
                textR += "K"
            elif val == "wr":
                text += " R "
                textR += "R"
            text += "|"
        lines.append(text)
        lines.append("  -----------------")
        resultText += textR + "\n"
    lines.append("    a   b   c   d")
    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText


def getLabelForPawnWhopping(facts, labelType):
    lines = []
    resultText = ""
    matrix = [["b" for _ in range(8)] for _ in range(8)]
    for fact in facts:
        parts = getFactParts(fact)
        if parts[0] == "cell":
            column = int(parts[1]) - 1
            row = int(parts[2]) - 1
            matrix[row][column] = parts[3]
    for i in range(8):
        row = 7 - i
        text = str(row + 1) + " |"
        textR = ""
        for j in range(8):
            val = matrix[row][j]
            if val == "b":
                text += " - "
                textR += "-"
            elif val == "x":
                text += " X "
                textR += "X"
            elif val == "o":
                text += " O "
                textR += "O"
        lines.append(text)
        resultText += textR + "\n"
    lines.append("  +-----------------------")
    text = "   "
    for i in range(8):
        text += " " + str(i + 1) + " "
    lines.append(text)
    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText


def getLabelForSheepAndWolf(facts, labelType):
    lines = []
    resultText = ""
    matrix = [["b" for _ in range(8)] for _ in range(8)]
    for fact in facts:
        parts = getFactParts(fact)
        if parts[0] == "cell":
            column = int(parts[1][1:]) - 1
            row = int(parts[2][1:]) - 1
            matrix[row][column] = parts[3]
    for i in range(8):
        row = 7 - i
        text = str(row + 1) + " |"
        textR = ""
        for j in range(8):
            val = matrix[row][j]
            if val == "b":
                text += " - "
                textR += "-"
            elif val == "s":
                text += " S "
                textR += "S"
            elif val == "w":
                text += " W "
                textR += "W"
        lines.append(text)
        resultText += textR + "\n"
    lines.append("  +-----------------------")
    text = "   "
    for i in range(8):
        text += " " + str(i + 1) + " "
    lines.append(text)
    if labelType == LABEL_TYPE_TEXT:
        return lines
    elif labelType == LABEL_TYPE_GRAPH:
        return resultText
