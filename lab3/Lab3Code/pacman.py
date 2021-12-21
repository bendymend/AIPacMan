import csv
import os
import random
import sys
from datetime import datetime

import layout
from game import Actions
from game import Directions
from game import Game
from game import GameStateData
from util import manhattanDistance
from util import nearestPoint


# Визначає повний стан гри, включаючи їжу, капсули, конфігурації агентів та зміни очок.
class GameState:
    explored = set()

    # Повертає можливі дії щодо зазначеного агента.
    def getLegalActions(self, agentIndex=0):

        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions(self)
        else:
            return GhostRules.getLegalActions(self, agentIndex)

    # Генерує наступний стан після того, як зазначений агент виконає дію.
    def generateSuccessor(self, agentIndex, action):

        if self.isWin() or self.isLose():
            raise Exception('Can\'t generate a successor of a terminal state.')

        state = GameState(self)

        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction(state, action)
        else:  # A ghost is moving
            GhostRules.applyAction(state, action, agentIndex)

        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY  # Penalty for waiting around
        else:
            GhostRules.decrementTimer(state.data.agentStates[agentIndex])

        GhostRules.checkDeath(state, agentIndex)

        state.data._agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    # Повернути можливі дії для Pac-man
    def getLegalPacmanActions(self):
        return self.getLegalActions(0)

    # Генерує наступний стан, після того, як Pac-man зробить хід
    def generatePacmanSuccessor(self, action):
        return self.generateSuccessor(0, action)

    # Повернути статус Pac-man
    def getPacmanState(self):
        return self.data.agentStates[0].copy()

    # Повернути статус привидів
    def getGhostStates(self):
        return self.data.agentStates[1:]

    def getScore(self):
        return float(self.data.score)

    # Повернути позицію Pac-man
    def getPacmanPosition(self):
        return self.data.agentStates[0].getPosition()

    # Повернути статус привида
    def getGhostState(self, agentIndex):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getGhostState")
        return self.data.agentStates[agentIndex]

    # Повернути загальну кількість всіх агентів
    def getNumAgents(self):
        return len(self.data.agentStates)

    # Повернути місцеположення привида
    def getGhostPosition(self, agentIndex):
        return self.data.agentStates[agentIndex].getPosition()

    # Повернути місцеположення залишених капсул
    def getCapsules(self):
        return self.data.capsules

    # Повернути кількість їжі
    def getNumFood(self):
        return self.data.food.count()

    # Повернути місцеположення стін
    def getWalls(self):
        return self.data.layout.walls

    # Повернути місцеположення їжі
    def getFood(self):
        return self.data.food

    # Перевірка, чи мають задані координати їжу
    def hasFood(self, x, y):
        return self.data.food[x][y]

    # Повернення статусу гри (перемога/поразка)
    def isLose(self):
        return self.data._lose

    def isWin(self):
        return self.data._win

    def __init__(self, prevState=None):
        if prevState is not None:  # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state

    # Створює початковий стан гри з масиву макета
    def initialize(self, layout, numGhostAgents=1000):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, numGhostAgents)


# Час наляканості привидів
SCARED_TIME = 40
# Наскільки близько мають знаходитися привиди для того, щоб вбити Pac-man
COLLISION_TOLERANCE = 0.7
# Кількість очок, які губляться із кожним циклом гри
TIME_PENALTY = 1


# Правила гри керують потоком управління грою, вирішуючи, коли і як гра починається і закінчується.
class ClassicGameRules:

    def __init__(self, timeout=30):
        self.timeout = timeout

    # Ініціалізація нової гри
    def newGame(self, layout, pacmanAgent, ghostAgents, display, catchExceptions=False):
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        initState = GameState()
        initState.initialize(layout, len(ghostAgents))
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        return game

    # Перевіряє, чи пора закінчувати гру, якщо так, то запишемо інформацію про гру у файл та
    # виведемо відповідне повідомлення.
    def process(self, state, game, timestart):
        if (state.isWin() or state.isLose()) and (game.agents[0].__class__.__name__ == 'ExpectimaxAgent' or
                                                  game.agents[0].__class__.__name__ == 'AlphaBetaAgent'):
            #header = ['AlgorithmAgent', 'IsWon', 'GameTime', 'Points']
            data = [game.agents[0].__class__.__name__, state.isWin(), datetime.now() - timestart, state.data.score]

            with open('stats.csv', 'a', encoding='UTF8') as f:
                writer = csv.writer(f)

                # write the header
                #writer.writerow(header)

                # write the data
                writer.writerow(data)
        if state.isWin():
            self.win(state, game)
        if state.isLose():
            self.lose(state, game)

    def win(self, state, game):
        print("Pacman emerges victorious! Score: %d" % state.data.score)
        game.gameOver = True

    def lose(self, state, game):
        print("Pacman died! Score: %d" % state.data.score)
        game.gameOver = True

    # Отримати прогрес гри
    def getProgress(self, game):
        return float(game.state.getNumFood()) / self.initialState.getNumFood()


