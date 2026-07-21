import numpy as np
import matplotlib.pyplot as plt
import time
import epics


class DCM():

    def __init__(self, timeout):
        # Define PVs
        self.prefix_dcm = 'SPU:A:DCM01:'
        self.dcm_sp = self.prefix_dcm + 'GonRx_GantrySP'
        self.dcm_rb = self.prefix_dcm + 'GonRx_GantrySP_RBV'
        self.dcm_move = self.prefix_dcm + 'EnergyUpdate_SP'
        self.dcm_energy_sp = self.prefix_dcm + 'Energy_SP'
        self.dcm_energy_rb = self.prefix_dcm + 'GonRx_Energy_RBV'
        self.dcm_energy_update = self.prefix_dcm + 'EnergyUpdate_SP'
        # self.dcm_stopped = self.prefix_dcm + 'GonRx_DesVelZero_RBV'
        self.timeout = timeout

    # --- properties
    @property
    def bragg_mon(self):
        return epics.caget(self.dcm_rb)

    @property
    def is_moving(self, tol=1e-4):
        if (epics.caget(self.dcm_energy_rb) - epics.caget(self.dcm_energy_sp) > tol):
            return True
        else:
            return False

    @property
    def energy_mon(self):
        return epics.caget(self.dcm_energy_rb)

    # # --- methods
    def set_energy(self, energy, timeout=None):
        """Set energy

        Args:
            energy (1d numpy array): KeV
            timeout (_type_, optional): _description_. Defaults to None.
        """
        epics.caput(self.dcm_energy_sp, energy)
        return epics.caput(self.dcm_energy_update, 1)

    # --- cmd methods
    def cmd_move(self, timeout=None):
        if timeout is None:
            timeout = self.timeout

        success = epics.caput(self.dcm_move, 1)
        if success == 1:
            return True
        else:
            return False

    def cmd_move_robust(self, energy, timeout=None):
        if timeout is None:
            timeout = self.timeout

        sucess = self.set_energy(energy)
        time.sleep(0.2)
        if sucess:
            while self.is_moving:
                print('DMC is moving...', end='\r')
                time.sleep(0.1)
            return True
        else:
            print('cmd move failed!')
            return False


def bragg2energy(theta_deg):
    return 1e-3 * (1.9752e+03 + 0.0427*theta_deg) / np.sin((theta_deg + 0.0207)*np.pi/180)


def test_poly_fit():

    bragg = np.linspace(3, 40, 501)
    energy = bragg2energy(bragg)

    coeffs_b2e = np.polyfit(bragg, energy, deg=8)
    poly_b2e = np.polyval(coeffs_b2e, bragg)

    coeffs_e2b = np.polyfit(energy, bragg, deg=8)
    poly_e2b = np.polyval(coeffs_e2b, energy)

    plt.figure()
    plt.plot(energy, bragg, '.')
    plt.plot(poly_b2e, bragg, '-')
    plt.plot(energy, poly_e2b, '--')
    plt.grid()
