#!/usr/bin/env python-sirius

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import apu
from hddcm import DCM
import time
from slit import WBS1, FOES
from dvf import DVF
from scan import Scan
from ui_mainwindow import Ui_MainWindow
import os
import epics
from apu_widget import APUWidget
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
from mpl_canvas import MplCanvas
from spectrum_canvas import SpectrumCanvas
import plots
from functools import partial
import resources_rc  # noqa: F401


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        os.environ['EPICS_CA_ADDR_LIST'] = '10.33.34.32 10.33.34.29 10.39.50.76 10.0.38.143 10.128.249.20'

        self.und = None
        self.dcm = None
        self.wbs = None
        self.foe = None
        self.dvf = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.canvas = MplCanvas()
        self.spectrum_canvas = SpectrumCanvas()

        layout = QVBoxLayout(self.ui.SpectrumplotWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spectrum_canvas)

        layout = QVBoxLayout(self.ui.FieldplotWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.wbs = WBS1()
        self.foe = FOES()
        self.dvf = DVF()
        self.apu_widget = APUWidget(self.ui.graphicsViewAPU)

        self.connect_undulator()
        self.connect_dcm()

        self.initial_verifications()

        # Undulator functions
        self.ui.Und_Connect_Button.clicked.connect(self.connect_undulator)
        self.ui.Und_Phase_Button.clicked.connect(self.calc_phase)
        self.ui.Und_Move_Button.clicked.connect(self.move_und)

        # DCM functions
        self.ui.DCM_Connect_Button.clicked.connect(self.connect_dcm)
        self.ui.DCM_Move_Button.clicked.connect(self.move_dcm)

        # Slits functions
        self.ui.WBS_Close_Button.clicked.connect(self.close_wbs)
        self.ui.WBS_Ref_Button.clicked.connect(self.set_ref_wbs)
        self.ui.WBS_Open_Button.clicked.connect(self.open_wbs)
        self.ui.WBS_Motor_Button.clicked.connect(self.set_wbs_motor)

        self.ui.FOE_Close_Button.clicked.connect(self.close_foe)
        self.ui.FOE_Ref_Button.clicked.connect(self.set_ref_foe)
        self.ui.FOE_Open_Button.clicked.connect(self.open_foe)
        self.ui.FOE_Motor_Button.clicked.connect(self.set_foe_motor)

        # DVF functions
        self.ui.DVF_Acq_Button.clicked.connect(self.start_stop_acquire)
        self.ui.ROI_Define_Button.clicked.connect(self.set_roi)
        self.ui.ROI_Disable_Button.clicked.connect(self.reset_roi)

        # Scan functions
        self.ui.FileButton.clicked.connect(self.select_input_file)
        self.ui.Scan_Button.clicked.connect(self.start_scan)

        # Plot functions
        self.ui.SpectrumSpinXMax.valueChanged.connect(self.update_axes)
        self.ui.SpectrumSpinXMin.valueChanged.connect(self.update_axes)
        self.ui.verticalSlider.valueChanged.connect(self.observation_changed)
        self.ui.AngleSpinBox.valueChanged.connect(self.observation_changed_spin)

        # Plot results functions
        self.ui.PlotFileButton_1.clicked.connect(partial(
            self.select_input_file_plot,
            self.ui.PlotInputFile_lineEdit_1,
            self.ui.PlotFileStatus_1,
        )
        )
        self.ui.PlotFileButton_2.clicked.connect(partial(
            self.select_input_file_plot,
            self.ui.PlotInputFile_lineEdit_2,
            self.ui.PlotFileStatus_2,
        )
        )

        self.ui.PlotFileButtonGif_1.clicked.connect(partial(
            self.plot_gif,
            self.ui.PlotInputFile_lineEdit_1,
            self.ui.PlotFileStatus_1,
        ))

        self.ui.PlotFileButtonGif_2.clicked.connect(partial(
            self.plot_gif,
            self.ui.PlotInputFile_lineEdit_2,
            self.ui.PlotFileStatus_2,
        ))

        self.ui.PlotFileButtonFlux_1.clicked.connect(partial(
            self.plot_flux,
            self.ui.PlotInputFile_lineEdit_1,
            self.ui.PlotFileStatus_1,

        ))

        self.ui.PlotFileButtonFlux_2.clicked.connect(partial(
            self.plot_flux,
            self.ui.PlotInputFile_lineEdit_2,
            self.ui.PlotFileStatus_2,

        ))

        self.ui.PlotFileButtonBoth.clicked.connect(
            self.plot_flux_both
        )

    def initial_verifications(self):
        if self.wbs.verify_motors_enable():
            self.set_led(self.ui.WBS_status_led, 'green')
            self.ui.WBS_Motor_Button.setText('Disable')
        else:
            self.set_led(self.ui.WBS_status_led, 'red')
            self.ui.WBS_Motor_Button.setText('Enable')

        if self.foe.verify_motors_enable():
            self.set_led(self.ui.FOE_status_led, 'green')
            self.ui.FOE_Motor_Button.setText('Disable')
        else:
            self.set_led(self.ui.FOE_status_led, 'red')
            self.ui.FOE_Motor_Button.setText('Enable')

        value = epics.caget(self.dvf.dvf_acquire)
        if value:
            self.set_led(self.ui.DVF_status_led, 'green')
            self.ui.DVF_Acq_Button.setText("Stop Acq.")
        else:
            self.set_led(self.ui.DVF_status_led, 'red')
            self.ui.DVF_Acq_Button.setText("Start Acq.")

    # LED functions
    def set_led(self, led, color):
        colors = {
            "green": "rgb(0,220,0)",
            "red": "rgb(220,0,0)",
            "yellow": "rgb(255,200,0)",
            "gray": "rgb(120,120,120)"
        }

        led.setStyleSheet(f"""
        QLabel {{
            background-color: {colors[color]};
            border-radius: 8px;
            border: 1px solid black;
        }}
        """)

    # Undulator related functions
    def connect_undulator(self):
        self.und = apu.initialize_apu(beamline='SAPUCAIA')
        time.sleep(1)
        if self.und.connected:
            self.set_led(self.ui.Und_status_led, 'green')
        else:
            self.set_led(self.ui.Und_status_led, 'red')

    def calc_phase(self):
        energy = float(self.ui.Energy_edit.text())
        harmonic = float(self.ui.Harmonic_edit.text())
        phase = apu.get_phase_from_energy(energy, harmonic)
        if not np.isnan(phase):
            k = apu.calc_k(phase)
            self.ui.Und_Phase_label.setText(f"Phase: {phase:.4f} mm")
            self.ui.Und_Klabel.setText(f"K =  {k:.4f}")
            self.apu_widget.set_phase(phase)
        else:
            self.ui.Und_Phase_label.setText("Harmonic not possible!")
        self.canvas.update_point(phase)
        theta = float(self.ui.AngleSpinBox.value())
        self.spectrum_canvas.update_spectrum(phase, theta)

    def move_und(self):
        phase_str = self.ui.Und_Phase_label.text()
        phase = float(phase_str.split(": ")[1].strip().split()[0])
        self.und.cmd_move(kparam=phase)

    # DCM related functions
    def connect_dcm(self):
        self.dcm = DCM(timeout=3)
        time.sleep(1)
        if self.dcm.energy_mon is not None:
            self.set_led(self.ui.DCM_status_led, 'green')
        else:
            self.set_led(self.ui.DCM_status_led, 'red')

    def move_dcm(self):
        energy = float(self.ui.Energy_edit.text())
        self.dcm.cmd_move_robust(energy, 5)

    # Slits related functions
    def close_wbs(self):
        self.wbs.set_slits_closed()

    def set_ref_wbs(self):
        self.wbs.set_slits_ref()

    def open_wbs(self):
        self.wbs.set_slits_open()

    def set_wbs_motor(self):
        self.wbs.set_motors()
        if self.wbs.verify_motors_enable():
            self.set_led(self.ui.WBS_status_led, 'green')
            self.ui.WBS_Motor_Button.setText('Disable')
        else:
            self.set_led(self.ui.WBS_status_led, 'red')
            self.ui.WBS_Motor_Button.setText('Enable')

    def close_foe(self):
        self.foe.set_slits_closed()

    def set_ref_foe(self):
        self.foe.set_slits_ref()

    def open_foe(self):
        self.foe.set_slits_open()

    def set_foe_motor(self):
        self.foe.set_motors()
        if self.foe.verify_motors_enable():
            self.set_led(self.ui.FOE_status_led, 'green')
            self.ui.FOE_Motor_Button.setText('Disable')
        else:
            self.set_led(self.ui.FOE_status_led, 'red')
            self.ui.FOE_Motor_Button.setText('Enable')

    # DVF related functions
    def start_stop_acquire(self):
        self.dvf.start_stop_acquire()
        value = epics.caget(self.dvf.dvf_acquire)
        if value:
            self.set_led(self.ui.DVF_status_led, 'green')
            self.ui.DVF_Acq_Button.setText("Stop Acq.")
        else:
            self.set_led(self.ui.DVF_status_led, 'red')
            self.ui.DVF_Acq_Button.setText("Start Acq.")

    def set_roi(self):
        roi_shape_x = int(self.ui.ROI_shape_x_edit.text())
        roi_shape_y = int(self.ui.ROI_shape_y_edit.text())
        roi_start_x = int(self.ui.ROI_start_x_edit.text())
        roi_start_y = int(self.ui.ROI_start_y_edit.text())
        roi_shape = (roi_shape_y, roi_shape_x)
        roi_start = (roi_start_y, roi_start_x)
        self.dvf.define_ROI(roi_shape, roi_start)

    def reset_roi(self):
        self.dvf.disable_ROI()

    # Scan related functions
    def select_input_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "Text files (*.txt)"
        )

        if filename:
            self.ui.InputFile_lineEdit.setText(filename)
            self.scan = Scan(fname=filename, dcm=self.dcm, dvf=self.dvf)
            self.scan.load_scan_points()
            nr_pts = len(self.scan.scanPoints[:, 0])
            min_energy = self.scan.scanPoints[0, 0]
            max_energy = self.scan.scanPoints[-1, 0]
            self.ui.Scan_nrpoints.setText("Nr. points: {:.0f}".format(nr_pts))
            self.ui.Scan_min_energy.setText("Min. energy: {:.1f} KeV".format(min_energy))
            self.ui.Scan_max_energy.setText("Max. energy: {:.1f} KeV".format(max_energy))

    def start_scan(self):
        self.scan.do_scan(
            progress_callback=self.update_progress
        )

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        QApplication.processEvents()

    # Plot related functions
    def update_axes(self):

        xmin = self.ui.SpectrumSpinXMin.value()
        xmax = self.ui.SpectrumSpinXMax.value()

        self.spectrum_canvas.ax.set_xlim(xmin, xmax)
        self.spectrum_canvas.draw_idle()

    def observation_changed(self, value):
        theta = value
        self.ui.AngleSpinBox.setValue(theta)
        self.update_spectrum(theta)

    def observation_changed_spin(self, value):
        theta = value
        self.ui.AngleSpinBox.setValue(theta)
        self.ui.verticalSlider.setValue(theta)
        self.update_spectrum(theta)

    def update_spectrum(self, theta):
        phase = float(self.ui.Und_Phase_label.text().split(": ")[1].strip().split()[0])
        self.spectrum_canvas.update_spectrum(
            phase,
            theta,
        )

    # PLot results related functions
    def select_input_file_plot(self, line_edit, label):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "HDF5 (*.h5)"
        )

        if filename:
            *_, max_intensity = plots.read_data(filename)
            line_edit.setText(filename)
            label.setText('File OK. max. intensity = {:0d}/1024'.format(max_intensity))

    def plot_gif(self, line_edit, label):
        if label.text().split('.')[0] == 'File OK':
            fname = line_edit.text()
            self.player = plots.SpectrumPlayer(fname)
            self.player.show()
            self.player.start()
        else:
            label.setText('Select a valid file first!')

    def plot_flux(self, line_edit, label):
        if label.text().split('.')[0] == 'File OK':
            fname = line_edit.text()
            plots.plot_one_flux(fname)
        else:
            label.setText('Select a valid file first!')

    def plot_flux_both(self):
        label1 = self.ui.PlotFileStatus_1.text().split('.')[0]
        label2 = self.ui.PlotFileStatus_2.text().split('.')[0]
        if label1 == 'File OK' and label2 == 'File OK':
            fname1 = self.ui.PlotInputFile_lineEdit_1.text()
            fname2 = self.ui.PlotInputFile_lineEdit_2.text()
            plots.plot_flux_both(fname1, fname2)
        else:
            self.ui.PlotFileStatus_1.setText('Select valid files first!')
            self.ui.PlotFileStatus_2.setText('Select valid files first!')


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
