# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

import numpy as np
from scipy.misc.common import derivative
from scipy.optimize import minimize
import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams['font.size'] = 18

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        # Global Settings
        self.setWindowTitle("Daisyworld")
        self.setWindowIcon(qtg.QIcon('icon.ico'))
        self.setFont(qtg.QFont("Helvetica", 10))
        self.resize(2000, 1500)

        # Menu Bar
        menubar = self.menuBar()
        menuHelp = menubar.addMenu("&Help")
        actionHelpAbout = qtw.QAction("&About", self)
        actionHelpAbout.triggered.connect(lambda: self._spawnWindow(AboutWindow))
        actionHelpLicense = qtw.QAction("&License", self)
        actionHelpLicense.triggered.connect(lambda: self._spawnWindow(LicenseWindow))
        menuHelp.addAction(actionHelpAbout)
        menuHelp.addAction(actionHelpLicense)

        # Main Widget
        mainWidget = qtw.QWidget(self)
        self.setCentralWidget(mainWidget)
        layout = qtw.QVBoxLayout()
        mainWidget.setLayout(layout)

        # Tabs
        tabs = qtw.QTabWidget()
        tabs.addTab(WorldTab(1), "One-Daisy")
        tabs.addTab(WorldTab(2), "Two-Daisy")
        # tabs.addTab(WorldTab(1, bifurcation=True), "1D Bifurcation")
        # tabs.addTab(WorldTab(2, bifurcation=True), "2D Bifurcation")
        layout.addWidget(tabs)

    def _spawnWindow(self, obj):
        self.window = obj()
        self.window.show()

class NotificationWindow(qtw.QWidget):
    def __init__(self, title, text):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(qtg.QIcon('icon.ico'))
        self.setFont(qtg.QFont("Helvetica", 10))
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        label = qtw.QLabel()
        label.setText(text)
        label.setOpenExternalLinks(True)
        layout.addWidget(label)

class AboutWindow(NotificationWindow):
    def __init__(self):
        super().__init__(
            "Daisyworld - About",
            "Welcome to Daisyworld GUI!<br/><br/>" + \
            "This is an interactive plotting programme that helps you visualise<br/>" + \
            "the dynamics of the Daisyworld climate model. Here, you can explore<br/>" + \
            "how the time evolution of the dynamical system is related to the<br/>" + \
            "trajectory in its state space.<br/><br/>" + \
            "Visit our <a href='https://github.com/nus-sps/earth-daisyworld-article'>Github repository page</a> for more.<br/><br/>" + \
            "More about us:<br/>" + \
            "<a href='http://sps.nus.edu.sg/'>Special Programme in Science, National University of Singapore</a>"
        )

class LicenseWindow(NotificationWindow):
    def __init__(self):
        super().__init__(
            "Daisyworld - License",
            "This program is free software: you can redistribute it and/or modify<br/>" + \
            "it under the terms of the GNU General Public License as published by<br/>" + \
            "the Free Software Foundation, either version 3 of the License, or<br/>" + \
            "(at your option) any later version.<br/><br/>" + \
            "This program is distributed in the hope that it will be useful,<br/>" + \
            "but WITHOUT ANY WARRANTY; without even the implied warranty of<br/>" + \
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the<br/>" + \
            "GNU General Public License for more details.<br/><br/>" + \
            "You should have received a copy of the GNU General Public License<br/>" + \
            "along with this program.  If not, see <a href='https://www.gnu.org/licenses/'>here</a>."
        )

