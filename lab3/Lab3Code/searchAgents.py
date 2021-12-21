from random import randrange

from game import Directions
from game import Agent
from game import Actions
import search


# Загальний пошуковий агент, який знаходить шлях за допомогою наданого пошуку алгоритм для заданої проблеми пошуку,
# а потім повертає дії, щоб слідувати цьому шлях.
class SearchAgent(Agent):
    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        super().__init__()
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            self.searchFunction = lambda x: func(x, heuristic=heur)
        self.searchType = globals()[prob]

    # Це перший випадок, коли агент бачить макет ігрового поля. Тут ми обираємо шлях до мети.
    # На цьому етапі агент повинен обчислити шлях до мети та зберегти його у локальній змінній.
    def registerInitialState(self, state):
        problem = self.searchType(state)  # Makes a new search problem
        self.actions = self.searchFunction(problem)  # Find a path
        if '_expanded' in dir(problem): print('Розширено пошукових вузлів: %d' % problem._expanded)

    # Повертає наступну дію на шляху, обраному раніше.
    def getAction(self, state):
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP


# Мангеттенська відстань
def manhattan(node_x, goal_x, node_y, goal_y):
    return abs(node_x - goal_x) + abs(node_y - goal_y)


# Евклідова відстань
def euclidean(node_x, goal_x, node_y, goal_y):
    return ((node_x - goal_x) ** 2 + (node_y - goal_y) ** 2) ** 0.5


# Евклідова квадратична відстань
def euclideanSquared(node_x, goal_x, node_y, goal_y):
    return (node_x - goal_x) ** 2 + (node_y - goal_y) ** 2


# Мангеттенська евристика
def manhattanHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return manhattan(xy1[0], xy2[0], xy1[1], xy2[1])


# Евклідова евристика
def euclideanHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return euclidean(xy1[0], xy2[0], xy1[1], xy2[1])


# Евклідова квадратична евристика
def euclideanSquaredHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return euclideanSquared(xy1[0], xy2[0], xy1[1], xy2[1])


# Мангеттенська евристика для проблеми пошуку кутів (4 точок)
def cornersManhattanHeuristic(state, problem):
    if len(state[1]) == 0:
        return 0

    val = []

    for s in state[1]:
        val.append(manhattan(s[0], state[0][0], s[1], state[0][1]))

    return max(val)


# Евклідова евристика для проблеми пошуку кутів (4 точок)
def cornersEuclideanHeuristic(state, problem):
    if len(state[1]) == 0:
        return 0

    val = []

    for s in state[1]:
        val.append(euclidean(s[0], state[0][0], s[1], state[0][1]))

    return max(val)


# Евклідова квадратична евристика для проблеми пошуку кутів (4 точок)
def cornersEuclideanSquaredHeuristic(state, problem):
    if len(state[1]) == 0:
        return 0

    val = []

    for s in state[1]:
        val.append(euclideanSquared(s[0], state[0][0], s[1], state[0][1]))

    return max(val)


# Мангеттенська евристика для проблеми пошуку всієї їжі на полі
def foodHeuristicManhattan(state, problem):
    position, foodGrid = state
    food = foodGrid.asList()

    if len(food) == 0:
        return 0

    val = []
    for s in food:
        val.append(manhattan(s[0], state[0][0], s[1], state[0][1]))

    return max(val)


# Евклідова евристика для проблеми пошуку всієї їжі на полі
def foodHeuristicEuclidean(state, problem):
    position, foodGrid = state
    food = foodGrid.asList()

    if len(food) == 0:
        return 0

    val = []
    for s in food:
        val.append(euclidean(s[0], state[0][0], s[1], state[0][1]))
    return max(val)


# Евклідова квадратична евристика для проблеми пошуку всієї їжі на полі
def foodHeuristicEuclideanSquared(state, problem):
    position, foodGrid = state
    food = foodGrid.asList()

    if len(food) == 0:
        return 0

    val = []
    for s in food:
        val.append(euclideanSquared(s[0], state[0][0], s[1], state[0][1]))
    return max(val)


# Проблема пошуку визначає простір стану, стартовий стан, перевірку мети, функцію наступника та функцію витрат.
class PositionSearchProblem(search.SearchProblem):
    def __init__(self, gameState, costFn=lambda x: randrange(11), goal=(1, 1), start=None, warn=True, visualize=True):
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start is not None:
            self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # DO NOT CHANGE

    # Повертає стартову позицію Pac-man.
    def getStartState(self):
        return self.startState

    # Повертає булеве значення, яке характеризує, чи буде досягнута перемога, при переході у деякий стан.
    def isGoalState(self, state):
        isGoal = state == self.goal
        return isGoal

    # Повертає можливі наступні стани для Pac-man.
    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        self._expanded += 1  # DO NOT CHANGE

        return successors


# Ця проблема пошуку знаходить шляхи через усі чотири кути поля (4 точки)
class CornersProblem(search.SearchProblem):

    # Зберігає стіни, кути та початкову позицію Pac-man
    def __init__(self, startingGameState):
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height - 2, self.walls.width - 2
        self.corners = ((1, 1), (1, top), (right, 1), (right, top))
        self._expanded = 0

    # Повертає стартову позицію Pac-man.
    def getStartState(self):
        return self.startingPosition, self.corners

    # Повертає булеве значення, яке характеризує, чи буде досягнута перемога, при переході у деякий стан.
    def isGoalState(self, state):
        return len(state[1]) == 0

    # Повертає можливі наступні стани для Pac-man.
    def getSuccessors(self, state):

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state[0]
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)

            if not self.walls[nextx][nexty]:
                corners = tuple(x for x in state[1] if x != (nextx, nexty))
                successors.append((((nextx, nexty), corners), action, 1))

        self._expanded += 1  # DO NOT CHANGE
        return successors

    # Повертає вартість певної послідовності дій.
    def getCostOfActions(self, actions):
        x, y = self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
        return len(actions)


# Проблема пошуку, пов'язана з пошуком шляху, який збирає всю їжу у грі Pacman.
class FoodSearchProblem(search.SearchProblem):

    # Зберігає стіни, кути та початкову позицію Pac-man
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0  # DO NOT CHANGE
        self.heuristicInfo = {}  # A dictionary for the heuristic to store information

    # Повертає стартову позицію Pac-man.
    def getStartState(self):
        return self.start

    # Повертає булеве значення, яке характеризує, чи буде досягнута перемога, при переході у деякий стан.
    def isGoalState(self, state):
        return state[1].count() == 0

    # Повертає можливі наступні стани для Pac-man.
    def getSuccessors(self, state):
        successors = []
        self._expanded += 1  # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append((((nextx, nexty), nextFood), direction, 1))
        return successors

    # Повертає вартість певної послідовності дій.
    def getCostOfActions(self, actions):
        x, y = self.getStartState()[0]
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            cost += 1
        return cost
