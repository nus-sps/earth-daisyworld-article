import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        # Global Settings
        self.setWindowTitle("Daisyworld")
        self.setWindowIcon(qtg.QIcon('icon.ico'))
        self.setFont(qtg.QFont("Helvetica", 10))
        self.resize(2000, 1500)

        # Status Bar
        self.statusBar = qtw.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Hello!")

        # Menu Bar
        menubar = self.menuBar()
        menuHelp = menubar.addMenu("&Help")
        actionHelpAbout = qtw.QAction("&About", self)
        actionHelpAbout.triggered.connect(lambda: self._spawnWindow(AboutWindow))
        menuHelp.addAction(actionHelpAbout)

        # Main Widget
        mainWidget = qtw.QWidget(self)
        self.setCentralWidget(mainWidget)
        layout = qtw.QVBoxLayout()
        mainWidget.setLayout(layout)

        # Tabs
        tabs = qtw.QTabWidget()
        tabs.addTab(WorldTab(1), "One-Daisy")
        tabs.addTab(WorldTab(2), "Two-Daisy")
        layout.addWidget(tabs)

    def _spawnWindow(self, obj):
        self.window = obj()
        self.window.show()

class AboutWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daisyworld - About")
        self.setWindowIcon(qtg.QIcon('icon.ico'))
        self.setFont(qtg.QFont("Helvetica", 10))
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        label = qtw.QLabel()
        label.setText(
            "Welcome to Daisyworld GUI!<br/><br/>" + \
            "This is an interactive plotting programme that helps you visualise<br/>" + \
            "the dynamics of the Daisyworld climate model. Here, you can explore<br/>" + \
            "how the time evolution of the dynamical system is related to the<br/>" + \
            "trajectory in its state space.<br/><br/>" + \
            "Visit our <a href='https://github.com/nus-sps/earth-daisyworld-article'>Github repository page</a> for more.<br/><br/>" + \
            "More about us:<br/>" + \
            "<a href='http://sps.nus.edu.sg/'>Special Programme in Science, National University of Singapore</a>"
        )
        label.setOpenExternalLinks(True)
        layout.addWidget(label)

class WorldTab(qtw.QWidget):
    def __init__(self, dimension):
        super().__init__()
        self.dimension = dimension
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        # Initialize Daisyworld
        self.isRunning = False
        self.initDaisyWorld()

        # Parameter Input Boxes
        layoutInputBoxes = qtw.QFormLayout()
        self.inputboxes = []
        for p in self.DW.parameters:
            inputbox = self._newInputBox(str(p.value))
            self.inputboxes.append(inputbox)
            layoutInputBoxes.addRow("{} ({})".format(p.name, p.short), inputbox)

        # Buttons
        layoutButtons = qtw.QHBoxLayout()
        self.buttons = [
            self._newButton("Restore default values"),
            self._newButton("Stop"),
            self._newButton("Run!")
        ]
        self.buttons[0].clicked.connect(self._restore)
        self.buttons[1].clicked.connect(self._stop)
        self.buttons[2].clicked.connect(self._run)
        layoutButtons.addStretch()
        for b in self.buttons:
            layoutButtons.addWidget(b)

        # Plots
        layoutPlots = qtw.QHBoxLayout()
        self.canvas = PlotCanvas()
        layoutPlots.addWidget(self.canvas)

        # And finally...
        layout.addLayout(layoutInputBoxes)
        layout.addLayout(layoutButtons)
        layout.addLayout(layoutPlots)

    def initDaisyWorld(self):
        if self.dimension == 1:
            self.DW = DaisyWorld1()
        elif self.dimension == 2:
            self.DW = DaisyWorld2()

    def _newInputBox(self, text, width=300):
        inputbox = qtw.QLineEdit()
        inputbox.setText(text)
        inputbox.setFixedWidth(width)
        return inputbox
    
    def _newButton(self, text, width=300, function=None, *args):
        button = qtw.QPushButton("&{}".format(text))
        button.setFixedWidth(width)
        if function is not None:
            button.clicked.connect(lambda: function(*args))
        return button
    
    def _restore(self):
        choice = qtw.QMessageBox.question(
            self,
            "Restore Warning!",
            "Are you sure you want to restore the default values?",
            qtw.QMessageBox.Yes | qtw.QMessageBox.No
        )
        if choice == qtw.QMessageBox.Yes:
            self.initDaisyWorld()
            # Restoring part here
            for i in range(len(self.inputboxes)):
                self.inputboxes[i].setText(str(self.DW.parameters[i].value))

    def _stop(self):
        self.isRunning = False
        self.initDaisyWorld()
        self._toggleRun()
        self.canvas.figClear()

    def _run(self):
        self.isRunning = not self.isRunning
        self._toggleRun()
    
    def _toggleRun(self):
        if self.isRunning:
            self.buttons[2].setText("Pause")
            self.canvas.timer.start(200)
        else:
            self.buttons[2].setText("Run!")
            self.canvas.timer.stop()