class WorldTab(qtw.QWidget):
    def __init__(self, dimension, bifurcation=False):
        super().__init__()
        self.dimension = dimension
        self.bifurcation = bifurcation
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        self._addDWCV()

        # Parameter Input Boxes
        layoutInputBoxes = qtw.QFormLayout()
        self.inputboxes = []
        for v in self.DW.parameters.get():
            inputbox = self._newInputBox(str(v.value))
            self.inputboxes.append(inputbox)
            asterisk = '*' if v.unitRange else ""
            layoutInputBoxes.addRow("{}{} ({})".format(v.name, asterisk, v.short), inputbox)

        # Buttons
        layoutButtons = qtw.QHBoxLayout()
        self.buttons = [self._newButton("Restore defaults"), self._newButton("Run!")]
        self.buttons[0].clicked.connect(self._restore)
        self.buttons[1].clicked.connect(self._run)
        layoutButtons.addWidget(qtw.QLabel("*from 0 to 1"))
        layoutButtons.addStretch()
        for b in self.buttons:
            layoutButtons.addWidget(b)

        # Plots
        layoutPlots = qtw.QHBoxLayout()
        layoutPlots.addWidget(self.canvas)

        # And finally...
        layout.addLayout(layoutInputBoxes)
        layout.addLayout(layoutButtons)
        layout.addLayout(layoutPlots)

    def _addDWCV(self):
        if self.dimension == 1:
            self.DW = DaisyWorld1()
        elif self.dimension == 2:
            self.DW = DaisyWorld2()
        self.canvas = PlotCanvas(self.DW)

    def _newInputBox(self, text, width=300):
        inputbox = qtw.QLineEdit()
        inputbox.setText(text)
        inputbox.setFixedWidth(width)
        return inputbox
    
    def _newButton(self, text, width=300, function=None, *args):
        button = qtw.QPushButton("{}".format(text))
        button.setFixedWidth(width)
        if function is not None:
            button.clicked.connect(lambda: function(*args))
        return button
    
    def _restore(self):
        choice = qtw.QMessageBox.question(self,
            "Restore Warning!",
            "Are you sure you want to restore the default values?",
            qtw.QMessageBox.Yes | qtw.QMessageBox.No
        )
        if choice == qtw.QMessageBox.Yes:
            self.DW.parameters.reset()
            self._dw2box()

    def _run(self):
        if self.canvas.isRunning:
            self.buttons[1].setText("Rerun!")
            self.canvas.figStop()
        else:
            try:
                self._box2dw()
                self.buttons[1].setText("Stop")
                self.DW.setupEvolution()
                self.canvas.setDaisyWorld(self.DW)
                self.canvas.figInit()
                self.canvas.figRun()
                self.buttons[1].setStyleSheet("color: black; font-size: 27px")
            except Exception as e:
                self.buttons[1].setStyleSheet("color: red; font-size: 27px")
        self.canvas.isRunning = not self.canvas.isRunning

    def _dw2box(self):
        values = [str(p.value) for p in self.DW.parameters.get()]
        for i in range(len(self.inputboxes)):
            self.inputboxes[i].setText(values[i])

    def _box2dw(self):
        values = [float(ib.text()) for ib in self.inputboxes]
        self.DW.parameters.set(values)

class PlotCanvas(FigureCanvas):
    def __init__(self, daisyWorld, width=10, height=12, dpi=100):
        self.isRunning = False
        self.DW = daisyWorld
        fig = self.DW.generateFigure(width, height, dpi)
        FigureCanvas.__init__(self, fig)
        self.figInit()

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self._update)
    
    def setDaisyWorld(self, daisyWorld):
        self.DW = daisyWorld

    def figRun(self, milliseconds=0):
        self.timer.start(milliseconds)
    
    def figStop(self):
        self.timer.stop()

    def figInit(self):
        for ax in self.DW.axes:
            ax.cla()
        self.DW.drawBackground()
        self.draw()

    def _update(self):
        self.flush_events()
        self.DW.evolve()
        self.DW.drawForeground()
        self.draw()
    
