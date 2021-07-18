# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
import matplotlib.pyplot as plt
import utils2d

# Define Parameters
L = 1.0          # Luminosity
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

# Time Iteration
dt = 0.05
time = np.arange(0, 10, dt)
black_areas, white_areas = np.zeros(len(time)), np.zeros(len(time))
Ab, Aw = 0.87, 0.11  # initial areas to choose
for i in range(len(time)):
    black_areas[i] = Ab
    white_areas[i] = Aw
    Ab += vb(Ab, Aw) * dt
    Aw += vw(Ab, Aw) * dt
utils2d.plot_time_iteration(time, black_areas, white_areas)
plt.show()

# State Space
Aws, Abs = np.mgrid[0:1:100j, 0:1:100j] 
vbs, vws = vb(Abs, Aws), vw(Abs, Aws)  # find dA/dt at every possible value of Ab and Aw
fixed_points = utils2d.equilibrium(vb, vw)
print(fixed_points)
utils2d.plot_state_space(Abs, Aws, vbs, vws, fixed_points)
plt.show()

# Animated Comparison
t_data = (time, black_areas, white_areas)
s_data = (Abs, Aws, vbs, vws)
_ = utils2d.plot_together(t_data, s_data, fixed_points)
plt.show()

# Bifurcation Plot with respect to Luminosity
Luminosities = np.arange(0.5, 1.8, 0.02)
fixed_points_list = []
for l in Luminosities:
    L = l
    fixed_points_list.append(utils2d.equilibrium(vb, vw))
utils2d.plot_bifurcation(Luminosities, fixed_points_list)
plt.show()

# # Example: Save Bifurcation Images
# import os
# foldername = "./tmp/"
# if not os.path.exists(foldername):
#     os.makedirs(foldername)
# for i in range(len(Luminosities)):
#     plt.figure()
#     plt.suptitle("Luminosity: {:.3f}".format(Luminosities[i]))
#     L = Luminosities[i]
#     utils2d.plot_state_space(Abs, Aws, vb(Abs, Aws), vw(Abs, Aws), fixed_points_list[i])
#     plt.savefig(foldername + "{:.3f}".format(Luminosities[i]) + ".png")
#     plt.close('all')
