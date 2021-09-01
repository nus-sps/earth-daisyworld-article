import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import utils1d

# Folder Setting
foldername = './Diagrams/'
if not os.path.exists(foldername):
    os.makedirs(foldername)

# Define Parameters
L = 1.5          # Luminosity
ai = 0.75        # Daisy Albedo
ag = 0.5         # Ground Albedo
R = 0.2          # Insulation Constant
S = 917          # Solar Constant
sigma = 5.67e-8  # Stefan-Boltzmann Constant
Ti = 22.5        # Ideal Growth Temperature
gamma = 0.3      # Death Rate

# dA/dt Function
def v(A):
    ap = A * ai + (1 - A) * ag                                 # Planet Albedo
    Te = (L * (S / sigma) * (1 - ap)) ** 0.25                  # Planet Temp
    T = (R * L * (S / sigma) * (ap - ai) + (Te ** 4)) ** 0.25  # Black Daisy Temp
    b = 1 - (0.003265 * ((273.15 + Ti) - T) ** 2)              # Black Daisy Growth Rate
    return A * ((1 - A) * b - gamma)

def tip1d(save=True):
    dt = 0.01
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    time = np.arange(0, 20, dt)
    areas = np.zeros(len(time))
    A = 0.32
    ax[0].set_title(r'$A^{(j=0)}=$' + '${:.02f}$'.format(A))
    ax[0].grid()
    for i in range(len(time)):
        # Forward-Euler Trajectory
        areas[i] = A
        A += v(A) * dt
    l = utils1d.plot_time_iteration(time, areas, ax=ax[0])
    l[0].set_color('#000000')
    l[0].set_marker('')
    l[0].set_linestyle('-')

    time = np.arange(0, 20, dt)
    areas = np.zeros(len(time))
    A = 0.46
    ax[1].set_title(r'$A^{(j=0)}=$' + '${:.02f}$'.format(A))
    ax[1].grid()
    for i in range(len(time)):
        # Forward-Euler Trajectory
        areas[i] = A
        A += v(A) * dt
    l = utils1d.plot_time_iteration(time, areas, ax=ax[1])
    l[0].set_color('#000000')
    l[0].set_marker('')
    l[0].set_linestyle('-')
    
    if save:
        fig.savefig(foldername + 'tip1d.png')
    else:
        plt.show()

def ssp1d(save=True):
    fig, ax = plt.subplots(figsize=(8, 6))
    As = np.linspace(0, 1, num=101)
    vs = v(As)  # find dA/dt at every possible value of A
    fixed_points = utils1d.equilibrium(v)  # find equilibria
    print(fixed_points)
    keys = []
    for k in fixed_points.keys():
        ax.axvline(k, color='k', linestyle='-.')
        keys.append(k)
    ax.annotate('',
        xytext=(keys[0] + 0.2, -0.03),
        xy=(keys[0] + 0.075, -0.03),
        arrowprops={'facecolor': 'white'})
    ax.annotate('',
        xytext=(keys[2] - 0.2, -0.03),
        xy=(keys[2] - 0.075, -0.03),
        arrowprops={'facecolor': 'white'})
    ax.annotate('',
        xytext=(keys[2] + 0.2, -0.03),
        xy=(keys[2] + 0.075, -0.03),
        arrowprops={'facecolor': 'white'})
    l = utils1d.plot_state_space(As, vs, fixed_points, ax=ax)
    l[0][0].set_color('#000000')
    l[0][1].set_color('#000000')
    for i in range(len(l[1])):
        if l[1][i].get_color() == 'b':
            l[1][i].set_color('#000000')
            l[1][i].set_markeredgecolor('#000000')
        else:
            l[1][i].set_color('#ffffff')
            l[1][i].set_markeredgecolor('grey')
        l[1][i].set_markeredgewidth(1.5)
        l[1][i].set_markersize(10)
    ax.legend(loc=3, handles=[
        mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
            markersize=8, marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
            markersize=8, marker='v', linestyle='None', label='Unstable')
    ])

    if save:
        fig.savefig(foldername + 'ssp1d.png')
    else:
        plt.show()

def bif1d1(save=True):
    global L
    fig, ax = plt.subplots(figsize=(8, 6))
    Luminosities = np.arange(0.5, 2.1, 0.02)
    fixed_points_list = []
    threes = []
    for l in Luminosities:
        L = l
        eqs = utils1d.equilibrium(v)
        fixed_points_list.append(eqs)
        if len(eqs) == 3:
            threes.append(l)
    l = utils1d.plot_bifurcation(Luminosities, fixed_points_list)
    for i in range(len(l[0])):
        if l[0][i].get_color() == 'b':
            l[0][i].set_color('#000000')
            l[0][i].set_markeredgecolor('#000000')
        else:
            l[0][i].set_color('#ffffff')
            l[0][i].set_markeredgecolor('grey')
        l[0][i].set_markeredgewidth(1.5)
        l[0][i].set_markersize(10)
        l[0][i].set_zorder(10)
    ax.legend(loc=4, handles=[
        mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
            markersize=8, marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
            markersize=8, marker='v', linestyle='None', label='Unstable')
    ])
    ax.axhline(threes[0], color='k', linestyle='-.')
    ax.axhline(threes[-1], color='k', linestyle='-.')
    ax.text(1.02, threes[0], '$L_1$', fontsize=16)
    ax.text(1.02, threes[-1], '$L_2$', fontsize=16)

    if save:
        fig.savefig(foldername + 'bif1d1.png')
    else:
        plt.show()