class Parameters:
    def __init__(self):
        pass

    def add(self, attribute, parameter):
        setattr(self, attribute, parameter)
        self.unitRangeCheck()

    def get(self):
        return [v for v in self.__dict__.values()]
    
    def set(self, values):
        i = 0
        for v in vars(self):
            vars(self)[v].setValue(values[i])
            i += 1
        self.unitRangeCheck()

    def reset(self):
        for v in vars(self):
            vars(self)[v].resetValue()
    
    def unitRangeCheck(self):  # induce value error downstream
        if hasattr(self, "Ab0") and hasattr(self, "Aw0"):
            _ = Parameter("Initial Total Daisy Area", "_", self.Ab0.value + self.Aw0.value, unitRange=True)

class Parameter:
    def __init__(self, name="_", short="_", value=0, unitRange=False):
        self.name = name
        self.short = short
        self.unitRange = unitRange
        self.setValue(value)
        self.default = self.value
    
    def getValue(self):
        return self.value
    
    def setValue(self, value):
        self.value = value
        if self.unitRange:
            if (value < 0) or (1 < value):
                raise ValueError("Parameter value out of range!")
                
    def resetValue(self):
        self.value = self.default

class FixedPoint:
    def __init__(self, coords, stable=None):
        self.coords = coords
        self.stable = stable

class DaisyWorld1:
    def __init__(self):
        self.parameters = Parameters()
        self.parameters.add("A0", Parameter("Initial Daisy Area", "A<sup>t=0</sup>", 0.92, unitRange=True))
        self.parameters.add("L", Parameter("Luminosity", "L", 1.))
        self.parameters.add("ai", Parameter("Daisy Albedo", "a<sub>i</sub>", 0.75, unitRange=True))
        self.parameters.add("ag", Parameter("Ground Albedo", "a<sub>g</sub>", 0.5, unitRange=True))
        self.parameters.add("R", Parameter("Insulation Constant", "R", 0.2, unitRange=True))
        self.parameters.add("S", Parameter("Solar Constant", "S", 917.))
        self.parameters.add("sigma", Parameter("Stefan-Boltzmann Constant", "σ", 5.67e-8))
        self.parameters.add("Ti", Parameter("Ideal Growth Temperature", "T<sub>i</sub>", 22.5))
        self.parameters.add("gamma", Parameter("Death Rate", "γ", 0.3, unitRange=True))

        self.setupEvolution()

    def v(self, A):  # dA/dt
        ap = A * self.parameters.ai.value + (1 - A) * self.parameters.ag.value  # planet albedo
        Te = (self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * (1 - ap)) ** 0.25  # planet temp
        T = (self.parameters.R.value * self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * \
            (ap - self.parameters.ai.value) + (Te ** 4)) ** 0.25  # daisy temp
        b = 1 - (0.003265 * ((273.15 + self.parameters.Ti.value) - T) ** 2)  # daisy growth rate
        return A * ((1 - A) * b - self.parameters.gamma.value)

    def setupEvolution(self):
        self.evolution = Parameters()
        self.evolution.add("t", Parameter("Time", "t", 0.))
        self.evolution.add("A", Parameter("Daisy Area", "A", self.parameters.A0.value))
        self.evolution.add("v", Parameter("Rate of Change of Daisy Area", "dA/dt", self.v(self.evolution.A.value)))

    def evolve(self, dt=.025):
        self.evolution.t.value += dt
        self.evolution.A.value += self.v(self.evolution.A.value) * dt
        self.evolution.v.value = self.v(self.evolution.A.value)

    def generateFigure(self, width, height, dpi):
        self.axes = []
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes.append(fig.add_subplot(121))
        self.axes.append(fig.add_subplot(122))
        self.axes[1].set_aspect("equal")
        return fig

    def drawBackground(self):
        As = np.linspace(0, 1, num=101)
        self.axes[1].plot(As, np.zeros(As.shape), ':', color="#8080ff")
        self.axes[1].plot(As, self.v(As), color="#8080ff")

        self.fixedPoints = []
        dp = 1e-5
        testvec = np.linspace(0, 1, num=21)
        for A0 in testvec:
            res = minimize(
                lambda A : self.v(A) ** 2,
                A0, method="nelder-mead", options={"xtol": 1e-7}
            )
            p = round(res.x[0], 5)
            if (p not in [fps.coords for fps in self.fixedPoints]) and (0 <= p <= 1):
                fp = FixedPoint([p])
                fp.stable = (self.v(p + dp) - self.v(p - dp) < 0)
                self.fixedPoints.append(fp)
        for fp in self.fixedPoints:
            self.axes[1].plot(fp.coords[0], 0, "b^" if fp.stable else "rv", markersize=12, clip_on=False)

        self.axes[0].set_xlabel("Time ($t$)")
        self.axes[0].set_ylabel("Daisy Area ($A$)")
        self.axes[0].set_ylim(0, 1)
        self.axes[1].set_xlabel("Daisy Area ($A$)")
        self.axes[1].set_ylabel("Rate of Change of Daisy Area ($dA/dt$)")
        self.axes[1].set_xlim(0, 1)

    def drawForeground(self):
        self.axes[0].plot(self.evolution.t.value, self.evolution.A.value, color="#ff8080", marker='o')
        self.axes[1].plot(self.evolution.A.value, self.evolution.v.value, color="#ff8080", marker='o')

