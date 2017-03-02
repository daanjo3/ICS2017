import random
import numpy as np

class Humans():
    state, ttl, age = None, None, None
    width, height = 0, 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = np.zeros((width, height))
        self.ttl = np.zeros((width, height))
        self.age = np.zeros((width, height))

    def printClass(self):
        print "State:\n" + str(self.state)
        print "TTL:\n" + str(self.ttl)

    def die(self, x, y):
        self.state[x, y] = 0
        self.ttl[x, y] = 0
        self.age[x, y] = 0
        xnew = random.randint(self.width)
        ynew = random.randint(self.height)
        self.birth(xnew, ynew)

    def birth(self, x, y):
        self.state[x, y] = 1
        self.ttl[x, y] = 14
        self.age[x, y] = 29200

    def build(self, humans):
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < humans:
                    self.birth(x, y)

    def get(self, x, y, l):
        if l == 0: return state[x, y]
        if l == 1: return ttl[x, y]
        if l == 2: return age[x, y]

    def set(self, x, y, n, l):
        if l == 0: state[x, y] = n
        if l == 1: ttl[x, y] = n
        if l == 2: age[x, y] = n

class Mosquito():
    # Locatie
    coordinate = []
    # Honger-timer
    hunger = 0
    # Infected boolean
    infected = 0

    def __init__(self, width, height, infected):
        x = random.randint(0, width)
        y = random.randint(0, height)
        self.coordinate = [x, y]
        if random.random() < infected: self.infected = 1
        self.hunger = random.randint(0, 7)
