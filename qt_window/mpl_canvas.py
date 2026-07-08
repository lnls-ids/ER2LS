from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import apu
import numpy as np


class MplCanvas(FigureCanvas):

    def __init__(self):

        phases = np.linspace(0, 11, 100)
        b = apu.calc_field(phases)

        self.fig = Figure(figsize=(4, 3))
        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111)

        # # Cor do fundo
        # bg = (210/255, 210/255, 235/255)
        bg = (187/255, 187/255, 221/255)
        self.fig.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)

        # Grid
        self.ax.grid(
            True,
            linestyle='--',
            linewidth=0.5,
            alpha=0.5
        )

        # Fonte dos eixos
        self.ax.tick_params(
            labelsize=11,
            width=1.0,
            length=4
        )

        self.ax.set_xlabel(
            "Phase [mm]",
            fontsize=10,
            fontweight='bold'
        )

        self.ax.set_ylabel(
            "Field [T]",
            fontsize=10,
            fontweight='bold'
        )
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.spines['left'].set_linewidth(1.2)
        self.ax.spines['bottom'].set_linewidth(1.2)

        self.curve, = self.ax.plot(phases, b, 'b', lw=2)
        self.point, = self.ax.plot([], [], 'ro', markersize=8)

        self.fig.tight_layout(pad=1.2)
        self.draw()

    def update_point(self, phase):
        b = apu.calc_field(phase)
        self.point.set_data([phase], [b])
        self.draw_idle()
