import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize
from scipy.misc import derivative

_modes = ['display', 'save']

def equilibrium(vb, vw, L):
    # Auxillary Function for Cost (to be minimised)
    def cost(A):
        Ab, Aw = A
        return (vb(Ab, Aw, L=L)) ** 2 + (vw(Ab, Aw, L=L)) ** 2

    # Root Finder
    solutions = []
    testvec = np.linspace(0, 1, num=21)
    for Ab0 in testvec:
        for Aw0 in testvec:
            if (Ab0 + Aw0) <= 1:
                A0 = np.array([Ab0, Aw0])
                res = minimize(cost, A0,
                               method='nelder-mead',
                               options={'xtol': 1e-8})
                sb = round(res.x[0], 5)
                sw = round(res.x[1], 5)
                if ((sb + sw) <= 1) and (sb >= 0) and (sw >= 0) and (cost([sb, sw]) < 1e-7):
                    if [sb, sw] not in solutions:
                        solutions.append([sb, sw])

    # Auxillary Function for Partial Derivatives
    def partial_derivative(func, var, point):
        args = point[:]

        def wraps(x):
            args[var] = x
            return func(*args, L=L)

        return derivative(wraps, point[var], dx=1e-5)

    # Stability Finder
    nature = []
    for s in solutions:
        eb, ew = s
        j00 = partial_derivative(vb, var=0, point=[eb, ew])
        j01 = partial_derivative(vb, var=1, point=[eb, ew])
        j10 = partial_derivative(vw, var=0, point=[eb, ew])
        j11 = partial_derivative(vw, var=1, point=[eb, ew])
        jacobian = np.array([[j00, j01], [j10, j11]])
        eigval, _ = np.linalg.eig(jacobian)
        if eigval[0] < 0 and eigval[1] < 0:
            nature.append('Stable')
        else:
            nature.append('Unstable')

    return solutions, nature

def plot_time_iteration(x, yb, yw, ax=None):
    ax = ax or plt.gca()
    ax.plot(x, yb, color='#8080ff', label='$A_b$')
    ax.plot(x, yw, color='#ff80ff', label='$A_w$')

    # Formatting
    ax.set_xlim(0, x[-1])
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('$t$', fontsize=15)
    ax.set_ylabel('$A$', fontsize=15)
    ax.legend(fontsize=12)

def plot_state_space(xb, xw, yb, yw, eqs=None, ax=None):
    # Impose Region Constraint (Ab+Aw >= 1)
    mask = np.zeros(yw.shape, dtype=bool)
    for i in range(len(yw)):
        yw[i, len(yw) - i:] = np.nan
        yw = np.ma.array(yw, mask=mask)

    ax = ax or plt.gca(aspect=1)
    ax.streamplot(xb, xw, yb, yw, color='#ff8080', density=1.5, linewidth=0.75)

    # Equilibria
    if eqs is not None:
        labels = {'s': 'Stable', 'u': 'Unstable'}
        sol, nature = eqs
        for i in range(len(nature)):
            if nature[i] == 'Stable':
                ax.plot(sol[i][0], sol[i][1], 'b^',
                        markersize=7, label=labels['s'])
                labels['s'] = '_nolegend_'
            else:
                ax.plot(sol[i][0], sol[i][1], 'rv',
                        markersize=7, label=labels['u'])
                labels['u'] = '_nolegend_'

    # Formatting
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('$A_b$', fontsize=15)
    ax.set_ylabel('$A_w$', fontsize=15)
    ax.legend(fontsize=12)

def animated_comparison(t_data, s_data, eqs=None):
    tx, tyb, tyw = t_data
    sxb, sxw, syb, syw = s_data

    fig = plt.figure(figsize=(16, 6))
    ax1 = fig.add_subplot(121, adjustable='box')
    ax2 = fig.add_subplot(122, adjustable='box', aspect=1)

    plot_time_iteration(tx, tyw, tyb, ax=ax1)
    plot_state_space(sxb, sxw, syb, syw, eqs, ax=ax2)

    # Trajectory Animation
    tip_line_b, = ax1.plot(tx[0], tyb[0], color='k', linewidth=3)
    tip_line_w, = ax1.plot(tx[0], tyw[0], color='k', linewidth=3)
    ssp_line, = ax2.plot(tyb[0], tyw[0], color='k', linewidth=3)

    def update(num, tip_line_b, tip_line_w, ssp_line):
        tip_line_b.set_data(tx[:num], tyw[:num])
        tip_line_w.set_data(tx[:num], tyb[:num])
        ssp_line.set_data(tyb[:num], tyw[:num])
        return tip_line_b, tip_line_w, ssp_line,

    ani = animation.FuncAnimation(fig, update, len(tx),
                                  fargs=[tip_line_b, tip_line_w, ssp_line],
                                  interval=20 * 1e3 / len(tx), blit=True, repeat=False)

    return ani

def plot_bifurcation(x, y, elev=12.5, azim=-132.5):
    plt.figure()
    ax = plt.gca(projection='3d')

    labels = {'s': 'Stable', 'u': 'Unstable'}
    for j in range(len(x)):
        sol, nature = y[j]
        for i in range(len(nature)):
            if nature[i] == 'Stable':
                ax.plot([sol[i][0]], sol[i][1], x[j], 'k^',
                        markersize=8, clip_on=False, label=labels['s'])
                labels['s'] = '_nolegend_'
            else:
                ax.plot([sol[i][0]], sol[i][1], x[j], 'wv',
                        markeredgewidth=1.5, markeredgecolor='k',
                        markersize=6.5, label=labels['u'])
                labels['u'] = '_nolegend_'

    # Formatting
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(min(x), max(x))
    ax.set_xlabel('$A_b$', fontsize=15)
    ax.set_ylabel('$A_w$', fontsize=15)
    ax.set_zlabel('$L$', fontsize=15)
    ax.legend(fontsize=12)
    ax.view_init(elev=elev, azim=azim)
