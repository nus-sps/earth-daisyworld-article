# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines
from scipy.optimize import minimize

def equilibrium(v, nTestvec=21, dA=1e-5, ctol=1e-7, xtol=1e-7):
    def _cost(A):
        return v(A) ** 2
    def _stability(A):
        return (v(A + dA) - v(A - dA) < 0)
    fixedPoints = {}
    testvec = np.linspace(0, 1, num=nTestvec)
    for A0 in testvec:
        res = minimize(_cost, A0, method="nelder-mead", options={"xtol": xtol})
        p = round(res.x[0], 5)
        if (p not in fixedPoints.keys()) and (0 <= p <= 1) and (_cost(p) < ctol):
            isStable = _stability(p)
            fixedPoints[p] = isStable
    return fixedPoints

def plot_time_iteration(x, y, ax=None, plot=True):
    ax = ax or plt.gca()
    l0 = None
    if plot:
        l0, = ax.plot(x, y, '.', color='#ff8080')
    ax.set_xlim(0, x[-1])
    ax.set_ylim(0, 1)
    ax.set_xlabel('Time ($t$)')
    ax.set_ylabel('Daisy Area ($A$)')
    return l0,

def plot_state_space(x, y, fixedPoints=None, ax=None):
    ax = ax or plt.gca()
    ax.set_xlim(0, 1)
    ax.set_xlabel('Daisy Area ($A$)')
    ax.set_ylabel('Rate of Change of Daisy Area ($dA/dt$)')
    plt.legend(handles=[
        mlines.Line2D([], [], color='b', marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='r', marker='v', linestyle='None', label='Unstable')
    ])
    _l00, = ax.plot(x, np.zeros(len(x)), ':', color='#8080ff')
    _l01, = ax.plot(x, y, '-', color='#8080ff')
    l0 = (_l00, _l01)
    l1 = []
    if fixedPoints is not None:
        for k in fixedPoints.keys():
            _l1, = ax.plot(k, 0, "b^" if fixedPoints[k] else "rv", clip_on=False)
            l1.append(_l1)
    return l0, l1

def plot_together(t_data, s_data, fixedPoints=None):
    tx, ty = t_data
    tv = np.append(np.diff(ty), 0) / (tx[1] - tx[0])
    sx, sy = s_data
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    plot_time_iteration(tx, ty, ax1, plot=False)
    plot_state_space(sx, sy, fixedPoints, ax2)
    traj1, = ax1.plot(tx[0], ty[0], '.', color='#ff8080')
    traj2, = ax2.plot(ty[0], tv[0], '.', color='#ff8080')
    def _update(i, traj1, traj2):
        traj1.set_data(tx[:i], ty[:i])
        traj2.set_data(ty[:i], tv[:i])
        return traj1, traj2,
    ani = animation.FuncAnimation(fig, _update, len(tx), fargs=[traj1, traj2],
                                  interval=50 / len(tx), blit=True, repeat=False)
    return ani

def plot_bifurcation(x, y, ax=None):
    ax = ax or plt.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(min(x), max(x))
    ax.set_xlabel('Daisy Area ($A$)')
    ax.set_ylabel('Luminosity ($L$)')
    plt.legend(handles=[
        mlines.Line2D([], [], color='b', marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='r', marker='v', linestyle='None', label='Unstable')
    ])
    l0 = []
    for i in range(len(x)):
        for k in y[i].keys():
            _l0, = ax.plot(k, x[i], "b^" if y[i][k] else "rv", clip_on=False)
            l0.append(_l0)
    return l0,