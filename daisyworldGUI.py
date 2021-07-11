# This file is part of the Daisyworld project <https://github.com/nus-sps/earth-daisyworld-article>
# The project is licensed under the terms of GPL-3.0-or-later. <https://www.gnu.org/licenses/>
# Author: Kun Hee Park

from ast import parse
import numpy as np
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
        # tabs.addTab(WorldTab(2), "Two-Daisy")
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

class LicenseWindow(qtw.QWidget):
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
            if v.unitRange:
                layoutInputBoxes.addRow("{}* ({})".format(v.name, v.short), inputbox)
            else:
                layoutInputBoxes.addRow("{} ({})".format(v.name, v.short), inputbox)

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
            if self.bifurcation:
                self.canvas = None # PlotCanvas1bif(self.DW)
            else:
                self.canvas = PlotCanvas(self.DW)
        elif self.dimension == 2:
            self.DW = DaisyWorld2()
            if self.bifurcation:
                self.canvas = None # PlotCanvas2bif(self.DW)
            else:
                self.canvas = None #PlotCanvas2(self.DW)

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
            if self.canvas.isRunning:
                self.buttons[1].setText("Rerun!")
                self.canvas.figStop()
                self.canvas.isRunning = not self.canvas.isRunning
            self.DW.parameters.reset()
            self._dw2box()
            self.canvas.figClear()

    def _run(self):
        if self.canvas.isRunning:
            self.buttons[1].setText("Rerun!")
            self.canvas.figStop()
            self.canvas.isRunning = not self.canvas.isRunning
        else:
            try:
                self._box2dw()
                self.DW.setupBackground()
                self.DW.setupEvolution()
                self.canvas.updateDaisyWorld(self.DW)
                self.buttons[1].setText("Stop")
                self.canvas.figClear()
                self.canvas.figInit()
                self.canvas.figRun()
                self.canvas.isRunning = not self.canvas.isRunning
                self.buttons[1].setStyleSheet("color: black; font-size: 27px")
            except Exception as e:
                self.buttons[1].setStyleSheet("color: red; font-size: 27px")

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
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.DW = daisyWorld
        self.tip = fig.add_subplot(121)
        self.ssp = fig.add_subplot(122)
        self.figInit()
        FigureCanvas.__init__(self, fig)

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.figUpdate)
    
    def updateDaisyWorld(self, daisyWorld):
        self.DW = daisyWorld

    def figRun(self, milliseconds=0):
        self.timer.start(milliseconds)
    
    def figStop(self):
        self.timer.stop()

    def figInit(self):
        x = self.DW.x
        y = self.DW.y
        self.ssp.plot(x, np.zeros(x.shape), ':', color='#8080ff')  # zero line
        self.ssp.plot(x, y, '-', color='#8080ff')
        self._drawFixedPoints()
        self._axesSet()

    def figUpdate(self):
        self.flush_events()
        self.DW.evolve()
        self.tip.plot(self.DW.evolution.t.value, self.DW.evolution.A.value, color='#ff8080', marker='o')
        self.ssp.plot(self.DW.evolution.A.value, self.DW.evolution.v.value, color='#ff8080', marker='o')
        self._axesSet()
        self.draw()

    def figClear(self):
        self.tip.cla()
        self.ssp.cla()
        self.figInit()
        self.draw()

    def _drawFixedPoints(self):
        labels = {'s': 'Stable', 'u': 'Unstable'}
        for fp in self.DW.fixedPoints:
            c = fp.coords + [0]
            if fp.stable:
                self.ssp.plot(c[0], c[1], 'b^', markersize=12, clip_on=False, label=labels['s'])
                labels['s'] = '_nolegend_'
            else:
                self.ssp.plot(c[0], c[1], 'rv', markersize=12, clip_on=False, label=labels['u'])
                labels['u'] = '_nolegend_'

    def _axesSet(self):
        self.tip.set_xlabel('{} (${}$)'.format(self.DW.evolution.t.name, self.DW.evolution.t.short))
        self.tip.set_ylabel('Daisy Area ($A$)')
        self.tip.set_ylim(0, 1)
        self.ssp.set_xlabel('Daisy Area ($A$)')
        self.ssp.set_ylabel('$dA/dt$')
        self.ssp.set_xlim(0, 1)