class DaisyWorld2:
    def __init__(self):
        self.parameters = Parameters()
        self.parameters.add("Ab0", Parameter("Initial Black Daisy Area", "A<sub>b</sub><sup>t=0</sup>", 0.87, unitRange=True))
        self.parameters.add("Aw0", Parameter("Initial White Daisy Area", "A<sub>w</sub><sup>t=0</sup>", 0.11, unitRange=True))
        self.parameters.add("L", Parameter("Luminosity", "L", 1.))
        self.parameters.add("ab", Parameter("Black Daisy Albedo", "a<sub>b</sub>", 0.25, unitRange=True))
        self.parameters.add("aw", Parameter("White Daisy Albedo", "a<sub>w</sub>", 0.75, unitRange=True))
        self.parameters.add("ag", Parameter("Ground Albedo", "a<sub>g</sub>", 0.5, unitRange=True))
        self.parameters.add("R", Parameter("Insulation Constant", "R", 0.2, unitRange=True))
        self.parameters.add("S", Parameter("Solar Constant", "S", 917.))
        self.parameters.add("sigma", Parameter("Stefan-Boltzmann Constant", "σ", 5.67e-8))
        self.parameters.add("Ti", Parameter("Ideal Growth Temperature", "T<sub>i</sub>", 22.5))
        self.parameters.add("gamma", Parameter("Death Rate", "γ", 0.3, unitRange=True))

        self.setupEvolution()

    def vb(self, Ab, Aw):  # dA/dt of Black Daisy
        ap = Aw * self.parameters.aw.value + Ab * self.parameters.ab.value + (1 - Aw - Ab) * self.parameters.ag.value  # Planet Albedo
        Te = (self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * (1 - ap)) ** 0.25  # Planet Temp
        Tb = (self.parameters.R.value * self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * \
             (ap - self.parameters.ab.value) + (Te ** 4)) ** 0.25  # Black Daisy Temp
        bb = 1 - (0.003265 * ((273.15 + self.parameters.Ti.value) - Tb) ** 2)  # Black Daisy Growth Rate
        return Ab * ((1 - Ab - Aw) * bb - self.parameters.gamma.value)

    def vw(self, Ab, Aw):  # dA/dt of White Daisy
        ap = Aw * self.parameters.aw.value + Ab * self.parameters.ab.value + (1 - Aw - Ab) * self.parameters.ag.value  # Planet Albedo
        Te = (self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * (1 - ap)) ** 0.25  # Planet Temp
        Tw = (self.parameters.R.value * self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * \
             (ap - self.parameters.aw.value) + (Te ** 4)) ** 0.25  # White Daisy Temp
        bw = 1 - (0.003265 * ((273.15 + self.parameters.Ti.value) - Tw) ** 2)  # White Daisy Growth Rate
        return Aw * ((1 - Aw - Ab) * bw - self.parameters.gamma.value)
    
    def setupEvolution(self):
        self.evolution = Parameters()
        self.evolution.add("t", Parameter("Time", "t", 0.))
        self.evolution.add("Ab", Parameter("Black Daisy Area", "Ab", self.parameters.Ab0.value))
        self.evolution.add("Aw", Parameter("White Daisy Area", "Aw", self.parameters.Aw0.value))

    def evolve(self, dt=.05):
        self.evolution.t.value += dt
        self.evolution.Ab.value += self.vb(self.evolution.Ab.value, self.evolution.Aw.value) * dt
        self.evolution.Aw.value += self.vw(self.evolution.Ab.value, self.evolution.Aw.value) * dt

    def generateFigure(self, width, height, dpi):
        self.axes = []
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes.append(fig.add_subplot(121))
        self.axes.append(fig.add_subplot(122))
        self.axes[1].set_aspect("equal")
        return fig

    def drawBackground(self):
        Aws, Abs = np.mgrid[0:1:100j, 0:1:100j]
        vbs = self.vb(Abs, Aws)
        vws = self.vw(Abs, Aws)
        mask = np.zeros(vws.shape, dtype=bool)
        for i in range(len(vws)):
            vws[i, len(vws) - i:] = np.nan
            vws = np.ma.array(vws, mask=mask)
        self.axes[1].streamplot(Abs, Aws, vbs, vws, color="#8080ff", density=1.5)
        
        self.fixedPoints = []
        testvec = np.linspace(0, 1, num=21)
        for Ab0 in testvec:
            for Aw0 in testvec:
                if (Ab0 + Aw0) <= 1:
                    A0 = np.array([Ab0, Aw0])
                    res = minimize(
                        lambda A : self.vb(A[0], A[1]) ** 2 + self.vw(A[0], A[1]) ** 2,
                        A0, method="nelder-mead", options={'xtol': 1e-7}
                    )
                    pb = round(res.x[0], 5)
                    pw = round(res.x[1], 5)
                    if ([pb, pw] not in [fps.coords for fps in self.fixedPoints]) and ((pb + pw) <= 1) and (pb >= 0) and (pw >= 0):
                        fp = FixedPoint([pb, pw])
                        fp.stable = self._JacobianStability(fp)
                        self.fixedPoints.append(fp)
        for fp in self.fixedPoints:
            self.axes[1].plot(fp.coords[0], fp.coords[1], "b^" if fp.stable else "rv", markersize=12, clip_on=False)
    
        self.axes[0].set_xlabel("Time ($t$)")
        self.axes[0].set_ylabel("Daisy Area ($A$)")
        self.axes[0].set_ylim(0, 1)
        self.axes[1].set_xlabel("Daisy Area ($A$)")
        self.axes[1].set_ylabel("Rate of Change of Daisy Area ($dA/dt$)")
    
    def drawForeground(self):
        self.axes[0].plot(self.evolution.t.value, self.evolution.Ab.value, color="#ffc000", marker='o')
        self.axes[0].plot(self.evolution.t.value, self.evolution.Aw.value, color="#ff00c0", marker='o')
        self.axes[1].plot(self.evolution.Ab.value, self.evolution.Aw.value, color="#ff8000", marker='o')

    def _JacobianStability(self, fixedPoint):
        def partial_derivative(v, coords, idx):
            args = coords[:]
            def wraps(x):
                args[idx] = x
                return v(*args)
            return derivative(wraps, coords[idx], dx=1e-5)

        j00 = partial_derivative(self.vb, fixedPoint.coords, 0)
        j01 = partial_derivative(self.vb, fixedPoint.coords, 1)
        j10 = partial_derivative(self.vw, fixedPoint.coords, 0)
        j11 = partial_derivative(self.vw, fixedPoint.coords, 1)
        jacobian = np.array([[j00, j01], [j10, j11]])
        eigval, _ = np.linalg.eig(jacobian)
        return (eigval[0] < 0 and eigval[1] < 0)

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
