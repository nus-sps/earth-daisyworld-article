import numpy as np
from scipy.optimize import minimize
from scipy.misc import derivative
import matplotlib.pyplot as plt
import os
import time

# Parameters
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
    ap = Aw*aw + Ab*ab + (1-Aw-Ab)*ag           # Planet Albedo
    Te = (L*(S/sigma)*(1-ap))**0.25             # Planet Temp
    Tb = (R*L*(S/sigma)*(ap-ab)+(Te**4))**0.25  # Black Daisy Temp
    bb = 1-(0.003265*((273.15+Ti)-Tb)**2)       # Black Daisy Growth Rate
    return Ab*((1-Ab-Aw)*bb-gamma)


# dA/dt of White Daisy
def vw(Ab, Aw):
    ap = Aw*aw + Ab*ab + (1-Aw-Ab)*ag           # Planet Albedo
    Te = (L*(S/sigma)*(1-ap))**0.25             # Planet Temp
    Tw = (R*L*(S/sigma)*(ap-aw)+(Te**4))**0.25  # White Daisy Temp
    bw = 1-(0.003265*((273.15+Ti)-Tw)**2)       # White Daisy Growth Rate
    return Aw*((1-Aw-Ab)*bw-gamma)


# Find Local Minima (Equilibria) and Jacobian Stability
def equilibrium():

    # Auxillary Function for Cost (to be minimised)
    def cost(A):
        Ab, Aw = A
        return (vb(Ab, Aw)) ** 2 + (vw(Ab, Aw)) ** 2

    print('Finding Equilibrium Positions...')
    solutions = []
    testvec = np.linspace(0, 1, num=21)
    for i in range(len(testvec)):
        for j in range(len(testvec)):
            if testvec[i] + testvec[j] <= 1:
                A0 = np.array([testvec[i], testvec[j]])
                res = minimize(cost, A0,
                               method='nelder-mead',
                               options={'xtol': 1e-8})
                x = round(res.x[0], 5)
                y = round(res.x[1], 5)
                if x+y <= 1 and x >= 0 and y >= 0:
                    if [x, y] not in solutions:
                        solutions.append([x, y])

    # Auxillary Function for Partial Derivatives
    def partial_derivative(func, var, point):
        args = point[:]
        def wraps(x):
            args[var] = x
            return func(*args)
        return derivative(wraps, point[var], dx=1e-5)

    print('Calculating Stability...')
    nature = []
    for i in range(len(solutions)):
        eb, ew = solutions[i]
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


# Set initial conditions for the trajectory
def plot_gen(L):

    # Generate Arrays
    Aw, Ab = np.mgrid[0:1:100j, 0:1:100j]
    x = vb(Ab, Aw)
    y = vw(Ab, Aw)

    # Impose Region Constraint (Ab+Aw >= 1)
    mask = np.zeros(y.shape, dtype=bool)
    for i in range(len(y)):
        y[i, len(y)-i:] = np.nan
    y = np.ma.array(y, mask=mask)

    # Find Equilibria and Stability
    sol, nature = equilibrium()

    # Plot
    print('Rendering Plots...')
    fig = plt.figure(figsize=(8, 8))
    ax1 = fig.add_subplot(111, adjustable='box', aspect=1)

    # Streamplot
    ax1.streamplot(Ab, Aw, x, y, color='k',
                   density=1.5, linewidth=0.75)

    # Equilibria
    for i in range(len(nature)):
        if nature[i] == 'Stable':
            ax1.plot(sol[i][0], sol[i][1], 'b^', markersize=9)
        else:
            ax1.plot(sol[i][0], sol[i][1], 'rv', markersize=9)

    # Dummy for Legends
    ax1.plot(-1, -1, 'b^', label='Stable')
    ax1.plot(-1, -1, 'rv', label='Unstable')

    # Formatting
    ax1.set_xlim(-0.1, 1.1)
    ax1.set_ylim(-0.1, 1.1)
    ax1.set_xlabel('$A_b$', fontsize=15)
    ax1.set_ylabel('$A_w$', fontsize=15)
    ax1.text(0.5, 0.9, "L = {:.3f}".format(L),
             fontsize=20, transform=ax1.transAxes, ha='center')
    ax1.legend(fontsize=12)

    plt.savefig('./plots/L = {:.3f}.png'.format(L))
    plt.close('all')


# Plot-saving
def plot_save(L_begin=0.5, L_end=1.7, L_step=0.001):
    # Book-keeping Head
    nl = int(round((L_end-L_begin)/L_step, 0))
    t_estimated = int(round((nl*2.263)/60, 0))
    t0 = time.time()
    print('\nINITIATED GENERATING {} PLOTS'.format(nl))
    print('Estimated Duration: {} min'.format(t_estimated))

    # Create Directory
    directory = './plots'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Saving Plots
    lumins = np.arange(L_begin, L_end, L_step)
    for i in range(len(lumins)):
        L = lumins[i]
        print('\nGenerating: L = {:.3f}'.format(L))
        plot_gen(L)

    # Book-keeping Tail
    t_elapsed = int(round((time.time()-t0)/60, 0))
    print('\nCOMPLETED GENERATING {} PLOTS'.format(nl))
    print('Time Elapsed: {} min'.format(t_elapsed))


plot_save()
