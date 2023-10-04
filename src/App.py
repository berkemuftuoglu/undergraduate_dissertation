import random
import sys

import psutil
from PIL import Image
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal as Signal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, \
    QPushButton, QDialog, QTextEdit, QComboBox, QFileDialog, QLabel, QCheckBox, QSpinBox

from src.parser.StateMachine import StateMachine
from tree.TreeGenerator import *


def kill_proc_tree(pid, including_parent=True):
    # This method is used to kill subprocesses
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()


class MainWindow(QDialog):
    work_requested = Signal(int)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__parent = parent
        createFoldersWithCheck()
        self.lastOpenedFolder = ""
        self.moveList = []
        self.stateList = []
        self.currentStateIndex = -1
        self.playerNames = []
        self.game = UNKNOWN_GAME
        self.firstState = None
        self.fileNamePng = None
        self.gameTreeML = None

        self.fromFileChange = False

        self.setGeometry(400, 50, 1250, 700)
        self.font = QtGui.QFont("Courier New", 12, QtGui.QFont.Bold)
        self.mainLayout = QHBoxLayout()

        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()
        self.layout3 = QVBoxLayout()
        self.layout4 = QHBoxLayout()
        self.layout5 = QHBoxLayout()
        self.layout6 = QHBoxLayout()

        self.layout11 = QVBoxLayout()
        self.layout12 = QVBoxLayout()

        self.layout11.addLayout(self.layout3)
        self.layout11.addLayout(self.layout4)

        self.label = QLabel(self)
        self.label.setMaximumWidth(650)
        self.label.setMinimumWidth(400)
        self.label.setMinimumHeight(700)
        self.label.autoFillBackground()
        self.label.setStyleSheet("background-color: lightsteelblue")
        self.blankPixmap = QPixmap("blank.png")
        self.blankPixmap = self.blankPixmap.scaled(700, 800)
        self.layout12.addWidget(self.label)
        self.clearImage()

        self.layout12.addLayout(self.layout6)

        self.layout1.addLayout(self.layout11)
        self.layout1.addLayout(self.layout2)

        self.layout2.addLayout(self.layout5)

        self.outputTe1 = self.createTextEdit(self.layout3, True)
        self.outputTe1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.outputTe1.setMinimumWidth(750)
        self.outputTe1.setMinimumHeight(400)
        self.outputTe1.setMaximumHeight(700)
        self.outputTe1.setStyleSheet("color: black;  background-color: snow")

        self.layout1.addLayout(self.layout4)

        self.outputTe2 = self.createTextEdit(self.layout5, False)
        self.outputTe2.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.outputTe2.setStyleSheet("color: darkred;  background-color: seashell")
        self.outputTe2.setMinimumHeight(400)
        self.outputTe2.setMinimumWidth(180)
        self.outputTe2.setMaximumHeight(700)

        self.outputTe3 = self.createTextEdit(self.layout5, False)
        self.outputTe3.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.outputTe3.setStyleSheet("color: darkred;  background-color: seashell")
        self.outputTe3.setMinimumHeight(400)
        self.outputTe3.setMinimumWidth(180)
        self.outputTe3.setMaximumHeight(700)

        self.layout2.addLayout(self.layout6)

        self.layout7 = QVBoxLayout()
        self.layout8 = QVBoxLayout()
        self.layout9 = QVBoxLayout()
        self.layout10 = QVBoxLayout()
        self.layout6.addLayout(self.layout7)
        self.layout6.addLayout(self.layout8)
        self.layout6.addLayout(self.layout9)
        self.layout6.addLayout(self.layout10)

        self.createButton(self.layout4, self.btnLoadGame, "Load (File)", "green")
        self.createButton(self.layout4, self.btnLoadGameByText, "Load (Text)", "green")
        self.createButton(self.layout4, self.btnOpenImage, "Open Image", "green")
        self.createButton(self.layout4, self.btnSaveResult, "Save Xml", "green")
        self.gameCb = self.createCombobox(self.layout4)
        self.gameCb.addItem("---NO GAME---")

        storedGames = []
        for file in os.listdir(GAME_FOLDER):
            if os.path.isfile(os.path.join(GAME_FOLDER, file)):
                storedGames.append(file.split(".")[0])
        for game in GAMES_GDL:
            if game[1] in storedGames:
                self.gameCb.addItem(game[2])
        self.gameCb.currentIndexChanged.connect(self.gameCbChanged)
        self.showMoveTreeCb = self.createCheckbox(self.layout4)
        self.showMoveTreeCb.toggle()
        self.showMoveTreeCb.toggled.connect(self.moveTreeCbChanged)
        rightButton = self.createButton(self.layout10, self.btnRight, "-->", "yellow")
        rightButton.setMaximumWidth(40)

        self.createButton(self.layout10, self.btnGenerateTree, "Generate Tree", "green")

        self.moveCb = self.createCombobox(self.layout7)
        self.createButton(self.layout7, self.btnRandomMove, "Random Move", "blue", 180)
        self.createButton(self.layout8, self.btnMakeMove, "Make Move")

        self.nodeLimitSb = self.createSpinBox(self.layout8, 20, 10000, "green", 100, 20)
        leftButton = self.createButton(self.layout9, self.btnLeft, "<--", "yellow")
        leftButton.setMaximumWidth(40)
        self.depthSb = self.createSpinBox(self.layout9, 0, 50, "green", 1)

        self.mainLayout.addLayout(self.layout1)
        self.mainLayout.addLayout(self.layout12)

        self.mainLayout.setAlignment(self.layout3, QtCore.Qt.AlignBottom)

        self.qw = QtWidgets.QMainWindow()

        self.setLayout(self.mainLayout)
        self.setWindowTitle("Generating and Visualizing Trees")

    def createButton(self, layout, action, name, color="blue", width=140):
        button = QPushButton(name)
        if color == "blue":
            button.setStyleSheet(
                "QPushButton { color: white;background-color: darkBlue; padding: 2px ; font: bold 14px ; border-radius: 0px;}"
                "QPushButton:hover { background-color: blue }"
                "QPushButton:pressed{ color:black;background-color: lightBlue}")
        if color == "green":
            button.setStyleSheet(
                "QPushButton { color: white;background-color: darkGreen; padding: 2px ; font: bold 14px ; border-radius: 0px;}"
                "QPushButton:hover { background-color: green }"
                "QPushButton:pressed{ color:black;background-color: darkCyan}")
        if color == "yellow":
            button.setStyleSheet(
                "QPushButton { color: white;background-color: darkgoldenrod; padding: 2px ; font: bold 14px ; border-radius: 0px;}"
                "QPushButton:hover { background-color: goldenrod }"
                "QPushButton:pressed{ color:black;background-color: gold}")
        button.setMinimumHeight(35)
        button.setMaximumHeight(35)
        button.setMinimumWidth(width)
        button.setMaximumWidth(width)
        button.setFont(self.font)
        button.clicked.connect(action)
        layout.addWidget(button)
        return button

    def createTextEdit(self, layout, editable):
        te = QTextEdit()
        te.setFont(self.font)
        te.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        te.setTabChangesFocus(True)
        if not editable:
            te.setReadOnly(True)
        if layout != None:
            layout.addWidget(te)
        return te

    def createCombobox(self, layout):
        cb = QComboBox()
        cb.setFont(self.font)
        cb.setMaxVisibleItems(50)
        cb.setFixedSize(180, 35)
        if layout != None:
            layout.addWidget(cb)
        return cb

    def createCheckbox(self, layout):
        cb = QCheckBox()
        cb.setFont(self.font)
        cb.setText("Show move tree")
        cb.setFixedSize(180, 30)
        if layout != None:
            layout.addWidget(cb)
        return cb

    def createSpinBox(self, layout, rangeMin, rangeMax, color="yellow", val=1, step=1):
        sp = QSpinBox()
        sp.setFixedHeight(30)
        sp.setRange(rangeMin, rangeMax)
        sp.setValue(val)
        sp.setSingleStep(step)
        sp.setFont(self.font)
        sp.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        if color == "blue":
            sp.setStyleSheet("color: white;  background-color: darkblue")
        if color == "yellow":
            sp.setStyleSheet("color: white;  background-color: darkgoldenrod")
        if color == "green":
            sp.setStyleSheet("color: white;  background-color: darkGreen")
        if layout is not None:
            layout.addWidget(sp)
        return sp

    def btnLoadGame(self):
        # Load game (from file) button action
        fileName, _ = QFileDialog.getOpenFileName(self, 'Load Game', self.lastOpenedFolder, "Gdl Files (*.gdl)")
        if not fileName:
            return
        self.lastOpenedFolder = fileName
        self.game = findGameByFileName(fileName)
        self.fromFileChange = True
        if self.game[0] != 0:
            self.gameCb.setCurrentIndex(self.game[0])
        else:
            self.gameCb.setCurrentIndex(0)
        self.fromFileChange = False
        self.updateGameByFileName(fileName)

    def updateGameByFileName(self, fileName):
        # Updates game by game file name
        self.outputTe1.clear()
        try:
            file = open(fileName, 'r', encoding="utf-8")
        except:
            self.resetGame()
            self.clearResult()
            self.addToResult("EXCEPTION. (GAME FILE NOT FOUND)", self.outputTe2)
            return
        lines = file.readlines()
        for line in lines:
            if line != "":
                self.outputTe1.append(line.replace("\n", ""))
        self.outputTe1.moveCursor(1)

        self.updateGameByText()

    def clearImage(self):
        # Clears game tree image (loads blank image)
        self.label.setPixmap(self.blankPixmap)

    def btnOpenImage(self):
        # Open Image button action
        if self.fileNamePng is not None:
            im = Image.open(self.fileNamePng)
            im.show()
        else:
            self.clearResult()
            self.addToResult("NO IMAGE!", self.outputTe2)
            return

    def btnSaveResult(self):
        # Save XML Result button action
        if self.gameTreeML is not None:
            fileName, _ = QFileDialog.getSaveFileName(self, 'Save Xml', self.lastOpenedFolder,
                                                      "GraphMl Files (*.graphml)")
            if not fileName:
                return
            nx.write_graphml_lxml(self.gameTreeML, fileName)
        else:
            self.clearResult()
            self.addToResult("NO XML!", self.outputTe2)
            return

    def updateGameByText(self):
        # Updates state machine by text in the game description area
        self.resetGame()
        try:
            data = self.outputTe1.toPlainText()
            stateMachine = StateMachine.getStateFromData(data)
            self.firstState = StateMachine.getStateFromData(data)
            self.stateList.append(stateMachine)
            self.moveList.append(GDL_NO_MOVE)
            self.currentStateIndex = 0
            self.playerNames = getPlayerNames(self.getCurrentState())
        except:
            self.resetGame()
            self.clearResult()
            self.addToResult("EXCEPTION. (PARSING GAME DESCRIPTION)", self.outputTe2)
            return
        self.resultCursor()
        self.afterLoad()

    def btnLoadGameByText(self):
        # Load game from text button action
        self.updateGameByText()

    def resetGame(self):
        # Resets details
        self.clearResult()
        self.moveList.clear()
        self.stateList.clear()
        self.currentStateIndex = -1
        self.currentStateIndex = -1
        self.playerNames.clear()
        self.firstState = None
        self.fileNamePng = None

    def afterLoad(self):
        # Actions to be taken after loading a game
        self.clearImage()
        self.showState()
        self.refreshMovesCb()

    def getCurrentState(self):
        # Returns current state of the game
        if self.currentStateIndex == -1:
            return None
        else:
            return self.stateList[self.currentStateIndex]

    def showState(self):
        # Displays information about the state of the game in the fields in the interface.
        # It also shows the game tree if the checkbox is ticked.
        state = self.getCurrentState()
        if state is None:
            self.clearResult()
            self.addToResult("LOAD GAME FIRST!", self.outputTe2)
            return

        self.clearResult()
        try:
            self.addToResult("PAST MOVES : ", self.outputTe2)

            for i in range(self.currentStateIndex + 1):
                if self.moveList[i] != GDL_NO_MOVE:
                    self.addToResult(str(i) + " : " + self.moveList[i], self.outputTe2)

            self.addEmptyLineToResult(self.outputTe2)

            stateFacts = getNotControlByFacts(state)
            self.addToResult("STATE INFO : ", self.outputTe2)
            for fact in stateFacts:
                self.addToResult(fact, self.outputTe2)

            labelLines = getLabelForState(self.game[0], stateFacts, None, LABEL_TYPE_TEXT)
            for labelLine in labelLines:
                self.addToResult(labelLine, self.outputTe3)

            self.addEmptyLineToResult(self.outputTe3)
            if state.is_terminal():
                self.addToResult("Game over!", self.outputTe3)
                self.addToResult(getWinnerStr(state, self.playerNames), self.outputTe3)
                self.addEmptyLineToResult(self.outputTe3)
                self.addToResult("SCORES : ", self.outputTe3)
                for player in self.playerNames:
                    score = getScoreForPlayer(state, player)
                    self.addToResult(player + " : " + str(score), self.outputTe3)
                self.clearMovesCb()
            else:
                legalMovesP1, p1 = getLegalMoves(state, self.playerNames)
                self.addToResult("TURN : " + p1, self.outputTe3)
                self.addEmptyLineToResult(self.outputTe3)
                self.addToResult("LEGAL MOVES : ", self.outputTe3)
                for move in legalMovesP1:
                    self.addToResult(str(move), self.outputTe3)
                self.refreshMovesCb()

            if self.showMoveTreeCb.isChecked():
                self.showMoveTree()
        except:
            self.clearResult()
            self.clearImage()
            self.addToResult("EXCEPTION. (SHOW STATE)", self.outputTe2)
        self.resultCursor()

    def showMoveTree(self):
        if self.currentStateIndex == -1:
            return
        treeGenerator = TreeGenerator(state=self.firstState, game=self.game, movesTree=True)
        treeGenerator.generateWithMoves(self.moveList[0:self.currentStateIndex + 1])
        self.gameTreeML = treeGenerator.gameTreeML
        self.updateImage(treeGenerator)

    def btnMakeMove(self):
        # Make Move button action
        if self.moveCb.currentText() == "":
            return

        state = self.getCurrentState()
        if state is None:
            self.clearResult()
            self.addToResult("LOAD GAME FIRST!", self.outputTe2)
            return

        self.makeMove(state, self.moveCb.currentText())

    def makeMove(self, state, move):
        # Enables the execution of the given move in the given state
        self.clearResult()
        try:
            if self.currentStateIndex != len(self.stateList) - 1:
                self.stateList = self.stateList[0:self.currentStateIndex + 1]
                self.moveList = self.moveList[0:self.currentStateIndex + 1]

            p1, p2 = getPlayers(state, self.playerNames)
            state.move(p1, move)
            legalMovesP2 = getLegalMovesForPlayer(state, p2)
            state.move(p2, legalMovesP2[0])
            nextState = state.next()
            self.clearResult()
            self.moveList.append(p1 + " - " + move)
            self.stateList.append(nextState)
            self.currentStateIndex += 1
            self.showState()

        except:
            self.clearResult()
            self.addToResult("EXCEPTION. (MAKE MOVE)", self.outputTe2)
        self.resultCursor()

    def btnRandomMove(self):
        # Random Move button action
        state = self.getCurrentState()
        if state is None or state.is_terminal():
            return
        legalMoves, _ = getLegalMoves(state, self.playerNames)
        if len(legalMoves) == 0:
            return
        move = legalMoves[random.randint(0, len(legalMoves) - 1)]
        self.makeMove(state, move)

    def btnGenerateTree(self):
        # Generate Tree button action
        state = self.getCurrentState()
        if state is None:
            self.clearResult()
            self.addToResult("LOAD GAME FIRST!", self.outputTe2)
            return

        try:
            depth = self.depthSb.value()
            if depth == 0:
                depth = NO_LIMIT
            treeNodeLimit = self.nodeLimitSb.value()
            self.clearImage()
            self.clearResult()
            self.addToResult("Tree generation started...", self.outputTe2)
            QtGui.QGuiApplication.processEvents()
            treeGenerator = TreeGenerator(state=state, game=self.game, moveDepth=depth, treeNodeLimit=treeNodeLimit)
            treeGenerator.generate()
            self.clearResult()
            self.addToResult("Tree generation completed.", self.outputTe2)
            self.addToResult("", self.outputTe2)
            self.addToResult("Number of nodes : " + str(treeGenerator.numNodes - 1), self.outputTe2)
            self.addToResult("", self.outputTe2)
            self.addToResult("Max depth : " + str(treeGenerator.maxDepth), self.outputTe2)
            self.addToResult("", self.outputTe2)
            self.addToResult("Time elapsed : " + str(round(treeGenerator.elapsedTime, 2)) + " seconds.", self.outputTe2)
            self.gameTreeML = treeGenerator.gameTreeML
            self.updateImage(treeGenerator)
        except:
            self.clearResult()
            self.addToResult("EXCEPTION. (GENERATING TREE)", self.outputTe2)
        self.resultCursor()

    def updateImage(self, treeGenerator):
        # Updates the image with the last generated tree (may be move tree)
        treeGenerator.createFiles()
        self.fileNamePng = treeGenerator.fileNamePng
        pixmap = QPixmap(self.fileNamePng)
        pixmap = pixmap.scaled(600, 750, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)

    def btnLeft(self):
        # Goes to previous state
        if self.currentStateIndex == 0:
            return

        self.currentStateIndex -= 1
        self.showState()

    def btnRight(self):
        # Goes to next state
        if self.currentStateIndex == len(self.stateList) - 1:
            return

        self.currentStateIndex += 1
        self.showState()

    def refreshMovesCb(self):
        # Refreshs legal moves combobox
        try:
            legalMovesP1, _ = getLegalMoves(self.getCurrentState(), self.playerNames)
            self.moveCb.clear()
            for move in legalMovesP1:
                self.moveCb.addItem(move)
        except:
            self.clearResult()
            self.addToResult("EXCEPTION. (FINDING LEGAL MOVES)", self.outputTe2)
            self.resultCursor()

    def clearMovesCb(self):
        # Clears the legal moves combobox when the game is over
        self.moveCb.clear()

    def clearResult(self):
        # Clears the interface areas where the state details are printed
        self.outputTe2.clear()
        self.outputTe3.clear()

    def addToResult(self, line, te):
        # Adds text line to text area
        te.append(line)

    def addEmptyLineToResult(self, te):
        # Adds empty line to text area
        self.addToResult("\n", te)

    def resultCursor(self):
        # Resets cursors of the areas where the state details are printed
        self.outputTe2.moveCursor(1)
        self.outputTe3.moveCursor(1)

    def gameCbChanged(self):
        # Actions to be taken if a new game is selected in the game combobox
        if self.fromFileChange:
            return

        index = self.gameCb.currentIndex()
        if index == 0:
            self.game = UNKNOWN_GAME
            self.outputTe1.clear()
            self.resetGame()
            self.clearImage()
        else:
            self.game = GAMES_GDL[index - 1]
            fullName = getFullFileNameForGame(self.game[1])
            self.updateGameByFileName(fullName)

    def moveTreeCbChanged(self):
        # Shows the move tree or deletes it according to checkbox selection
        if self.showMoveTreeCb.isChecked():
            self.showMoveTree()
        else:
            self.clearImage()


app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
app.exec_()