class PlotCanvas2(FigureCanvas):
    def __init__(self, daisyWorld, dt=0.1, width=10, height=12, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.DW = daisyWorld
        self.dt = dt
        self.tip = fig.add_subplot(121)
        self.ssp = fig.add_subplot(122)
        self.figInit()
        FigureCanvas.__init__(self, fig)

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.figUpdate)

    def updateDaisyWorld(self, daisyWorld):
        self.DW = daisyWorld

    def figRun(self, milliseconds=0):
        self.timer.start(milliseconds)
    
    def figStop(self):
        self.timer.stop()

    def figInit(self):
        Aws, Abs = np.mgrid[0:1:100j, 0:1:100j]
        vbs = self.DW.vb(Abs, Aws)
        vws = self.DW.vw(Abs, Aws)
        mask = np.zeros(vws.shape, dtype=bool)
        for i in range(len(vws)):
            vws[i, len(vws) - i:] = np.nan
            vws = np.ma.array(vws, mask=mask)
        self.ssp.streamplot(Abs, Aws, vbs, vws, color='#8080ff', density=1.5)
        self._axesSet()
        self.time = []
        self.areasB = []
        self.areasW = []
        self.velosB = []
        self.velosW = []
        self.t = 0
        self.Ab = self.DW.Ab0.value
        self.Aw = self.DW.Aw0.value

    def figUpdate(self):
        self.t += self.dt
        self.Ab += self.DW.vb(self.Ab, self.Aw) * self.dt
        self.Aw += self.DW.vw(self.Ab, self.Aw) * self.dt
        self.vb = self.DW.vb(self.Ab, self.Aw)
        self.vw = self.DW.vw(self.Ab, self.Aw)
        self.time.append(self.t)
        self.areasB.append(self.Ab)
        self.areasW.append(self.Aw)
        self.velosB.append(self.vb)
        self.velosW.append(self.vw)
        self.flush_events()
        self.tip.plot(self.time[-1], self.areasB[-1], color='#ffC000', marker='o')
        self.tip.plot(self.time[-1], self.areasW[-1], color='#ff00C0', marker='o')
        self.ssp.plot(self.areasB[-1], self.areasW[-1], color='#ff8080', marker='o')
        self._axesSet()
        self.draw()

    def figClear(self):
        self.tip.cla()
        self.ssp.cla()
        self.figInit()
        self.draw()
    
    def _axesSet(self):
        self.tip.set_xlabel('Time ($t$)')
        self.tip.set_ylabel('Daisy Area ($A$)')
        self.tip.set_ylim(0, 1)
        self.ssp.set_xlabel('Daisy Area ($A$)')
        self.ssp.set_ylabel('$dA/dt$')
        self.ssp.set_xlim(-0.05, 1.05)
        self.ssp.set_ylim(-0.05, 1.05)

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

        self.setupBackground()
        self.setupEvolution()

    def setupBackground(self):  # state space background
        self.x = np.linspace(0, 1, num=101)
        self.y = self.v(self.x)
        self.findFixedPoints()
    
    def setupEvolution(self):
        self.evolution = Parameters()
        self.evolution.add("t", Parameter("Time", "t", 0.))
        self.evolution.add("A", Parameter("Daisy Area", "A", self.parameters.A0.value))
        self.evolution.add("v", Parameter("Rate of Change of Daisy Area", "dA/dt", self.v(self.evolution.A.value)))

    def evolve(self, dt=0.025):
        self.evolution.t.value += dt
        self.evolution.A.value += self.v(self.evolution.A.value) * dt
        self.evolution.v.value = self.v(self.evolution.A.value)

    def v(self, A):  # dA/dt
        ap = A * self.parameters.ai.value + (1 - A) * self.parameters.ag.value  # planet albedo
        Te = (self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * (1 - ap)) ** 0.25  # planet temp
        T = (self.parameters.R.value * self.parameters.L.value * (self.parameters.S.value / self.parameters.sigma.value) * \
            (ap - self.parameters.ai.value) + (Te ** 4)) ** 0.25  # daisy temp
        b = 1 - (0.003265 * ((273.15 + self.parameters.Ti.value) - T) ** 2)  # daisy growth rate
        return A * ((1 - A) * b - self.parameters.gamma.value)

    def findFixedPoints(self):
        self.fixedPoints = []
        dp = 1e-5
        testvec = np.linspace(0, 1, num=21)
        for A0 in testvec:
            p = round(minimize(lambda A : self.v(A) ** 2, A0, method='nelder-mead', options={'xtol': 1e-7}).x[0], 5)
            if (p not in self.fixedPoints) and (0 <= p <= 1):
                fp = FixedPoint([p])
                fp.stable = (self.v(p + dp) - self.v(p - dp) < 0)
                self.fixedPoints.append(fp)

