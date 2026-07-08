import numpy as np
import time
from dvf import HDFfile


class Scan():
    def __init__(self, fname, dcm, dvf):
        self.fname = fname
        self.dcm = dcm
        self.dvf = dvf
        self.scanPoints = None

    def load_scan_points(self):
        self.scanPoints = np.genfromtxt(self.fname)

    def do_scan(self, progress_callback=None):
        folder = './'
        # fname_prefix = 'SPU_CS_eScan_{0:.1f}keV_h{1:d}_'.format(energy0, harmonic)
        fname_prefix = 'SPU_test'

        start_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

        t0 = time.time()

        hdf = HDFfile(filename=folder + fname_prefix + start_time + '.h5')
        hdf.initialize_hdf5()

        ne = len(self.scanPoints)
        for i in range(ne):

            print('Scanning energy point {0}/{1} ...'.format(i+1, ne), end='\r')

            self.dcm.cmd_move_robust(self.scanPoints[i][0], timeout=5)
            self.dvf.set_exposure_time(self.scanPoints[i][2])
            time.sleep(0.5)

            energy_mon = self.dcm.energy_mon
            # energy_mon = self.scanPoints[i][0]
            exp_time_mon = self.dvf.exposure_time
            img = self.dvf.acquire_image()
            flux = self.dvf.get_integral(img)
            max_intensity = img.max()

            attributes = []
            attributes.append(['energy_mon', energy_mon])
            attributes.append(['flux_mon', flux])
            attributes.append(['max_intensity', max_intensity])
            attributes.append(['exp_time_mon', exp_time_mon])
            attributes.append(['exp_time_sp', self.scanPoints[i][2]])

            hdf.append_image_to_hdf5('img_{0:03d}'.format(i+1), img, attributes)
            if progress_callback is not None:
                progress = int((i + 1) / ne * 100)
                progress_callback(progress)

        hdf.end_hdf5()

        t1 = time.time()

        print('Finished Energy Scan!')
        print('Elapsed time = {0:.1f} min'.format((t1-t0)/60))
        print(fname_prefix + start_time)
#
