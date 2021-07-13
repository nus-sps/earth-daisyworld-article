# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import minimize

def equilibrium(v, L):
    """
        Finds the equilibrium points in 1D Daisyworld.
        Args:
            v: dA/dt function
            L: Luminosity
        Returns:
            The coordinates and the stability of each equilibrium point
    """

    def cost(A):
        """
            This is the function to be minimized in the scipy optimizer.
            I'm using the square of dA/dt.
        """
        return v(A, L) ** 2

    # Root Finder
    """
        Here, I select 21 points like this: A = 0, 0.05, ..., 1.
        For each of the points, I run the scipy optimizer.
        The optimizer wiggles these points around until the cost decreases enough.
        I collect the unique points.
        *note: cost(s) check is there because while nelder-mead is fast,
        it doesn't always guarantee that the cost goes close to zero.
    """
    solutions = []
    testvec = np.linspace(0, 1, num=21)
    for A0 in testvec:
        res = minimize(cost, A0, method='nelder-mead', options={'xtol': 1e-8})
        s = round(res.x[0], 5)
        if (0 <= s <= 1) and (cost(s) < 1e-7):
            if s not in solutions:
                solutions.append(s)

    # Stability Finder
    """
        For each of the collected points from above, I check the sign of the gradient.
        The fixed points with negative gradient is attractive/stable, and positive - repulsive/unstable.
    """
    nature = []
    ds = 1e-5
    for s in solutions:
        deriv = v(s + ds, L) - v(s - ds, L)
        if deriv < 0:
            nature.append('Stable')
        else:
            nature.append('Unstable')
    return solutions, nature

def plot_time_iteration(x, y, ax=None):
    ax = ax or plt.gca()
    ax.plot(x, y, color='#8080ff')
    ax.set_xlim(0, x[-1])
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('$t$', fontsize=15)
    ax.set_ylabel('$A$', fontsize=15)

def plot_state_space(x, y, eqs=None, ax=None):
    ax = ax or plt.gca()
    ax.plot(x, np.zeros(x.shape), ':', color='#ff8080')  # zero line
    ax.plot(x, y, '-', color='#ff8080')
    if eqs is not None:
        labels = {'s': 'Stable', 'u': 'Unstable'}
        sol, nature = eqs
        for i in range(len(nature)):
            if nature[i] == 'Stable':
                ax.plot(sol[i], 0, 'b^',
                        markersize=7, clip_on=False, label=labels['s'])
                labels['s'] = '_nolegend_'
            else:
                ax.plot(sol[i], 0, 'rv',
                        markersize=7, clip_on=False, label=labels['u'])
                labels['u'] = '_nolegend_'
    ax.set_xlim(0, 1)
    ax.set_ylim(np.amin(y) * 1.1, np.amax(y) * 1.1)
    ax.set_xlabel('$A$', fontsize=15)
    ax.set_ylabel('$dA/dt$', fontsize=15)

def animated_comparison(t_data, s_data, v_data, eqs=None):
    tx, ty = t_data
    sx, sy = s_data
    vty = v_data

    fig = plt.figure(figsize=(16, 6))
    ax1 = fig.add_subplot(121, adjustable='box')
    ax2 = fig.add_subplot(122, adjustable='box')

    plot_time_iteration(tx, ty, ax=ax1)
    plot_state_space(sx, sy, eqs, ax=ax2)

    # Trajectory Animation
    tip_line, = ax1.plot(tx[0], ty[0], color='k', linewidth=3)
    ssp_line, = ax2.plot(ty[0], vty[0], color='k', linewidth=3)

    def update(num, tip_line, ssp_line):
        tip_line.set_data(tx[:num], ty[:num])
        ssp_line.set_data(ty[:num], vty[:num])
        return tip_line, ssp_line,

    ani = animation.FuncAnimation(fig, update, len(tx),
                                  fargs=[tip_line, ssp_line],
                                  interval=20 * 1e3 / len(tx), blit=True, repeat=False)
    return ani

def plot_bifurcation(x, y):
    plt.figure()
    ax = plt.gca()

    labels = {'s': 'Stable', 'u': 'Unstable'}
    for j in range(len(x)):
        sol, nature = y[j]
        for i in range(len(nature)):
            if nature[i] == 'Stable':
                ax.plot(sol[i], x[j], 'k^',
                        markersize=8, clip_on=False, label=labels['s'])
                labels['s'] = '_nolegend_'
            else:
                ax.plot(sol[i], x[j], 'wv',
                        markeredgewidth=1.5, markeredgecolor='k',
                        markersize=6.5, label=labels['u'])
                labels['u'] = '_nolegend_'

    ax.set_xlim(0, 1)
    ax.set_ylim(min(x), max(x))
    ax.set_xlabel('$A$', fontsize=15)
    ax.set_ylabel('$L$', fontsize=15)
