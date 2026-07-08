import numpy as np
from scipy.special import jv
import mathphys
import scipy.constants as constants

PI = constants.pi
EMASS = mathphys.constants.electron_mass
LSPEED = mathphys.constants.light_speed
ECHARGE = mathphys.constants.elementary_charge
PLANCK = mathphys.constants.reduced_planck_constant
VCPERM = mathphys.constants.vacuum_permitticity
GAMMA = 5870
PERIOD = 22e-3


def get_A(gamma, theta, k):
    return (1 + 0.5*k**2 + (gamma*theta)**2)


def get_harmonic(n , gamma, theta, period, k):
    return period/(n*2*gamma**2)*(1 + 0.5*k**2 + (gamma*theta)**2)


def l_function(N, domega_omega1):
    num = np.sin(N*np.pi*domega_omega1)**2
    dem = N**2*np.sin(np.pi*domega_omega1)**2
    return num/dem


def calc_flux_density(b, angle):
    gamma = GAMMA
    period = PERIOD
    current = 0.2
    k = b*period*ECHARGE/(2*np.pi*EMASS*LSPEED)
    N = 51

    theta_ = angle*1e-6
    phi = np.pi/2*1

    theta, phi = np.array(np.meshgrid(theta_, phi))
    x = np.arctan(theta*np.cos(phi))
    y = np.arctan(theta*np.sin(phi))

    a = get_A(gamma, theta, k)
    lamb1 = get_harmonic(1, gamma, theta, period, k)
    omega1 = 2*np.pi*LSPEED/lamb1
    max_harmonic = 20

    omega_omega1 = np.linspace(-0.5, 0.5 , 5000)
    i = np.zeros((max_harmonic, len(omega_omega1)))
    flux = np.zeros((max_harmonic, len(omega_omega1)))
    fn = np.zeros((max_harmonic, len(omega_omega1)))
    omega = np.zeros((max_harmonic, len(omega_omega1)))
    lamb = np.zeros((max_harmonic, len(omega_omega1)))
    energy = np.zeros((max_harmonic, len(omega_omega1)))
    for n in np.arange(1, max_harmonic + 1, 1):
        domega = omega_omega1*omega1 - n*omega1
        domega_omega1 = domega/omega1
        l = l_function(N, domega_omega1)
        pre_fac = (ECHARGE*n*N*gamma)**2
        pre_fac /= (4*np.pi*VCPERM*LSPEED)
        X = 2*n*gamma*theta*k*np.cos(phi)/a
        Y = n*k**2/(4*a)
        values = np.arange(-240, 241, 1)
        p_ = np.ones((X.shape[0], X.shape[1], len(values)))
        p_[0, 0, :] = values

        argy_ = np.zeros((X.shape))
        term1 = np.zeros((X.shape))
        term2 = np.zeros((X.shape))

        # Vertical term
        argy_ = (jv(n + 2*p_, X)*jv(p_, Y))

        # Horizontal term
        term1 = (jv(n + 2*p_, X)*jv(p_, Y))
        term2 = (jv(n + 2*p_ - 1, X)*jv(p_, Y)) + (jv(n + 2*p_ + 1, X)*jv(p_, Y))

        term1 = np.sum(term1)
        term2 = np.sum(term2)
        argy_ = np.sum(argy_)

        argy = np.absolute(2*gamma*theta*np.sin(phi)*argy_)**2
        argx = np.absolute(2*gamma*theta*np.cos(phi)*term1 - k*term2)**2

        # Spectral angular power
        i[n-1, :] = pre_fac*l*(argx + argy)/a**2
        omega[n-1, :] = omega_omega1*omega1 + n*omega1
        energy[n-1, :] = PLANCK*omega[n-1, :] / ECHARGE
        lamb[n-1, :] = 2*np.pi*LSPEED/omega[n-1, :]
        flux[n-1, :] = i[n-1, :]*current/(ECHARGE*PLANCK)*1e-9
    return energy, flux
