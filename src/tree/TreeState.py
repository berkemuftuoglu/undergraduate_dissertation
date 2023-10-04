class TreeState:
    # This class is designed to maintain important information that will be used in a tree, along with its state

    def __init__(self, state, id=0, depth=0, graphLabel="", isTerminal=False, winner=0):
        self.state = state
        self.id = id
        self.depth = depth
        self.graphLabel = graphLabel
        self.isTerminal = isTerminal
        self.winner = winner
