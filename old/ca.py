# Daan Meijers, 10727167
# Steven Raaijmakers, 10804242

from __future__ import division
import numpy as np
import random
from classes import Humans, Mosquito
from pyics import Model

class CASim(Model):
    def __init__(self):
        Model.__init__(self)

        self.t = 0
        self.config = None
        self.mosq = []

        #
        self.healthy = 0
        self.sick = 0
        self.prevalence = 0
        self.prevalences = []

        self.make_param('humans', 0.7)
        self.make_param('mosquitos', 1.2)

        self.make_param('m_infected', 0.5)
        self.make_param('p_mosquito_human', 1.0)
        self.make_param('p_human_mosquito', 1.0)

        self.make_param('prevention', 0.0)
        self.make_param('width', 100)
        self.make_param('height', 100)

    # Builds the initial simulation grid w/ humans & mosquitos
    def build(self):
        m_amount = int(self.mosquitos * self.width * self.height)

        for i in range(m_amount):
            if random.random() < self.m_infected:
                self.mosq.append(Mosquito(self.width, self.height, 1))
            else:
                self.mosq.append(Mosquito(self.width, self.height, 0))
        self.config = Humans(self.width, self.height)
        self.config.build(self.humans)
        # Set a specific amount of states to 1, 2 or 3
        # Create a list with a certain amount of mosquitos on random locations

    def reset(self):
        """Initializes the configuration of the cells and converts the entered
        rule number to a rule set."""

        self.t = 0
        self.build()
        self.prevalences = []

    def draw(self):
        """Draws the current state of the grid."""

        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap

        cm = LinearSegmentedColormap.from_list("my_cmap", ['white','green','red','c'])
        plt.cla()
        if not plt.gca().yaxis_inverted():
            plt.gca().invert_yaxis()
        plt.imshow(self.config.state, interpolation='none', vmin=0, vmax=3,
                cmap=cm)
        plt.axis('image')
        plt.title('t = %d' % self.t)

    # First loops over the humans which are infected
    def step(self):
        """Performs a single step of the simulation by advancing time (and thus
        row) and applying the rule to determine the state of the cells."""
        # Loop over mosquitos for interactions with humans
        # Then update the states of all humans

        # print "CHECK MOSQUITOS"
        for m in self.mosq:
            x, y = m.coordinate
            state = self.config.state[x, y]

            if m.hunger > 0:
                m.walk()
            elif state == 0:
                m.walk()
            else:
                # Musquito bites
                m.hunger = 7
                if state == 1 and m.infected == 1:
                    # Chance of getting infected after 1 bite
                    if random.random() < self.p_human_mosquito:
                        # has net
                        if random.random() > self.prevention:
                            self.config.state[x, y] = 2
                    else:
                        self.config.state[x, y] = 1
                if state == 2 and m.infected == 0:
                    if random.random() < self.p_mosquito_human:
                        m.infected = 1
                    else:
                        m.infected = 0

        self.config.update()

        # print "-UPDATE-"
        if self.t % 100 == 0:
            self.update_stats()
            self.print_update()

        self.t += 1

    def update_stats(self):
        healthy = 0
        sick = 0
        for i in range(3):
            xnew, _ = np.where(self.config.state==i+1)
            if i+1 != 2:
                healthy += xnew.size
            else:
                sick += xnew.size
        self.healthy = healthy
        self.sick = sick
        self.prevalence = sick / (healthy + sick) * 100.0
        self.prevalences.append(self.prevalence)

    def percentage(self, begin=0, end=14):
        ages = []
        zeros = 0

        for i in range(0, self.width):
            for j in range(0, self.height):
                age = self.config.age[i, j] / 365
                if age > begin and age < (end + 1):
                    ages.append(age)
                elif age == 0:
                    zeros += 1
        return len(ages) / ((self.height * self.width) - zeros) * 100

    def print_update(self):
        print "T:" + str(self.t) + ", Prevalence: " + str(self.prevalence)
        # print "Healthy: " + str(self.healthy)
        # print "Sick: " + str(self.sick)

    def set_params(self, dict):
        self.width = dict["width"]
        self.height = dict["height"]
        self.humans = dict["humans"]
        self.mosquitos = dict["mosquitos"]
        self.m_infected = dict["m_infected"]

        self.p_mosquito_human = dict["p_mosquito_human"]
        self.p_human_mosquito = dict["p_human_mosquito"]
        self.prevention = dict["has_mosquito_net"]

    def run(self, t=1000):
        self.reset()
        self.update_stats()

        print "INITIAL CONDITIONS:"
        print str(self.height) + " x " + str(self.width)
        print "Humans: " + str(self.healthy + self.sick) + ", Age 0-14: " + str(self.percentage())
        print "Mosquitos: " + str(self.mosquitos) + ", Infected: " + str(self.m_infected)
        print "P_mosquito_human: " + str(self.p_mosquito_human) + ", P_human_mosquito: " + str(self.p_human_mosquito) + "\n"
        for i in range(t + 1):
            self.step()

        return self.prevalences

if __name__ == '__main__':
    sim = CASim()

    parameters = {
        # percentage of human on field
        "humans": 0.5,
        # percentage of mosquitos on field
        "mosquitos": 1.2,
        # percentage of infected mosquites
        "m_infected": 0.5,

        "has_mosquito_net": 1.0,

        # probability of mosquito getting infected by human with malaria
        "p_mosquito_human": 1.0,
        # probability of human getting infected by mosquito with malaria
        "p_human_mosquito": 1.0,
    }

    n = 1
    ls = 5

    # TODO: choose ranges

    # try n times random shit
    for i in range(0, n):
        parameters["height"] = 100
        parameters["width"] = 100
        parameters["humans"] = 0.6
        parameters["mosquitos"] = 2.0
        parameters["m_infected"] = 0.5
        parameters["p_mosquito_human"] = 1.0
        parameters["p_human_mosquito"] = 0.3
        parameters["has_mosquito_net"] = 0.3
        sim.set_params(parameters)
        sim.run()

        # print "avg prevalence of last " + str(ls) + " items: " + str(sum(prevalences[-ls:]) / ls)
