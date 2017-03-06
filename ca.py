"""
Author: Daan Meijers
Student-ID: 10727167
Assignment: CA3 - Langton Parameter
"""
from __future__ import division
import numpy as np
import random
from classes import Humans, Mosquito
from pyics import Model
import matplotlib.pyplot as plt
from scipy.interpolate import spline

class CASim(Model):
    def __init__(self):
        Model.__init__(self)

        self.t = 0
        self.config = None
        self.mosq = []
        #
        self.healthy = 0
        self.sick = 0

        self.healthies = []
        self.sicks = []

        #
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

        self.healthies.append(self.healthy / (self.healthy + self.sick) * 100)
        self.sicks.append(self.sick / (self.healthy + self.sick) * 100)

    def reset(self):
        self.t = 0
        self.healthies = []
        self.mosq = []
        self.sicks = []
        self.build()
        self.update_stats()

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

    def percentage(self, begin=0, end=14):
        ages = []
        # zeros = 0

        for i in range(0, self.width):
            for j in range(0, self.height):
                age = self.config.age[i, j] / 365
                ages.append(age)
        return sum(ages) / len(ages)

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

        # print "-UPDATE-"
        self.config.update()
        if self.t % 10 == 0:
            self.update_stats()
            print "Healthy: " + str(self.healthy)
            print "Sick: " + str(self.sick)
            # print str(self.percentage())
            print "---"
        self.t += 1

    def set_params(self, dict):
        self.width = dict["width"]
        self.height = dict["height"]
        self.humans = dict["humans"]
        self.mosquitos = dict["mosquitos"]
        self.m_infected = dict["m_infected"]

        self.p_mosquito_human = dict["p_mosquito_human"]
        self.p_human_mosquito = dict["p_human_mosquito"]
        self.prevention = dict["has_mosquito_net"]

        for key, value in dict.items():
            print key, value
        print "---"

    def run(self, t=300):
        self.reset()
        for i in range(t):
            self.step()
        return np.array(self.healthies), np.array(self.sicks)

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

        # probability of mosquito getting infected by human
        "p_mosquito_human": 1.0,
        # probability of human getting infected by mosquito with malaria
        "p_human_mosquito": 1.0,
    }

    n = 1
    ls = 5

    x = np.arange(0, 300, 10)

    parameters["height"] = 100
    parameters["width"] = 100
    parameters["humans"] = 0.7
    parameters["mosquitos"] = 0.7
    parameters["m_infected"] = 0.6
    parameters["p_mosquito_human"] = 0.3
    parameters["p_human_mosquito"] = 0.9
    parameters["has_mosquito_net"] = 0.0
    sim.set_params(parameters)
    healthies, sicks = sim.run()
    healthies = np.delete(healthies, 0)
    sicks = np.delete(sicks, 0)

    prevalences = sicks / (healthies + sicks) * 100

    xnew = np.linspace(x.min(),x.max(),50) #300 represents number of points to make between T.min and T.max
    h1 = spline(x,prevalences,xnew)

    parameters["m_infected"] = 0.2
    sim.set_params(parameters)

    healthies2, sicks2 = sim.run()
    healthies2 = np.delete(healthies2, 0)
    sicks2 = np.delete(sicks2, 0)

    prevalences2 = sicks2 / (healthies2 + sicks2) * 100
    h2 = spline(x, prevalences2, xnew)


    plt.plot(xnew, h1, label="Mosquitos infected 60%", color="orange")
    plt.plot(xnew, h2, label="Mosquitos infected 20%", color="purple")
    # plt.plot(xnew, h2, label="prevention 50%", color="orange")
    axes = plt.gca()
    axes.set_ylim([0,100])
    plt.title('Prevalence of malaria among humans')
    plt.ylabel('Percentage of people with malaria')
    plt.xlabel('Days')
    plt.legend()
    plt.show()
    # from pyics import GUI
    # cx = GUI(sim)
    # cx.start()
