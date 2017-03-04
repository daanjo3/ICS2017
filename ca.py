"""
Author: Daan Meijers
Student-ID: 10727167
Assignment: CA3 - Langton Parameter
"""

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

        self.make_param('humans', 0.6)
        # The table parameter can be used to set the rule set generation method.
        self.make_param('mosquitos', 1.2)
        self.make_param('m_infected', 0.5)
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
                    if random.random() < 0.3:
                        self.config.state[x, y] = 2
                    else:
                        self.config.state[x, y] = 1
                if state == 2 and m.infected == 0:
                    m.infected = 1

        # print "-UPDATE-"
        self.config.update()
        if self.t % 100 == 0:
            healthy = 0
            sick = 0
            for i in range(3):
                xnew, _ = np.where(self.config.state==i+1)
                if i+1 != 2: healthy += xnew.size
                else: sick += xnew.size
            print "Healthy: " + str(healthy)
            print "Sick: " + str(sick)
            print "Prevalence: " + str(sick/float(healthy+sick)*100.0)
        self.t += 1



if __name__ == '__main__':
    sim = CASim()
    from pyics import GUI
    cx = GUI(sim)
    cx.start()
