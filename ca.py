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

        self.make_param('humans', 0.7)
        # The table parameter can be used to set the rule set generation method.
        self.make_param('mosquitos', 0.0)
        self.make_param('m_infected', 0.5)
        self.make_param('prevention', 0.0)
        self.make_param('width', 50)
        self.make_param('height', 50)

    # Builds the initial simulation grid w/ humans & mosquitos
    def build(self):
        m_amount = int(self.mosquitos * self.width * self.height)

        self.mosq = [Mosquito(self.width, self.height, self.m_infected)] * m_amount
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

        cm = LinearSegmentedColormap.from_list("my_cmap", ['white','green','red','cyan'])
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
        pass
        


if __name__ == '__main__':
    sim = CASim()
    from pyics import GUI
    cx = GUI(sim)
    cx.start()
