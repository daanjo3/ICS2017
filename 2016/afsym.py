"""Afrika Simulator by Daan van Ingen (10345078) & Daan Meijers (10727167)
The following code is used to simulate the spread of Malaria in a random enviroment. Malaria is spread by mosquitos, which
transfer the disease from one person to another. Every cell in the grid acts as an human. A cell can have four states, dead/empty,
susceptible for malaria, infected by malaria and immune from malaria. The goal for this simulator is to find the settings which simulate
a stable enviroment with a stable amount of infected humans. Another goal is to figure out what must be done to minimize the infection spread
of malaria."""
import numpy as np
import copy
from random import randint
from pyics import Model
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

class CASim(Model):
    def __init__(self):
        Model.__init__(self)

        self.t = 0
        self.l_infected = []
        self.l_immune = []
        self.l_susceptible = []
        self.l_t = []
        self.d_sick = 0
        self.d_old = 0
        self.l_trend = [0]
        self.new_infected = 0
        self.new_infected0 = 0

        """The following variables are being used by the GUI."""
        self.make_param('width', 100)
        self.make_param('height', 100)

        """The net parameter tells the simulator what percentage of the population uses a net."""
        self.make_param('net', 0)

        """The human parameter tells the simulator how many humans will spawn. The standard chance for a human to spawn is 1/100. The chance for
        a human to spawn in the vicinity of that human is defined by this parameter."""
        self.make_param('humans', 80)

        """The born_infected parameter tells the simulator what the chance for malaria is for humans created at the start of the simulation."""
        self.make_param('born_infected', 3)

        """"The immune parameter tells the simulator what the chance is to become immune for malaria after being infected."""
        self.make_param('immune', 5)

        """The step_len parameter tells the simulator how often it should calculate certain data. Increasing this value will increase the speed
        of the simulation, though making the results of the data more inaccurate."""
        self.make_param('step_len', 10)
        self.init_grid()

    """This function is used for the initialisation of the simulation. It starts with calculation the amount of mosquitos base on the size of the
    grid and initializing of data structures to store our information."""
    def init_grid(self):
        self.mq_amount = self.width*self.height/100*20
        
        # We zouden iets bij moeten houden met al onze variablenen. Dict?
        self.stats = np.zeros((self.width, self.height), dtype={'names':['state', 'age', 'sick'], 'formats':['i4', 'i4', 'i4']})
        self.mosquito = np.zeros(self.mq_amount, dtype={'names':['x_coord', 'y_coord', 'infected', 'hunger'], 'formats':['i4', 'i4', 'i4', 'i4']})

        """This part of code is used for the creation of humans. Humans have four states, dead/empty, susceptible, infected and immune respectively.
        As explained earlier humans are more likely to be born in the neighbourhood of other humans and the first humans have a chance of getting infected.
        The age of a human is set random."""
        for x in range(0, self.width):
            for y in range(0, self.height):
                random = randint(0, 100)
                self.stats[x][y]['state'] = 0
                self.stats[x][y]['age'] = 0
                self.stats[x][y]['sick'] = 0
                if(self.stats[x][y-1]['state'] == 1 or self.stats[x-1][y]['state'] == 1):
                    if(random < self.humans):
                        if (randint(0, 100) < self.born_infected):
                            self.stats[x][y]['state'] = 2
                        else:
                            self.stats[x][y]['state'] = 1
                        self.stats[x][y]['age'] = randint(0,80)
                else:
                    if(random == 0):
                        if (randint(0, 100) < self.born_infected):
                            self.stats[x][y]['state'] = 2
                        else:
                            self.stats[x][y]['state'] = 1
                        self.stats[x][y]['age'] = randint(0,80)

        """As seen at the start of this function, the mosquito population is as large as 20 percent of the total amount of blocks in the grid
        Mosquitos are being placed randomly in the grid in the following loop. All mosquitos start uninfected."""
        for x in range(0, self.mq_amount):
            self.mosquito_birth(x)
        
        self.get_data()

    """Initializes a new mosquito at a random location on the grid."""
    def mosquito_birth(self, x):
        x_coord = randint(0, self.width - 1)
        y_coord = randint(0, self.height - 1)
        self.mosquito[x]['x_coord'] = x_coord
        self.mosquito[x]['y_coord'] = y_coord
        self.mosquito[x]['infected'] = 0
        self.mosquito[x]['hunger'] = 0
        
    """Resets all the data to ready the simulator for a new simulation."""
    def reset(self):
        self.t = 0
        self.l_t = []
        self.l_susceptible = []
        self.l_infected = []
        self.l_immune = []
        self.d_old = 0
        self.d_sick = 0
        self.l_trend = [0]
        self.new_infected = 0
        self.new_infected0 = 0
        self.init_grid()
        plt.close('State Ratio')
        plt.close('Death Count')

    """This function draws the current state of the grid. It also draws three graphs to represent some interesting data."""
    def draw(self):
        plt.cla()
        if not plt.gca().yaxis_inverted():
            plt.gca().invert_yaxis()

        """A special colormap is created for this simulator. White represents empty/dead, green: susceptible, red: infected and cyan: immune."""
        cmap = mpl.colors.ListedColormap(['white', 'green', 'red', 'cyan'])
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        plt.figure(1)
        plt.imshow(self.stats[:][:]['state'], interpolation='none', vmin=0, vmax=3,
                cmap=cmap, norm=norm)
        plt.axis('image')
        plt.title('t = %d' % self.t)

        """This part draws the first graph displaying the ratio between the three states (not counting state 0/dead/empty)."""
        plt.figure('State Ratio')
        plt.subplot(211)
        line1, = plt.plot(self.l_t, self.l_susceptible, 'g', label='Susceptible')
        line2, = plt.plot(self.l_t, self.l_infected, 'r', label='Infected')
        line3, = plt.plot(self.l_t, self.l_immune, 'c', label='Immune')
        plt.legend([line1, line2, line3], ['Susceptible', 'Infected', 'Immune'], framealpha=0.0)
        plt.xlabel('Steps')
        plt.ylabel('Percentage of People per State')
        plt.axis([0, 200, 0, 100])
        table2 = plt.subplot(212)
        table2.set_xticks([])
        table2.set_yticks([])
        table2.set_frame_on(False)
        plt.table(
            cellText=[[self.l_susceptible[-1], self.l_infected[-1], self.l_immune[-1]]],
            rowLabels=['%'],
            colLabels=('Susceptible', 'Infected', 'Immune'),
            loc=0)
        text1 = '''
        This graphs shows the ratio between Healthy, Sick and Immune people.
        It shows clearly how a certain prevalence is reached.
        Time is measured roughly in years, considering the age of humans and 
        the time they spend sick before recovering or dying.'''
        plt.figtext(0.1, 0.2, text1)

        """This part draws a second graph to display the cause of death. This is either old age or malaria, unfortunately mostly the latter."""
        plt.figure('Death Count')
        plt.subplot(211)
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.xlabel('Cause of Death')
        plt.ylabel('Percentage of Deaths')
        plt.axis([0, 2, 0, 100])
        sum_d = self.d_old+self.d_sick
        if(sum_d == 0):
            p_d_old = 0
            p_d_sick = 0
        else:
            p_d_old = float(self.d_old)/float(sum_d)*100
            p_d_sick = float(self.d_sick)/float(sum_d)*100
        bar1, = plt.bar(0, p_d_old, width=1, color='#996633')
        bar2, = plt.bar(1, p_d_sick, width=1, color='red')
        plt.legend([bar1, bar2], ['Death by Age', 'Death by Malaria'])
        text2 = '''
        This graph shows the ratio between the amount of deaths of sick or old 
        people. When people don't use protection against Malaria they are most 
        likely to die of that disease, as the percentage of deaths by Malaria is 
        enormous compared to the percentage of deaths by old age.'''
        plt.figtext(0.1, 0.2, text2)

        """This parts draws another graph to display the rise/decline of the infection spread."""
        plt.figure('Infection Trend')
        plt.subplot(211)
        plt.xlabel('Steps')
        plt.ylabel('Difference in Infection Spread')
        plt.plot(self.l_t, self.l_trend, 'm')
        plt.xlim(0, 200)
        plt.gca().invert_yaxis()
        text3 = '''
        This graph shows how fast the infection spreads. 
        The y-axis represents how many people get infected per tick.'''
        plt.figtext(0.1, 0.2, text3)
        plt.show()

    """ Moves the simulation one step ahead in time. First by randomly
    moving all the mosquitos. Then calculating their behaviour in
    a cell and killing them if they are too hungry (5). The last
    part is increasing the age of the humans and killing them if they 
    are too old or sick for too long or deciding if they become immune. """ 
    def step(self):
        self.random_move_mosq()
        self.t += 1
        self.new_infected = 0
        
        for x in range(0, self.mq_amount):
            status = self.stats[self.mosquito[x]['x_coord'], self.mosquito[x]['y_coord']]['state']
            """ If there is a human at x,y and there is no net"""
            if(status is not 0 and randint(1, 100) > self.net and self.mosquito[x]['hunger'] != 0):
                """Healthy vs infected, sick vs infected en sick vs non-infected.
                All come down to the same outcome"""
                if((status == 1 and self.mosquito[x]['infected'] == 1) or 
                    (status == 2 and self.mosquito[x]['infected'] == 0) or
                    (status == 2 and self.mosquito[x]['infected'] == 1)):
                    self.stats[self.mosquito[x]['x_coord'], self.mosquito[x]['y_coord']]['state'] = 2
                    if(status == 1 and self.mosquito[x]['infected'] == 1):
                        self.new_infected += 1
                    self.mosquito[x]['infected'] = 1
                    self.mosquito[x]['hunger'] = 0

                    """Immune human and infected mosquito, healthy human and uninfected mosquito
                    and immune human and uninfected mosquito lead to no change except hunger"""
                else:
                    self.mosquito[x]['hunger'] = 0
            else:
                self.mosquito[x]['hunger'] += 1
                if(self.mosquito[x]['hunger'] >= 5):
                    self.mosquito_birth(x)
        
        self.final_checks()

        if (self.t % self.step_len == 0):
            self.get_data()

    """The following function is used for the collection of data. Most graphs are made with information obtained
    by this function. The parameter step_len is used to indicate the step size between data collection. There are 
    two parts in this function. The first part calculates the percentage of particular states. The second part calculates
    the rise/decline of the infection spread."""
    def get_data(self):
        sum_humans = 0
        sum_infected = 0
        sum_immune = 0
        sum_susceptible = 0
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.stats[x][y]['state'] != 0:
                    sum_humans += 1
                if self.stats[x][y]['state'] == 1:
                    sum_susceptible += 1
                if self.stats[x][y]['state'] == 2:
                    sum_infected += 1
                if self.stats[x][y]['state'] == 3:
                    sum_immune += 1
        p_susceptible = (float(sum_susceptible)/float(sum_humans))*100
        p_infected = (float(sum_infected)/float(sum_humans))*100
        p_immune = (float(sum_immune)/float(sum_humans))*100
          
        self.l_t.append(self.t)
        self.l_susceptible.append(p_susceptible)
        self.l_infected.append(p_infected)
        self.l_immune.append(p_immune)

        if(self.t != 0):
            self.l_trend.append(self.new_infected-self.new_infected0)
            self.new_infected0 = self.new_infected

    """This function is used for updating the grid before the next round starts. It checks every cell where it
    increments the age and the sick timer. When someone gets too old(81) he dies. If someone reaches the end of
    the sick timer he will either die or become immune."""
    def final_checks(self):
        for x in range(0, self.height):
            for y in range(0, self.width):
                if(self.stats[x][y]['state'] != 0):
                    if(self.stats[x][y]['age'] >= 81):
                        """Human dies of old age"""
                        self.human_birth(x, y)
                        self.d_old += 1
                    elif(self.stats[x][y]['sick'] >= 5):
                        random = randint(0,100)
                        if(random <= self.immune):
                            """Human survives malaria and becomes immune"""
                            self.stats[x][y]['state'] = 3
                            self.stats[x][y]['age'] += 1
                            self.stats[x][y]['sick'] = 0
                        else:
                            """Human dies from malaria"""
                            self.human_birth(x,y)
                            self.d_sick += 1
                    elif(self.stats[x][y]['state'] == 2):
                        self.stats[x][y]['sick'] += 1
                        self.stats[x][y]['age'] += 1
                    else:
                        self.stats[x][y]['age'] += 1
        
    """Whenever a human dies this function is called. The idea was to spawn a human in a random empty cell,
    but this was not smart perfomance-wise. Therefore when someone dies a new healthy human spawns in the same cell."""
    def human_birth(self, x, y):
        """ places a new human at random place. This new person gets
            state 1 (healthy) and kills the old person"""
        self.stats[x][y]['state'] = 1
        self.stats[x][y]['age'] = 0
        self.stats[x][y]['sick'] = 0
        
    """This function moves all the mosquitos to a random location."""
    def random_move_mosq(self):
        for x in range(0, self.mq_amount):
            x_coord = randint(0, self.width - 1)
            y_coord = randint(0, self.height - 1)
            self.mosquito[x]['x_coord'] = x_coord
            self.mosquito[x]['y_coord'] = y_coord
                            
if __name__ == '__main__':
    sim = CASim()
    from pyics import GUI
    cx = GUI(sim)
    cx.start()