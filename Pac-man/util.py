import sys
import inspect
import random


# Повертає Мангеттенську відстань між двома точками
def manhattanDistance( xy1, xy2 ):
    return abs( xy1[0] - xy2[0] ) + abs( xy1[1] - xy2[1] )


class Counter(dict):

    # Повертає суму підрахунків для всіх ключів.
    def totalCount(self):

        return sum(self.values())

    # Редагує лічильник таким чином, що загальна кількість усіх ключів дорівнює 1.
    def normalize(self):
        total = float(self.totalCount())
        if total == 0:
            return
        for key in self.keys():
            self[key] = self[key] / total


# Допоміжна функція, якщо метод не імпелментовано
def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" % (method, line, fileName))
    sys.exit(1)


# Нормалізація векторів або лічильників шляхом ділення кожного значення на суму всіх значень
def normalize(vectorOrCounter):
    normalizedCounter = Counter()
    if type(vectorOrCounter) == type(normalizedCounter):
        counter = vectorOrCounter
        total = float(counter.totalCount())
        if total == 0:
            return counter
        for key in counter.keys():
            value = counter[key]
            normalizedCounter[key] = value / total
        return normalizedCounter
    else:
        vector = vectorOrCounter
        s = float(sum(vector))
        if s == 0:
            return vector
        return [el / s for el in vector]


# Допоміжний метод для вибіркового розподілу
def sample(distribution, values=None):
    if type(distribution) == Counter:
        items = sorted(distribution.items())
        distribution = [i[1] for i in items]
        values = [i[0] for i in items]
    if sum(distribution) != 1:
        distribution = normalize(distribution)
    choice = random.random()
    i, total = 0, distribution[0]
    while choice > total:
        i += 1
        total += distribution[i]
    return values[i]


# Вибір елементу із розподілу
def chooseFromDistribution(distribution):
    if type(distribution) == dict or type(distribution) == Counter:
        return sample(distribution)
    r = random.random()
    base = 0.0
    for prob, element in distribution:
        base += prob
        if r <= base:
            return element


# Знаходить найближчу точку сітки до позиції (дискретно)
def nearestPoint(pos):
    (current_row, current_col) = pos

    grid_row = int(current_row + 0.5)
    grid_col = int(current_col + 0.5)
    return grid_row, grid_col