# Ці функції визначають, як Pac-man взаємодіє з навколишнім середовищем за класичними правилами гри.
class PacmanRules:
    PACMAN_SPEED = 1

    # Повертає список можливих дій.
    def getLegalActions(state):
        return Actions.getPossibleActions(state.getPacmanState().configuration, state.data.layout.walls)

    getLegalActions = staticmethod(getLegalActions)

    # Редагує стан, щоб відображати результати дії.
    def applyAction(state, action):
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        pacmanState = state.data.agentStates[0]

        vector = Actions.directionToVector(action, PacmanRules.PACMAN_SPEED)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(vector)

        next = pacmanState.configuration.getPosition()
        nearest = nearestPoint(next)
        if manhattanDistance(nearest, next) <= 0.5:
            PacmanRules.consume(nearest, state)

    applyAction = staticmethod(applyAction)

    # Опрацювання вживання їжі/капсул Pac-man
    def consume(position, state):
        x, y = position
        if state.data.food[x][y]:
            state.data.scoreChange += 10
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data._foodEaten = position
            numFood = state.getNumFood()
            if numFood == 0 and not state.data._lose:
                state.data.scoreChange += 500
                state.data._win = True
        if position in state.getCapsules():
            state.data.capsules.remove(position)
            state.data._capsuleEaten = position
            for index in range(1, len(state.data.agentStates)):
                state.data.agentStates[index].scaredTimer = SCARED_TIME

    consume = staticmethod(consume)


# Ці функції визначають, як привиди взаємодіють із своїм оточенням.
class GhostRules:
    GHOST_SPEED = 1.0

    # Дії, які можуть робити привиди
    def getLegalActions(state, ghostIndex):
        conf = state.getGhostState(ghostIndex).configuration
        possibleActions = Actions.getPossibleActions(conf, state.data.layout.walls)
        reverse = Actions.reverseDirection(conf.direction)
        if Directions.STOP in possibleActions:
            possibleActions.remove(Directions.STOP)
        if reverse in possibleActions and len(possibleActions) > 1:
            possibleActions.remove(reverse)
        return possibleActions

    getLegalActions = staticmethod(getLegalActions)

    # Редагує стан, щоб відображати результати дії.
    def applyAction(state, action, ghostIndex):

        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTimer > 0: speed /= 2.0
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)

    applyAction = staticmethod(applyAction)

    # Зменшення часу наляканості
    def decrementTimer(ghostState):
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint(ghostState.configuration.pos)
        ghostState.scaredTimer = max(0, timer - 1)

    decrementTimer = staticmethod(decrementTimer)

    # Перевірка того, чи вмер привид
    def checkDeath(state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0:
            for index in range(1, len(state.data.agentStates)):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill(pacmanPosition, ghostPosition):
                    GhostRules.collide(state, ghostState, index)
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill(pacmanPosition, ghostPosition):
                GhostRules.collide(state, ghostState, agentIndex)

    checkDeath = staticmethod(checkDeath)

    # Колізія
    def collide(state, ghostState, agentIndex):
        if ghostState.scaredTimer > 0:
            state.data.scoreChange += 200
            GhostRules.placeGhost(ghostState)
            ghostState.scaredTimer = 0
            state.data._eaten[agentIndex] = True
        else:
            if not state.data._win:
                state.data.scoreChange -= 500
                state.data._lose = True

    collide = staticmethod(collide)

    # Перевірка того, чи може привид вбити Pac-man
    def canKill(pacmanPosition, ghostPosition):
        return manhattanDistance(ghostPosition, pacmanPosition) <= COLLISION_TOLERANCE

    canKill = staticmethod(canKill)

    # Розмістити привида
    def placeGhost(ghostState):
        ghostState.configuration = ghostState.start

    placeGhost = staticmethod(placeGhost)


# Позначення базової строки
def default(str):
    return str + ' [Default: %default]'


# Парсинг аргументів консолі
def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key, val = p, 1
        opts[key] = val
    return opts


# Оброблення команди, що використовується для запуску Pac-man з командного рядка.
def readCommand(argv):
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='originalClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar='TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a', '--agentArgs', dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('KPI')

    # Choose a layout
    args['layout'] = layout.getLayout(options.layout, options.numGhosts*2)
    # Choose a Pacman agent
    if args['layout'] is not None:
        pacmanType = loadAgent(options.pacman)
        agentOpts = parseAgentArgs(options.agentArgs)
        pacman = pacmanType(**agentOpts)  # Instantiate Pacman with agentArgs
        args['pacman'] = pacman

        # Choose a ghost agent
        ghostTypeInput = loadAgent(options.ghost)
        ghostTypeDefault = loadAgent('RandomGhost')
        ghostIndexes = 1
        args['ghosts'] = []
        for ghost in range(options.numGhosts):
            args['ghosts'].append(ghostTypeInput(ghostIndexes))
            ghostIndexes += 1
        for ghost in range(options.numGhosts):
            args['ghosts'].append(ghostTypeDefault(ghostIndexes))
            ghostIndexes += 1

        # Choose a display format
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime=options.frameTime)

        args['catchExceptions'] = options.catchExceptions
        args['timeout'] = options.timeout

        return args

    raise Exception("The layout " + options.layout + " cannot be found")


# Завантаження агента
def loadAgent(pacman):
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir):
            continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')


# Запуск ігор
def runGames(layout, pacman, ghosts, display, catchExceptions=False, timeout=30):
    import __main__
    __main__.__dict__['_display'] = display
    rules = ClassicGameRules(timeout)
    game = rules.newGame(layout, pacman, ghosts, display, catchExceptions)
    game.run()
    return game


# Вхідна точка в програму
if __name__ == '__main__':
    args = readCommand(sys.argv[1:])  # Get game components based on input
    runGames(**args)
