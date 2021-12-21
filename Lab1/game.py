from datetime import datetime

from util import *


class Agent:
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        raiseNotDefined()


# Шляхи для пересування агентів
class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST: NORTH,
            WEST: SOUTH,
            STOP: STOP}

    RIGHT = dict([(y, x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}


# Конфігурація містить координати (x, y) персонажа разом з його напрямоком пересування.
class Configuration:

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    # Отримати позицію персонажа
    def getPosition(self):
        return self.pos

    # Отримати напрямок персонажа
    def getDirection(self):
        return self.direction

    # Створює нову конфігурацію, досягнуту шляхом перекладу поточної конфігурація за вектором дії.
    def generateSuccessor(self, vector):
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x + dx, y + dy), direction)


# Утримує стан агента (конфігурація, швидкість, наляканість тощо).
class AgentState:
    def __init__(self, startConfiguration, isPacman):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        self.numCarrying = 0
        self.numReturned = 0

    def copy(self):
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    # Отримати позицію агента
    def getPosition(self):
        if self.configuration is None:
            return None
        return self.configuration.getPosition()

    # Отримати напрямок агента
    def getDirection(self):
        return self.configuration.getDirection()


# Сітка деяких об'єктів. Двовимірний масив об’єктів, підкріплений списком списків.
class Grid:
    def __init__(self, width, height, initialValue=False):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]

    def __getitem__(self, i):
        return self.data[i]

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    # Рахунок об'єктів сітки
    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    # Конвертація сітки у список
    def asList(self, key=True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append((x, y))
        return list


# Колекція статичних методів для маніпулювання діями переміщення.
class Actions:
    # Шляхи
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST: (1, 0),
                   Directions.WEST: (-1, 0),
                   Directions.STOP: (0, 0)}

    _directionsAsList = [('West', (-1, 0)), ('Stop', (0, 0)), ('East', (1, 0)), ('North', (0, 1)), ('South', (0, -1))]

    TOLERANCE = .001

    # Метод, який перевертає шляхи. Потрібен для того, щоб привиди пересувалися більш природньо
    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    reverseDirection = staticmethod(reverseDirection)

    # Конвертація вектору у шлях
    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    vectorToDirection = staticmethod(vectorToDirection)

    # Конвертація шляху у вектор
    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return dx * speed, dy * speed

    directionToVector = staticmethod(directionToVector)

    # Метод для отримання можливих дій для агента
    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        if abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE:
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    # Метод для отримання легальних сусідів. Потрібен, щоб привиди не сливалися один із одним
    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    getLegalNeighbors = staticmethod(getLegalNeighbors)


# Створює новий пакет даних шляхом копіювання інформації з попередника.
class GameStateData:
    def __init__(self, prevState=None):
        if prevState is not None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agentStates = self.copyAgentStates(prevState.agentStates)
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score

        self._foodEaten = None
        self._foodAdded = None
        self._capsuleEaten = None
        self._agentMoved = None
        self._lose = False
        self._win = False
        self.scoreChange = 0

    def deepCopy(self):
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    # Метод для копіювання статусів агента
    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    # Створює початковий стан гри з масиву макета
    def initialize(self, layout, numGhostAgents):
        self.food = layout.food.copy()
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            if not isPacman:
                if numGhosts == numGhostAgents:
                    continue
                else:
                    numGhosts += 1
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
        self._eaten = [False for a in self.agentStates]


# Гра керує потоком управління, вимагаючи дії від агентів.
class Game:
    def __init__(self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
        self.numMoves = 0
        self.state = None
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    # Основний цикл для того, щоб грати
    def run(self):
        startTime = datetime.now()
        self.display.initialize(self.state.data)

        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if "registerInitialState" in dir(agent):
                agent.registerInitialState(self.state.deepCopy())

        agentIndex = self.startingIndex
        numAgents = len(self.agents)

        while not self.gameOver:
            agent = self.agents[agentIndex]
            if 'observationFunction' in dir(agent):
                observation = agent.observationFunction(self.state.deepCopy())
            else:
                observation = self.state.deepCopy()
            action = agent.getAction(observation)
            self.moveHistory.append((agentIndex, action))
            self.state = self.state.generateSuccessor(agentIndex, action)
            self.display.update(self.state.data)
            self.rules.process(self.state, self, startTime)
            agentIndex = (agentIndex + 1) % numAgents
