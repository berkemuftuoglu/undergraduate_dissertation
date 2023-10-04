import datetime
from time import time

import networkx as nx

from src.Util import *
from src.tree.GameLabels import *
from src.tree.TreeState import *


class TreeGenerator:
    # The TreeGenerator class is responsible for generating a game tree of the desired size starting from the given state

    def __init__(self, state, game=UNKNOWN_GAME, moveDepth=1, treeNodeLimit=100, movesTree=False):
        self.stateMachine = state  # Starting state
        self.game = game
        self.moveDepth = moveDepth
        self.treeNodeLimit = treeNodeLimit
        self.movesTree = movesTree  # Boolean variable that determines whether the tree is a regular tree or a move tree
        self.fileName = self.game[1]
        self.fileNamePng = ""
        self.fileNameDot = ""
        self.fileNameMl = ""

        self.gameTreeML = None
        self.gameTreeDot = None
        self.id_counter = None
        self.numNodes = None
        self.elapsedTime = None
        self.maxDepth = 0  # It is calculated and returned as the final result
        self.reset()

    def reset(self):
        self.id_counter = 1
        self.gameTreeDot = self.newTree()
        self.gameTreeML = self.newTree()
        self.numNodes = None
        self.elapsedTime = None
        self.maxDepth = 0

    def generate(self):
        # This method is used for generating a regular tree (not move tree)
        # Graphs are created for dot and graphml formats
        self.reset()
        startTime = time()
        playerNames = getPlayerNames(self.stateMachine)
        firstTreeState = self.generateTreeState(self.stateMachine, None, 0, playerNames)
        treeStateQueue = [firstTreeState]

        while treeStateQueue:
            currentTreeState = treeStateQueue.pop(0)
            self.addStateToTrees(currentTreeState)
            currentState = currentTreeState.state
            if currentState.is_terminal():
                continue
            p1, p2 = getPlayers(currentState, playerNames)
            if self.moveDepth == NO_LIMIT or currentTreeState.depth < self.moveDepth:
                legalMovesP1 = getLegalMovesForPlayer(currentState, p1)
                for move in legalMovesP1:
                    if self.id_counter > self.treeNodeLimit:
                        continue
                    currentState.move(p1, move)
                    legalMovesP2 = getLegalMovesForPlayer(currentState, p2)
                    currentState.move(p2, legalMovesP2[0])
                    nextState = currentState.next()
                    nextTreeState = self.generateTreeState(nextState, move, currentTreeState.depth + 1, playerNames)
                    treeStateQueue.append(nextTreeState)
                    self.gameTreeDot.add_edge(currentTreeState.id, nextTreeState.id)
                    self.gameTreeML.add_edge(currentTreeState.id, nextTreeState.id)
        self.elapsedTime = time() - startTime
        self.numNodes = self.id_counter

    def generateWithMoves(self, moveList):
        # This method is used for generating a move tree
        # Graphs are created for dot and graphml formats
        # Starting from the initial state, each move in the move list is added to the tree one by one
        self.reset()
        playerNames = getPlayerNames(self.stateMachine)
        currentState = self.stateMachine
        currentTreeState = self.generateTreeState(self.stateMachine, None, 0, playerNames)
        self.addStateToTrees(currentTreeState)
        for move in moveList:
            if move == GDL_NO_MOVE:
                continue
            p1, p2 = getPlayers(currentState, playerNames)
            firstParIndex = move.index("(")
            move = move[firstParIndex:]
            currentState.move(p1, move)
            legalMovesP2 = getLegalMovesForPlayer(currentState, p2)
            currentState.move(p2, legalMovesP2[0])
            nextState = currentState.next()
            nextTreeState = self.generateTreeState(nextState, move, currentTreeState.depth + 1, playerNames)
            self.addStateToTrees(nextTreeState)
            self.gameTreeDot.add_edge(currentTreeState.id, nextTreeState.id)
            self.gameTreeML.add_edge(currentTreeState.id, nextTreeState.id)
            currentState = nextState
            currentTreeState = nextTreeState

    def newTree(self):
        # Creates and returns a new tree
        return nx.DiGraph(directed=True)

    def generateTreeState(self, state, move, depth, playerNames):
        # Creates a TreeState object using the given state and other information
        facts = None
        if self.game[0] != 0:  # If self.game is a known game
            facts = getNotControlByFacts(state)
        graphLabel = getLabelForState(self.game[0], facts, move, LABEL_TYPE_GRAPH)
        isTerminal = state.is_terminal()
        winner = 0
        if isTerminal:
            winner = getWinner(state, playerNames)
        id = self.id_counter
        self.id_counter += 1
        return TreeState(state, id, depth, graphLabel, isTerminal, winner)

    def addStateToTrees(self, s):
        # Adds the TreeState object to the dot and graphML trees
        # When adding to the dot tree, determines the color variable using the winner and terminal information
        if s.winner == 1:
            color = "#BA545D"
        elif s.winner == 2:
            color = "#0570B0"
        elif s.isTerminal:
            color = "#CCCCCC"
        else:
            color = "#FFF2AE"
        self.gameTreeDot.add_node(s.id, id=s.id, fontname="Courier-bold", fontsize=15,
                                  shape="square", label=s.graphLabel, color=color, style="filled")

        # When adding to the GraphML tree, determines the stateType variable using the winner and terminal information
        stateType = 0
        if s.isTerminal:
            stateType = 3
        if s.winner > 0:
            stateType = s.winner

        if s.depth > self.maxDepth:
            self.maxDepth = s.depth

        self.gameTreeML.add_node(s.id, name=s.graphLabel, stateType=stateType)

    def createFiles(self):
        # Converts the dot and GraphML trees into the appropriate formats and saves them as files
        # Additionally, it converts the object in the dot format into an image and saves it as a PNG file
        
        if self.gameTreeDot.number_of_nodes() == 0:
            print("No states!")
            return

        if not self.movesTree:
            time = datetime.datetime.now()
            fileName = time.strftime("%Y%m%d_%H%M%S") + "_" + self.fileName

            if self.moveDepth != NO_LIMIT and self.moveDepth is not None:
                fileName += "_" + str(self.moveDepth)
        else:
            fileName = MOVES_TREE_FILE_NAME

        resultFileName = os.path.join(RESULT_FOLDER, fileName)

        self.fileNameDot = resultFileName + ".dot"
        self.fileNamePng = resultFileName + ".png"
        dot = nx.drawing.nx_pydot.to_pydot(self.gameTreeDot)  # NetworkX -> Dot
        dot.write(self.fileNameDot)  # Write Dot file
        print("Dot file created : ", self.fileNameDot)
        try:
            dot.write_png(self.fileNamePng)  # Save result png
            print("Png file created : ", self.fileNamePng)
        except:
            print("Exception while creating png file!")

        # Create GraphML File
        self.fileNameMl = resultFileName + ".graphml"
        nx.write_graphml_lxml(self.gameTreeML, self.fileNameMl)
        print("ML file created : ", self.fileNameMl)
