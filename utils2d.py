# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize
from scipy.misc import derivative

def equilibrium(vb, vw, nTestvec=21, dA=1e-5, ctol=1e-7, xtol=1e-7):
    def _cost(A):
        return vb(A[0], A[1]) ** 2 + vw(A[0], A[1]) ** 2
    def _derivative(v, coords, idx):
        args = coords[:]
        def wraps(x):
            args[idx] = x
            return v(*args)
        return derivative(wraps, coords[idx], dx=dA)
    def _JacobianStability(p):
        j00 = _derivative(vb, p, 0)
        j01 = _derivative(vb, p, 1)
        j10 = _derivative(vw, p, 0)
        j11 = _derivative(vw, p, 1)
        jacobian = np.array([[j00, j01], [j10, j11]])
        eigval, _ = np.linalg.eig(jacobian)
        return (eigval[0] < 0 and eigval[1] < 0)
    fixedPoints = {}
    testvec = np.linspace(0, 1, num=nTestvec)
    for Ab0 in testvec:
        for Aw0 in testvec:
            if (Ab0 + Aw0) <= 1:
                    A0 = np.array([Ab0, Aw0])
                    res = minimize(_cost, A0, method="nelder-mead", options={'xtol': xtol})
                    pb = round(res.x[0], 5)
                    pw = round(res.x[1], 5)
                    if ((pb, pw) not in fixedPoints.keys()) and ((pb + pw) <= 1) and (pb >= 0) and (pw >= 0) and (_cost([pb, pw]) < ctol):
                        isStable = _JacobianStability([pb, pw])
                        fixedPoints[(pb, pw)] = isStable
    return fixedPoints

def plot_time_iteration(x, yb, yw, ax=None):
    if ax is None:
        ax = plt.gca()
        ax.plot(x, yb, '.', color='#ff00c0', label='$A_b$')
        ax.plot(x, yw, '.', color='#ffc000', label='$A_w$')
        ax.legend()
    ax.set_xlim(0, x[-1])
    ax.set_ylim(0, 1)
    ax.set_xlabel('Time ($t$)')
    ax.set_ylabel('Daisy Area ($A$)')

def plot_state_space(xb, xw, yb, yw, fixedPoints=None, ax=None):
    ax = ax or plt.gca()
    ax.set_aspect('equal')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel('Black Daisy Area ($A_b$)')
    ax.set_ylabel('White Daisy Area ($A_w$)')
    plt.legend(handles=[
        mlines.Line2D([], [], color='b', marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='r', marker='v', linestyle='None', label='Unstable')
    ])
    mask = np.zeros(yw.shape, dtype=bool)
    for i in range(len(yw)):
        yw[i, len(yw) - i:] = np.nan
        yw = np.ma.array(yw, mask=mask)  # impose Ab+Aw >= 1
    ax.streamplot(xb, xw, yb, yw, color='#8080ff', density=1.5, linewidth=0.75)
    if fixedPoints is not None:
        for k in fixedPoints.keys():
            ax.plot(k[0], k[1], "b^" if fixedPoints[k] else "rv", clip_on=False)

def plot_together(t_data, s_data, fixedPoints=None):
    tx, tyb, tyw = t_data
    sxb, sxw, syb, syw = s_data
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    plot_time_iteration(tx, tyw, tyb, ax1)
    plot_state_space(sxb, sxw, syb, syw, fixedPoints, ax2)
    traj1b, = ax1.plot(tx[0], tyb[0], '.', color='#ff00c0')
    traj1w, = ax1.plot(tx[0], tyw[0], '.', color='#ffc000')
    traj2, = ax2.plot(tyb[0], tyw[0], '.', color='#ff8080')
    def _update(i, traj1b, traj1w, traj2):
        traj1b.set_data(tx[:i], tyb[:i])
        traj1w.set_data(tx[:i], tyw[:i])
        traj2.set_data(tyb[:i], tyw[:i])
        return traj1b, traj1w, traj2,
    ani = animation.FuncAnimation(fig, _update, len(tx), fargs=[traj1b, traj1w, traj2],
                                  interval=50 / len(tx), blit=True, repeat=False)
    return ani

def plot_bifurcation(x, y):
    plt.figure()
    ax = plt.subplot(111, projection='3d')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(min(x), max(x))
    ax.set_xlabel("Black Daisy Area ($A_b$)")
    ax.set_ylabel("White Daisy Area ($A_w$)")
    ax.set_zlabel("Luminosity ($L$)")
    plt.legend(handles=[
        mlines.Line2D([], [], color='b', marker='^', linestyle='None', label='Stable'),
        mlines.Line2D([], [], color='r', marker='v', linestyle='None', label='Unstable')
    ])
    for i in range(len(x)):
        for k in y[i].keys():
            ax.plot(k[0], k[1], x[i], "b^" if y[i][k] else "rv", clip_on=False)
