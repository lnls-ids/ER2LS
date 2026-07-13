import numpy as np
from siriuspy.devices import APU
from siriuspy.search import IDSearch
from scipy.optimize import minimize_scalar
from scipy import constants

PI = constants.pi
EMASS = constants.electron_mass
LSPEED = constants.speed_of_light
ECHARGE = constants.elementary_charge
PLANCK = constants.Planck/(2*PI)
GAMMA = 5870
PERIOD = 22e-3


def initialize_apu(beamline='SAPUCAIA'):
    # Search ID
    devname = IDSearch.conv_beamline_2_idname(beamline=beamline)
    apu22 = APU(devname=devname)
    return apu22


def get_sapucaia_poly_coefficients():

    # poly_coeffs = np.array([1.87690e+00,
    #                         -1.40530e-02,
    #                         2.27247e-02,
    #                         -2.62098e-03,
    #                         1.18683e-03,
    #                         -2.70916e-04,
    #                         3.69179e-05,
    #                         -2.66819e-06,
    #                         7.34316e-08]),

    poly_coeffs = ([1.8680901504703888,
                    -0.0010965860594141523,
                    0.020011139868170266,
                    -1.8626934139934243e-05,
                    9.162158439711758e-05,
                    -1.2298031796253283e-05,
                    6.580397699950502e-06,
                    -2.566367116526837e-06,
                    6.593662992306596e-07,
                    -1.1894376316949324e-07,
                    1.4458061010604742e-08,
                    -1.1443962847130537e-09,
                    5.2776910150174366e-11,
                    -1.0535251363098205e-12])
    return poly_coeffs


def poly_any_degree(x, coefficients):

    y = 0
    for i in range(len(coefficients)):
        y += coefficients[i] * x**i
    return y


def search_phase(x, *args):

    energy = args[0]
    coeffs = args[1]

    return np.abs(poly_any_degree(x, coeffs) - energy)


def get_phase_from_energy_h1(energy, coefficients, bounds=[0, 10]):

    args = (energy, coefficients)
    res = minimize_scalar(search_phase, args=args, bounds=[0, 10], method='bounded')
    return res.x


def find_harmonics_given_energy(energy_points, min_energy=1.870, max_energy=3.600,
                                print_points=0, initial_harmonic=1, only_max_harmonic=0):

    scan_points = []

    for i in range(len(energy_points)):

        energy = energy_points[i]

        if (only_max_harmonic):

            k = initial_harmonic
            while (True):

                if ((energy / k >= min_energy) & (energy / k <= max_energy)):
                    max_harmonic = k

                elif (energy / k < min_energy):
                    break

                k += 2

            scan_points.append([energy, max_harmonic])

            if (print_points):
                print(scan_points[-1])

        else:

            k = initial_harmonic
            while (True):

                if ((energy / k >= min_energy) & (energy / k <= max_energy)):
                    scan_points.append([energy, k])
                    if (print_points):
                        print(scan_points[-1])

                elif (energy / k < min_energy):
                    break

                k += 2

    return scan_points


def calc_field(phase):
    e1 = poly_any_degree(phase, get_sapucaia_poly_coefficients())
    k = np.sqrt(4*GAMMA**2*PLANCK*2*PI*LSPEED/(e1*1e3*ECHARGE*PERIOD)-2)
    b = 2*PI*EMASS*LSPEED*k/(ECHARGE*PERIOD)
    return b


def calc_k(phase):
    e1 = poly_any_degree(phase, get_sapucaia_poly_coefficients())
    k = np.sqrt(4*GAMMA**2*PLANCK*2*PI*LSPEED/(e1*1e3*ECHARGE*PERIOD)-2)
    return k


def get_phase_from_energy(energy_value=12.000, harmonic_number=5, verbose=0):

    # find possible harmonics
    harmonics = find_harmonics_given_energy(energy_points=[energy_value],
                               only_max_harmonic=False)

    harmonics = np.array(harmonics)
    if len(harmonics) == 0:
        return np.nan
    harmonics = harmonics[:, 1].astype(int)

    poly_coeffs = get_sapucaia_poly_coefficients()

    if (harmonic_number in harmonics):

        energy1 = energy_value / harmonic_number

        phase = get_phase_from_energy_h1(energy1, poly_coeffs, bounds=[0, 10])
        phase = round(phase, 4)

        if (verbose):
            print('phase value is:', phase)
            print('energy:', energy_value, 'keV')
            print('h =', harmonic_number)
            print('fundamental energy =', round(energy1, 4))

    else:
        if (verbose):
            print('harmonic h =', harmonic_number, 'is not valid for this energy.')
            print('please choose a valid harmonic number')
        phase = np.nan

    if (verbose):
        print('\n')
        print('possible harmonics for this energy are:')
        for h in harmonics:
            print('h =', h)

    return phase