class DaisyWorld2:
    def __init__(self):
        self.parameters = []
        self._addParameter("Ab0", Parameter("Initial Black Daisy Area", "A<sub>b</sub><sup>t=0</sup>", 0.87, unitRange=True))
        self._addParameter("Aw0", Parameter("Initial White Daisy Area", "A<sub>w</sub><sup>t=0</sup>", 0.11, unitRange=True))
        self._addParameter("L", Parameter("Luminosity", "L", 1.))
        self._addParameter("ab", Parameter("Black Daisy Albedo", "a<sub>b</sub>", 0.25, unitRange=True))
        self._addParameter("aw", Parameter("White Daisy Albedo", "a<sub>w</sub>", 0.75, unitRange=True))
        self._addParameter("ag", Parameter("Ground Albedo", "a<sub>g</sub>", 0.5, unitRange=True))
        self._addParameter("R", Parameter("Insulation Constant", "R", 0.2, unitRange=True))
        self._addParameter("S", Parameter("Solar Constant", "S", 917.))
        self._addParameter("sigma", Parameter("Stefan-Boltzmann Constant", "σ", 5.67e-8))
        self._addParameter("Ti", Parameter("Ideal Growth Temperature", "T<sub>i</sub>", 22.5))
        self._addParameter("gamma", Parameter("Death Rate", "γ", 0.3, unitRange=True))

    def _addParameter(self, attribute, parameter):
        setattr(self, attribute, parameter)
        self.parameters.append(parameter)

    def restoreDefaults(self):
        for p in self.parameters:
            p.resetValue()

    # dA/dt of Black Daisy
    def vb(self, Ab, Aw):
        ap = Aw * self.aw.value + Ab * self.ab.value + (1 - Aw - Ab) * self.ag.value  # Planet Albedo
        Te = (self.L.value * (self.S.value / self.sigma.value) * (1 - ap)) ** 0.25  # Planet Temp
        Tb = (self.R.value * self.L.value * (self.S.value / self.sigma.value) * \
             (ap - self.ab.value) + (Te ** 4)) ** 0.25  # Black Daisy Temp
        bb = 1 - (0.003265 * ((273.15 + self.Ti.value) - Tb) ** 2)  # Black Daisy Growth Rate
        return Ab * ((1 - Ab - Aw) * bb - self.gamma.value)

    # dA/dt of White Daisy
    def vw(self, Ab, Aw):
        ap = Aw * self.aw.value + Ab * self.ab.value + (1 - Aw - Ab) * self.ag.value  # Planet Albedo
        Te = (self.L.value * (self.S.value / self.sigma.value) * (1 - ap)) ** 0.25  # Planet Temp
        Tw = (self.R.value * self.L.value * (self.S.value / self.sigma.value) * \
             (ap - self.aw.value) + (Te ** 4)) ** 0.25  # White Daisy Temp
        bw = 1 - (0.003265 * ((273.15 + self.Ti.value) - Tw) ** 2)  # White Daisy Growth Rate
        return Aw * ((1 - Aw - Ab) * bw - self.gamma.value)

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