class PlotCanvas(FigureCanvas):
    def __init__(self, width=10, height=12, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.tip = fig.add_subplot(121)
        self.ssp = fig.add_subplot(122)
        FigureCanvas.__init__(self, fig)

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.figUpdate)

    def figUpdate(self):
        l = [np.random.randint(0, 10) for i in range(4)]
        self.tip.plot([0, 1, 2, 3], l, 'r')
        self.ssp.plot([0,1,2,3], l, 'b')
        self.draw()

    def figClear(self):
        self.tip.cla()
        self.ssp.cla()
        self.draw()

class DaisyWorld1:
    def __init__(self):
        self.parameters = []
        self._add_parameter("L", Parameter("Luminosity", "L", 1.))
        self._add_parameter("ai", Parameter("Daisy Albedo", "a<sub>i</sub>", 0.75))
        self._add_parameter("ag", Parameter("Ground Albedo", "a<sub>g</sub>", 0.5))
        self._add_parameter("R", Parameter("Insulation Constant", "R", 0.2))
        self._add_parameter("S", Parameter("Solar Constant", "S", 917))
        self._add_parameter("sigma", Parameter("Stefan-Boltzmann Constant", "σ", 5.67e-8))
        self._add_parameter("Ti", Parameter("Ideal Growth Temperature", "T<sub>i</sub>", 22.5))
        self._add_parameter("gamma", Parameter("Death Rate", "γ", 0.3))

    def _add_parameter(self, attribute, parameter):
        setattr(self, attribute, parameter)
        self.parameters.append(parameter)

    # dA/dt Function
    def v(self, A):
        ap = A * self.ai.value + (1 - A) * self.ag.value  # Planet Albedo
        Te = (self.L.value * (self.S.value / self.sigma.value) * (1 - ap)) ** 0.25  # Planet Temp
        T = (self.R.value * self.L.value * (self.S.value / self.sigma.value) * \
            (ap - self.ai.value) + (Te ** 4)) ** 0.25  # Black Daisy Temp
        b = 1 - (0.003265 * ((273.15 + self.Ti.value) - T) ** 2)  # Black Daisy Growth Rate
        return A * ((1 - A) * b - self.gamma.value)

class DaisyWorld2:
    def __init__(self):
        self.parameters = []
        self._add_parameter("L", Parameter("Luminosity", "L", 1.))
        self._add_parameter("ab", Parameter("Black Daisy Albedo", "a<sub>b</sub>", 0.25))
        self._add_parameter("aw", Parameter("White Daisy Albedo", "a<sub>w</sub>", 0.75))
        self._add_parameter("ag", Parameter("Ground Albedo", "a<sub>g</sub>", 0.5))
        self._add_parameter("R", Parameter("Insulation Constant", "R", 0.2))
        self._add_parameter("S", Parameter("Solar Constant", "S", 917))
        self._add_parameter("sigma", Parameter("Stefan-Boltzmann Constant", "σ", 5.67e-8))
        self._add_parameter("Ti", Parameter("Ideal Growth Temperature", "T<sub>i</sub>", 22.5))
        self._add_parameter("gamma", Parameter("Death Rate", "γ", 0.3))

    def _add_parameter(self, attribute, parameter):
        setattr(self, attribute, parameter)
        self.parameters.append(parameter)

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

class Parameter(object):
    def __init__(self, name, short, value):
        self.name = name
        self.short = short
        self.value = value

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())