from game import Agent
import util


# Абстрактний клас для агентів привидів
class GhostAgent(Agent):
    def __init__(self, index):
        super().__init__(index)
        self.index = index

    # Метод для отримання дії від агента
    def getAction(self, state):
        dist = self.getDistribution(state)
        return util.chooseFromDistribution(dist)

    # Повертає лічильник, що кодує розподіл над діями з наданого стану.
    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()


# Привид, який обирає наступну дію рівномірно випадковим чином.
class RandomGhost(GhostAgent):


    def getDistribution(self, state):
        dist = util.Counter()
        for a in state.getLegalActions(self.index): dist[a] = 1.0
        dist.normalize()
        return dist
