import numpy as np
import h5py
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


def read_data(fname):

    energy = []
    flux = []
    exp_time = []
    images = {}
    max_intensity = []
    max_intensity_global = 0

    with h5py.File(fname, 'r') as f:
        group = f['images']
        keys = list(group.keys())

        for i in range(len(keys)):
            energy.append(group[keys[i]].attrs['energy_mon'])
            flux.append(group[keys[i]].attrs['flux_mon'])
            exp_time.append([group[keys[i]].attrs['exp_time_mon'],
                            group[keys[i]].attrs['exp_time_sp']])
            images[keys[i]] = np.array(group[keys[i]])
            max_intensity.append(group[keys[i]].attrs['max_intensity'])
            max_intensity_global = np.max([max_intensity_global,
                                    group[keys[i]].attrs['max_intensity']])

    energy = np.array(energy)
    exp_time = np.array(exp_time)
    flux = np.array(flux) / exp_time[:, 0]
    # flux /= np.max(flux)
    max_intensity = np.array(max_intensity)

    return energy, flux, images, max_intensity_global


def plot_one_flux(fname):
    energy, flux, images, _ = read_data(fname)
    fig, ax = plt.subplots()
    ax.plot(energy, flux, 'o-')
    ax.set_xlabel('Energy [keV]')
    ax.set_ylabel('Flux [a.u.]')
    ax.grid(alpha=0.3)
    ax.minorticks_on()
    ax.tick_params(which='both', axis='both', direction='in', top=True, right=True)
    plt.show()


def plot_flux_both(fname1, fname2):
    energy1, flux1, images1, _ = read_data(fname1)
    energy2, flux2, images2, _ = read_data(fname2)
    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    ax.plot(energy1, flux1, '-', label='Open Slits')
    ax.plot(energy2, flux2, '-', label='Closed Slits')
    ax.set_xlabel('Energy [keV]')
    ax.set_ylabel('Flux [a.u.]')
    ax.grid(alpha=0.3)
    ax.legend()
    ax.minorticks_on()
    ax.tick_params(which='both', axis='both', direction='in', top=True, right=True)
    fig.tight_layout()
    plt.show()


class SpectrumPlayer(QMainWindow):

    def __init__(self, fname):
        super().__init__()

        self.energy, self.flux, self.images, _ = read_data(fname)

        self.setWindowTitle("Spectrum Animation")

        self.fig = Figure(figsize=(9, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)

        self.setCentralWidget(self.canvas)

        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

        # ---------- Flux plot ----------

        self.line, = self.ax1.plot([], [], '.-k')

        self.ax1.set_xlim(
            self.energy.min(),
            self.energy.max()
        )

        self.ax1.set_ylim(
            0,
            np.max(self.flux)
        )

        self.ax1.set_title("Flux vs Energy")
        self.ax1.set_xlabel("Energy [keV]")
        self.ax1.set_ylabel("Flux [a.u.]")

        # ---------- Image ----------

        self.first_img = self.images["img_001"]

        self.im = self.ax2.imshow(
            self.first_img,
            cmap="viridis",
            origin="lower",
            vmin=0,
            vmax=999
        )

        self.ax2.set_title("Image")
        self.ax2.set_xlabel("X [px]")
        self.ax2.set_ylabel("Y [px]")

        self.cbar = self.fig.colorbar(
            self.im,
            ax=self.ax2,
            fraction=0.046,
            pad=0.04
        )

        self.cbar.set_label("Intensity [a.u.]")

        self.fig.tight_layout()

        # ---------- Animation ----------

        self.frame = 0

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.next_frame
        )

    def start(self):

        self.frame = 0

        self.line.set_data([], [])

        self.im.set_data(
            np.zeros_like(self.first_img)
        )

        self.canvas.draw()

        self.timer.start(300)

    def next_frame(self):

        self.line.set_data(
            self.energy[:self.frame + 1],
            self.flux[:self.frame + 1]
        )

        key = f"img_{self.frame + 1:03d}"

        if key in self.images:
            self.im.set_data(
                self.images[key]
            )

        self.canvas.draw_idle()

        self.frame += 1

        if self.frame >= len(self.energy):
            self.timer.stop()
