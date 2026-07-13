from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from apu import calc_field
from undulator_radiation import calc_flux_density


class SpectrumCanvas(FigureCanvas):

    def __init__(self):

        self.lines = []
        self.fig = Figure(figsize=(5, 3))
        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111)

        # Cor de fundo
        bg = (187/255, 187/255, 221/255)

        self.fig.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)

        # Aparência
        self.ax.grid(
            True,
            linestyle='--',
            linewidth=0.5,
            alpha=0.5
        )

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.set_xlabel(
            "Energy (keV)",
            fontsize=10,
            fontweight='bold'
        )

        self.ax.set_ylabel(
            "Flux (ph/s/0.1%BW/mrad^2)",
            fontsize=10,
            fontweight='bold'
        )

        self.ax.tick_params(
            labelsize=10,
            direction='in',
            length=5
        )

        # Curva do espectro
        self.line, = self.ax.plot(
            [],
            [],
            color="#0B5FA5",
            linewidth=2
        )
        self.ax.set_xlim(0, 20)

        self.fig.tight_layout()

    def update_spectrum(self, phase):
        b = calc_field(phase)
        energy, flux = calc_flux_density(b, 0)
        energy *= 1e-3
        # Cria linhas caso ainda não existam
        while len(self.lines) < len(energy):
            line, = self.ax.plot([], [], lw=2)
            self.lines.append(line)

        # Atualiza cada harmônica
        for line, e, f in zip(self.lines, energy, flux):
            line.set_color('C0')
            line.set_data(e, f)

        self.ax.relim()
        self.ax.autoscale_view()

        self.draw_idle()
        self.draw_idle()
