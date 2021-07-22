# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
import matplotlib.pyplot as plt
import utils1d

# Define Parameters
L = 1.0          # Luminosity
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

# Time Iteration
dt = 0.025
time = np.arange(0, 10, dt)
areas = np.zeros(len(time))
A = 0.92  # initial area to choose
for i in range(len(time)):
    # Forward-Euler Trajectory
    areas[i] = A
    A += v(A) * dt
utils1d.plot_time_iteration(time, areas)
plt.show()

# State Space
As = np.linspace(0, 1, num=101)
vs = v(As)  # find dA/dt at every possible value of A
fixed_points = utils1d.equilibrium(v)  # find equilibria
print(fixed_points)
utils1d.plot_state_space(As, vs, fixed_points)
plt.show()

# Animated Comparison
t_data = (time, areas)
s_data = (As, vs)
_ = utils1d.plot_together(t_data, s_data, fixed_points)
plt.show()

# Bifurcation Plot with respect to Luminosity
Luminosities = np.arange(0.5, 1.8, 0.02)
fixed_points_list = []
for l in Luminosities:
    L = l
    fixed_points_list.append(utils1d.equilibrium(v))
utils1d.plot_bifurcation(Luminosities, fixed_points_list)
plt.show()
