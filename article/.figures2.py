import os
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import utils2d

# Folder Setting
foldername = './Diagrams/'
if not os.path.exists(foldername):
    os.makedirs(foldername)

# Define Parameters
L = 1.5          # Luminosity
ab = 0.25        # Black Daisy Albedo
aw = 0.75        # White Daisy Albedo
ag = 0.5         # Ground Albedo
R = 0.2          # Insulation Constant
S = 917          # Solar Constant
sigma = 5.67e-8  # Stefan-Boltzmann Constant
Ti = 22.5        # Ideal Growth Temperature
gamma = 0.3      # Death Rate

# dA/dt of Black Daisy
def vb(Ab, Aw):
    ap = Aw * aw + Ab * ab + (1 - Aw - Ab) * ag                 # Planet Albedo
    Te = (L * (S / sigma) * (1 - ap)) ** 0.25                   # Planet Temp
    Tb = (R * L * (S / sigma) * (ap - ab) + (Te ** 4)) ** 0.25  # Black Daisy Temp
    bb = 1 - (0.003265 * ((273.15 + Ti) - Tb) ** 2)             # Black Daisy Growth Rate
    return Ab * ((1 - Ab - Aw) * bb - gamma)

# dA/dt of White Daisy
def vw(Ab, Aw):
    ap = Aw * aw + Ab * ab + (1 - Aw - Ab) * ag                 # Planet Albedo
    Te = (L * (S / sigma) * (1 - ap)) ** 0.25                   # Planet Temp
    Tw = (R * L * (S / sigma) * (ap - aw) + (Te ** 4)) ** 0.25  # White Daisy Temp
    bw = 1 - (0.003265 * ((273.15 + Ti) - Tw) ** 2)             # White Daisy Growth Rate
    return Aw * ((1 - Aw - Ab) * bw - gamma)

def tip2d(save=True):
    dt = 0.01
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    time = np.arange(0, 20, dt)
    black_areas, white_areas = np.zeros(len(time)), np.zeros(len(time))
    Ab, Aw = 0.58, 0.41  # initial areas to choose
    ax[0].set_title(
        r'$A_b^{(j=0)}=$' + '${:.02f}$'.format(Ab) + \
        r', $A_w^{(j=0)}=$' + '${:.02f}$'.format(Aw)
    )
    ax[0].grid()
    for i in range(len(time)):
        black_areas[i] = Ab
        white_areas[i] = Aw
        Ab += vb(Ab, Aw) * dt
        Aw += vw(Ab, Aw) * dt
    lineb, linew = utils2d.plot_time_iteration(time, black_areas, white_areas, ax=ax[0])
    lineb.set_color('#000000')
    linew.set_color('#000000')
    lineb.set_marker('')
    linew.set_marker('')
    lineb.set_linestyle('-')
    linew.set_linestyle('--')

    time = np.arange(0, 20, dt)
    black_areas, white_areas = np.zeros(len(time)), np.zeros(len(time))
    Ab, Aw = 0.33, 0.65  # initial areas to choose
    ax[1].set_title(
        r'$A_b^{(j=0)}=$' + '${:.02f}$'.format(Ab) + \
        r', $A_w^{(j=0)}=$' + '${:.02f}$'.format(Aw)
    )
    ax[1].grid()
    for i in range(len(time)):
        black_areas[i] = Ab
        white_areas[i] = Aw
        Ab += vb(Ab, Aw) * dt
        Aw += vw(Ab, Aw) * dt
    lineb, linew = utils2d.plot_time_iteration(time, black_areas, white_areas, ax=ax[1])
    lineb.set_color('#000000')
    linew.set_color('#000000')
    lineb.set_marker('')
    linew.set_marker('')
    lineb.set_linestyle('-')
    linew.set_linestyle('--')
    ax[0].legend(handles=[
        mlines.Line2D([], [], color='k', linestyle='-', label='Black Daisy Area'),
        mlines.Line2D([], [], color='k', linestyle='--', label='White Daisy Area')
    ])
    ax[1].legend(handles=[
        mlines.Line2D([], [], color='k', linestyle='-', label='Black Daisy Area'),
        mlines.Line2D([], [], color='k', linestyle='--', label='White Daisy Area')
    ])
    
    if save:
        fig.savefig(foldername + 'tip2d.png')
    else:
        plt.show()
    
def ssp2d(save=True):
    fig, ax = plt.subplots(figsize=(6, 6))
    Aws, Abs = np.mgrid[0:1:100j, 0:1:100j] 
    vbs, vws = vb(Abs, Aws), vw(Abs, Aws)  # find dA/dt at every possible value of Ab and Aw
    fixed_points = utils2d.equilibrium(vb, vw)
    print(fixed_points)
    l = utils2d.plot_state_space(Abs, Aws, vbs, vws, fixed_points, ax=ax)
    l[0].lines.set_color('#000000')
    for art in ax.get_children():
        if not isinstance(art, patches.FancyArrowPatch):
            continue
        art.set_color('#000000')
    for i in range(len(l[1])):
        if l[1][i].get_color() == 'b':
            l[1][i].set_color('#000000')
            l[1][i].set_markeredgecolor('#000000')
        else:
            l[1][i].set_color('#ffffff')
            l[1][i].set_markeredgecolor('grey')
        l[1][i].set_markeredgewidth(1.5)
        l[1][i].set_markersize(10)
    ax.legend(handles=[
        mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
            markersize=8, marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
            markersize=8, marker='v', linestyle='None', label='Unstable')
    ])

    if save:
        fig.savefig(foldername + 'ssp2d.png')
    else:
        plt.show()

def bif2d(save=True):
    global L
    fig, ax = plt.subplots(1, 2, figsize=(10, 4), subplot_kw=dict(projection="3d"))
    Luminosities = np.arange(0.5, 2.1, 0.02)
    fixed_points_list = []
    for l in Luminosities:
        L = l
        fixed_points_list.append(utils2d.equilibrium(vb, vw, nTestvec=6))
    _l0 = utils2d.plot_bifurcation(Luminosities, fixed_points_list, ax=ax[0])
    _l1 = utils2d.plot_bifurcation(Luminosities, fixed_points_list, ax=ax[1])
    ls = [_l0, _l1]

    ax[1].view_init(60, -20)

    for j in range(len(ls)):
        for i in range(len(ls[j])):
            if ls[j][i].get_color() == 'b':
                ls[j][i].set_color('#000000')
                ls[j][i].set_markeredgecolor('#000000')
            else:
                ls[j][i].set_color('#ffffff')
                ls[j][i].set_markeredgecolor('grey')
            ls[j][i].set_markeredgewidth(1.5)
            ls[j][i].set_markersize(8)
            ls[j][i].set_zorder(10)
        ax[j].legend(loc=1, handles=[
            mlines.Line2D([], [], color='k', markeredgecolor='k', markeredgewidth=1.5, 
                markersize=8, marker='^', linestyle='None', label='Stable'),
            mlines.Line2D([], [], color='w', markeredgecolor='grey', markeredgewidth=1.5,
                markersize=8, marker='v', linestyle='None', label='Unstable')
        ])
    
    if save:
        fig.savefig(foldername + 'bif2d.png')
    else:
        plt.show()

tip2d()
ssp2d()
bif2d()