def bif1d2(save=True):
    global L
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    Luminosities = np.arange(0.5, 2.1, 0.02)
    fixed_points_list = []
    twos = []
    threes = []
    for l in Luminosities:
        L = l
        eqs = utils1d.equilibrium(v)
        fixed_points_list.append(eqs)
        if len(eqs) == 2:
            twos.append(l)
        elif len(eqs) == 3:
            threes.append(l)
            
    l = utils1d.plot_bifurcation(Luminosities, fixed_points_list, ax=ax[0])
    for i in range(len(l[0])):
        if l[0][i].get_color() == 'b':
            l[0][i].set_color('#000000')
            l[0][i].set_markeredgecolor('#000000')
        else:
            l[0][i].set_color('#ffffff')
            l[0][i].set_markeredgecolor('grey')
        l[0][i].set_markeredgewidth(1.5)
        l[0][i].set_markersize(8)
        l[0][i].set_zorder(10)
    ax[0].legend(loc=4, handles=[
        mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
            markersize=8, marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
            markersize=8, marker='v', linestyle='None', label='Unstable')
    ])
    ax[0].axhline(threes[-1], color='k', linestyle='-.')
    ax[0].text(0.05, twos[0] + 0.05, '1', fontsize=14)
    ax[0].text(0.65, threes[-1] + 0.05, '2', fontsize=14)
    ax[0].text(0.05, threes[-1] - 0.1, '3', fontsize=14)
    ax[0].annotate('',
        xytext=(0.05, twos[0] - 0.3),
        xy=(0.05, twos[0] - 0.1),
        arrowprops={'facecolor': 'white'})
    ax[0].annotate('',
        xytext=(0.4, (twos[-1] + twos[0]) / 2 - 0.1),
        xy=(0.6, (twos[-1] + twos[0]) / 2 + 0.1),
        arrowprops={'facecolor': 'white'})
    ax[0].annotate('',
        xytext=(0.5, threes[-1] + 0.1),
        xy=(0.2, threes[-1] + 0.1),
        arrowprops={'facecolor': 'white'})
    ax[0].annotate('',
        xytext=(0.05, threes[-1] + 0.1),
        xy=(0.05, threes[-1] + 0.3),
        arrowprops={'facecolor': 'white'})

    l = utils1d.plot_bifurcation(Luminosities, fixed_points_list, ax=ax[1])
    for i in range(len(l[0])):
        if l[0][i].get_color() == 'b':
            l[0][i].set_color('#000000')
            l[0][i].set_markeredgecolor('#000000')
        else:
            l[0][i].set_color('#ffffff')
            l[0][i].set_markeredgecolor('grey')
        l[0][i].set_markeredgewidth(1.5)
        l[0][i].set_markersize(8)
        l[0][i].set_zorder(10)
    ax[1].legend(loc=4, handles=[
        mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
            markersize=8, marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
            markersize=8, marker='v', linestyle='None', label='Unstable')
    ])
    ax[1].axhline(threes[0], color='k', linestyle='-.')
    ax[1].text(0.05, threes[0] - 0.1, '4', fontsize=14)
    ax[1].text(0.55, threes[0] + 0.05, '5', fontsize=14)
    ax[1].annotate('',
        xytext=(0.05, threes[-1] + 0.3),
        xy=(0.05, threes[-1] - 0.2),
        arrowprops={'facecolor': 'white'})
    ax[1].annotate('',
        xytext=(0.2, threes[0] - 0.05),
        xy=(0.4, threes[0] - 0.05),
        arrowprops={'facecolor': 'white'})
    ax[1].annotate('',
        xytext=(0.6, (twos[-1] + twos[0]) / 2 + 0.1),
        xy=(0.4, (twos[-1] + twos[0]) / 2 - 0.1),
        arrowprops={'facecolor': 'white'})
    ax[1].annotate('',
        xytext=(0.05, twos[0] - 0.1),
        xy=(0.05, twos[0] - 0.3),
        arrowprops={'facecolor': 'white'})

    if save:
        fig.savefig(foldername + 'bif1d2.png')
    else:
        plt.show()

tip1d()
ssp1d()
bif1d1()
bif1d2()
