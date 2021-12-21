import math
import util
from game import Agent


# Оцінка "сили" поточної позиції.
# За увагу береться найближча відстань до їжі, найближча відстань до привидів та поточна кількість очок
def scoreEvaluationFunction(currentGameState):
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newFood = newFood.asList()
    ghostPos = [(G.getPosition()[0], G.getPosition()[1]) for G in newGhostStates]

    if currentGameState.isLose():
        return -10000

    if newPos in ghostPos:
        return -10000

    closestFoodDist = sorted(newFood, key=lambda fDist: util.manhattanDistance(fDist, newPos))
    closestGhostDist = sorted(ghostPos, key=lambda gDist: util.manhattanDistance(gDist, newPos))

    score = 0

    fd = lambda fDis: util.manhattanDistance(fDis, newPos)
    gd = lambda gDis: util.manhattanDistance(gDis, newPos)

    if gd(closestGhostDist[0]) < 3:
        score -= 300
    if gd(closestGhostDist[0]) < 2:
        score -= 1000
    if gd(closestGhostDist[0]) < 1:
        return -10000

    if len(currentGameState.getCapsules()) < 2:
        score += 100

    if len(closestFoodDist) == 0 or len(closestGhostDist) == 0:
        score += currentGameState.getScore() + 10
    else:
        score += (currentGameState.getScore() + 10 / fd(closestFoodDist[0]) + 1 / gd(closestGhostDist[0]) +
                  1 / gd(closestGhostDist[-1]))

    return score


# Базовий (абстрактний клас) для мультиагентів
class MultiAgentSearchAgent(Agent):
    def __init__(self, evalFn='scoreEvaluationFunction', depth='3'):
        super().__init__()
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


# Агент minimax із alpha-beta pruning
class AlphaBetaAgent(MultiAgentSearchAgent):

    # Повернення наступної дії, в залежності від наведеного алгоритму
    def getAction(self, gameState):
        GhostIndex = [i for i in range(1, gameState.getNumAgents())]

        # Перевірка того, чи є статус термінальним
        def term(state, d):
            return state.isWin() or state.isLose() or d == self.depth

        # Min гравець (Привиди)
        def min_value(state, d, ghost, A, B):

            if term(state, d):
                return self.evaluationFunction(state)

            v = math.inf
            for action in state.getLegalActions(ghost):
                if ghost == GhostIndex[-1]:
                    v = min(v, max_value(state.generateSuccessor(ghost, action), d + 1, A, B))
                else:
                    v = min(v, min_value(state.generateSuccessor(ghost, action), d, ghost + 1, A, B))

                if v < A:
                    return v
                B = min(B, v)

            return v

        # Max гравець (Pacman)
        def max_value(state, d, A, B):

            if term(state, d):
                return self.evaluationFunction(state)

            v = -math.inf
            for action in state.getLegalActions(0):
                v = max(v, min_value(state.generateSuccessor(0, action), d, 1, A, B))

                if v > B:
                    return v
                A = max(A, v)
            print(self.evaluationFunction(state))
            return v

        # Вхідна точка в алгоритм. Тут же і відбувається Pruning
        def alphabeta(state):

            v = -math.inf
            act = None
            A = -math.inf
            B = math.inf

            for action in state.getLegalActions(0):
                tmp = min_value(gameState.generateSuccessor(0, action), 0, 1, A, B)

                if v < tmp:
                    v = tmp
                    act = action

                if v > B:
                    return v
                A = max(A, tmp)

            return act

        return alphabeta(gameState)


# Агент Expectimax
class ExpectimaxAgent(MultiAgentSearchAgent):

    # Повернення наступної дії, в залежності від наведеного алгоритму
    def getAction(self, gameState):

        GhostIndex = [i for i in range(1, gameState.getNumAgents())]

        # Перевірка того, чи є статус термінальним
        def term(state, d):
            return state.isWin() or state.isLose() or d == self.depth

        # Min гравець (Наступний крок буде залежати від деякої вірогідності)
        def exp_value(state, d, ghost):

            if term(state, d):
                return self.evaluationFunction(state)

            v = 0
            prob = 1 / len(state.getLegalActions(ghost))

            for action in state.getLegalActions(ghost):
                if ghost == GhostIndex[-1]:
                    v += prob * max_value(state.generateSuccessor(ghost, action), d + 1)
                else:
                    v += prob * exp_value(state.generateSuccessor(ghost, action), d, ghost + 1)
            return v

        # Max гравець (Pacman)
        def max_value(state, d):  # maximizer

            if term(state, d):
                return self.evaluationFunction(state)

            v = -math.inf
            for action in state.getLegalActions(0):
                v = max(v, exp_value(state.generateSuccessor(0, action), d, 1))
            print(self.evaluationFunction(state))
            return v

        res = [(action, exp_value(gameState.generateSuccessor(0, action), 0, 1)) for action in
               gameState.getLegalActions(0)]
        res.sort(key=lambda k: k[1])

        return res[-1][0]
