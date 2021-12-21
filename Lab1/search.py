import sys
from datetime import datetime

import searchAgents
import util
from graphicsUtils import _destroy_window
from pacman import readCommand, runGames


# Абстрактний клас, який описує структуру проблеми пошуку.
class SearchProblem:
    def getStartState(self):
        util.raiseNotDefined()

    def isGoalState(self, state):
        util.raiseNotDefined()

    def getSuccessors(self, state):
        util.raiseNotDefined()


# Алгоритм пошуку в глибину
def depthFirstSearch(problem):
    startTime = datetime.now()

    result = []
    visited = []
    coords_result = []

    stack = util.Stack()
    start = (problem.getStartState(), [], [])
    stack.push(start)

    while not stack.isEmpty():
        (state, path, coords) = stack.pop()
        if problem.isGoalState(state):
            result = path
            coords_result = coords
            visualiseWay(coords, 1, 0.4, .5)
            break

        visited.append(state)

        for w in problem.getSuccessors(state):
            if w[0] not in visited:
                newPath = path + [w[1]]
                newCoords = coords + [w[0]]
                newState = (w[0], newPath, newCoords)
                stack.push(newState)

    if not result:
        restartGame()
    endTime = datetime.now()
    print('Алгоритм працював:', endTime - startTime)
    if not isinstance(problem, searchAgents.FoodSearchProblem):
        print('Шлях:')
        for way in result:
            print(way + "; ", end='')
        print()
        print('Шлях із координатів:')
        for coords in coords_result:
            print(f'({coords[0]}, {coords[1]}); ', end='')
        print()
    return result


# Алгортм пошуку в ширину
def breadthFirstSearch(problem):
    startTime = datetime.now()

    result = []
    visited = []
    coords_result = []

    queue = util.Queue()
    start = (problem.getStartState(), [], [])
    queue.push(start)

    while not queue.isEmpty():
        (node, path, coords) = queue.pop()
        if problem.isGoalState(node):
            result = path
            coords_result = coords
            visualiseWay(coords, 1, 0.4, .5)
            break

        visited.append(node)
        for w in problem.getSuccessors(node):
            if w[0] not in visited:
                newPath = path + [w[1]]
                newCoords = coords + [w[0]]
                newNode = (w[0], newPath, newCoords)
                queue.push(newNode)

    if not result:
        restartGame()
    endTime = datetime.now()
    print('Алгоритм працював:', endTime - startTime)
    if not isinstance(problem, searchAgents.FoodSearchProblem):
        print('Шлях:')
        for way in result:
            print(way + "; ", end='')
        print()
        print('Шлях із координатів:')
        for coords in coords_result:
            print(f'({coords[0]}, {coords[1]}); ', end='')
        print()
    return result


# Алгоритм пошуку вузла із найменшою загальною вартістю
def uniformCostSearch(problem):
    startTime = datetime.now()
    result = []
    visited = []
    coords_result = []
    cost_result = []
    p_queue = util.PriorityQueue()
    start = (problem.getStartState(), [], 0, [])
    p_queue.update(start, 0)

    while not p_queue.isEmpty():
        (node, path, cost, coords) = p_queue.pop()
        # visualiseWay(coords)
        # sleep(0.001)
        if problem.isGoalState(node):
            result = path
            coords_result = coords
            cost_result = cost
            visualiseWay(coords_result, 1, 0.4, .5)
            break

        if node not in visited:
            visited.append(node)
            for w in problem.getSuccessors(node):
                newPath = path + [w[1]]
                newCost = cost + w[2]
                newCoords = coords + [w[0]]
                newNode = (w[0], newPath, newCost, newCoords)
                p_queue.update(newNode, newCost)

    if not result:
        restartGame()
    endTime = datetime.now()
    print('Алгоритм працював:', endTime - startTime)
    print(f'Загальна ціна шляху {cost_result}')
    if not isinstance(problem, searchAgents.FoodSearchProblem):
        print('Шлях:')
        for way in result:
            print(way + "; ", end='')
        print()
        print('Шлях із координатів:')
        for coords in coords_result:
            print(f'({coords[0]}, {coords[1]}); ', end='')
        print()
    return result


# Алгоритм пошуку а-зірочка
def aStarSearch(problem, heuristic):
    startTime = datetime.now()
    result = []
    visited = []
    cost_result = []

    p_queue = util.PriorityQueue()
    start = (problem.getStartState(), [], 0, [])
    p_queue.update(start, 0)

    while not p_queue.isEmpty():
        (node, path, cost, coords) = p_queue.pop()
        if problem.isGoalState(node):
            result = path
            cost_result = cost
            visualiseWay(coords, 1, 0.4, .5)
            break

        if node not in visited:
            visited.append(node)
            for w in problem.getSuccessors(node):
                newPath = path + [w[1]]
                newCost = cost + w[2]
                newCoords = coords + [w[0]]
                newNode = (w[0], newPath, newCost, newCoords)
                p_queue.update(newNode, newCost + heuristic(w[0], problem))

    if not result:
        restartGame()
    endTime = datetime.now()
    print('Алгоритм працював:', endTime - startTime)
    print(f'Загальна ціна шляху {cost_result}')
    if not isinstance(problem, searchAgents.FoodSearchProblem):
        print('Шлях:')
        for way in result:
            print(way + "; ", end='')
        print()
    return result


# Метод для візуалізації роботи алгоритмів та шляхів.
def visualiseWay(coords, r=.3, g=0.0, b=1.0):
    import __main__
    if '_display' in dir(__main__):
        if 'drawExpandedCells' in dir(__main__._display):
            try:
                if isinstance(coords[0], tuple):
                    for tupl in coords:
                        list_of_coords = list(tupl)
                        convert_to_list = list(list_of_coords[1])
                        convert_to_list.append(list_of_coords[0])
                        __main__._display.drawExpandedCells(convert_to_list, r, g, b)
            except:
                try:
                    __main__._display.drawExpandedCells(coords, r, g, b)
                except:
                    return


# Метод для перезапуску гри
def restartGame():
    print("Шляху не існує, перезапуск")
    _destroy_window()
    args = readCommand(sys.argv[1:])
    runGames(**args)


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
