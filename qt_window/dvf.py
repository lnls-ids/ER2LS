import numpy as np
import epics
import matplotlib.pyplot as plt
import time
import h5py


class DVF():

    def __init__(self):
        # Define PVs
        self.pv_prefix = 'SPU:A:BASLER02:'
        self.pv_image = self.pv_prefix + 'image1:ArrayData'
        self.pv_image_roi = self.pv_prefix + 'roi1:ArrayData'
        self.pv_nx = self.pv_prefix + 'image1:ArraySize0_RBV'
        self.pv_ny = self.pv_prefix + 'image1:ArraySize1_RBV'
        self.pv_exp_time = self.pv_prefix + 'cam1:AcquireTime'
        self.pv_exp_time_mon = self.pv_prefix + 'cam1:AcquireTime_RBV'
        self.dvf_acquire = self.pv_prefix + "cam1:Acquire"

        # self.nx = epics.caget(self.pv_nx)
        self.shape = (self.ny, self.nx)
        # self.shape_roi = self.shape
        self.roi_is_defined = False

    # --- properties
    @property
    def ny(self):
        return epics.caget(self.pv_ny)

    @property
    def nx(self):
        return epics.caget(self.pv_nx)

    @property
    def exposure_time(self):
        return epics.caget(self.pv_exp_time_mon)

    @property
    def saturation(self):
        return 1024

    def start_stop_acquire(self):
        value = not epics.caget(self.dvf_acquire)
        epics.caput(self.dvf_acquire, value)
        time.sleep(0.1)

    def set_exposure_time(self, exp_time=0.002):
        epics.caput(self.pv_exp_time, exp_time)

    def acquire_image(self, shape=(1024, 1280), binning=(1, 1)):

        img = np.array(epics.caget(self.pv_image))

        img = img.reshape(self.shape)

        if (binning != (1, 1)):
            img = self.bin_matrix(img, binning[0], binning[1])

        self.img = img

        return img

    def acquire_image_example(self, max_int=0):
        img = np.genfromtxt('img_test.dat')
        if (max_int > 0):
            img = img / np.max(img) * max_int

        self.img = img

        return img

    def get_integral(self, img):
        return np.sum(img)

    def plot_image(self):
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(self.img, origin='lower', cmap='viridis')
        fig.colorbar(im, ax=ax)
        plt.show()

    def bin_matrix(self, matrix, binning_y, binning_x):

        yn, xn = matrix.shape

        if ((xn % binning_x != 0) or (yn % binning_y != 0)):
            print('array of shape ({0} x {1}) cannot be binned by factor ({2},{3})'.format(yn, xn, binning_y, binning_x))
            return matrix

        else:
            print('binning matrix of shape({0},{1}) by factors ({2},{3})'.format(yn, xn, binning_y, binning_x))
            xn = int(xn / binning_x)
            yn = int(yn / binning_y)

            matrix_binned = np.zeros((yn, xn), dtype=float)

            count_y = 0
            for iy in range(yn):

                count_x = 0
                for ix in range(xn):

                    matrix_binned[iy, ix] = np.sum(matrix[count_y:count_y+binning_y,
                                                        count_x:count_x+binning_x])

                    count_x += binning_x
                count_y += binning_y

            matrix_binned /= binning_x*binning_y

            return matrix_binned

    def define_ROI(self, ROI_shape=(400, 400), ROI_start=(0, 0), ROI_binning=(1, 1)):

        # enable ROI
        epics.caput(self.pv_prefix +'ROI1:EnableCallbacks', 1, wait=True)
        epics.caput(self.pv_prefix + 'image1:NDArrayPort', 'ROI1', wait=True)

        # set ROI
        epics.caput(self.pv_prefix +'ROI1:MinX', ROI_start[1], wait=True)
        epics.caput(self.pv_prefix +'ROI1:MinY', ROI_start[0], wait=True)

        epics.caput(self.pv_prefix +'ROI1:SizeX', ROI_shape[1], wait=True)
        epics.caput(self.pv_prefix +'ROI1:SizeY', ROI_shape[0], wait=True)

        epics.caput(self.pv_prefix +'ROI1:BinX', ROI_binning[1], wait=True)
        epics.caput(self.pv_prefix +'ROI1:BinY', ROI_binning[0], wait=True)

        self.shape = ROI_shape
        # self.shape_roi = ROI_shape
        self.roi_is_defined = True

        time.sleep(1)

    def disable_ROI(self):

        epics.caput(self.pv_prefix +'ROI1:EnableCallbacks', 1, wait=True)
        epics.caput(self.pv_prefix + 'image1:NDArrayPort', 'CAM', wait=True)
        self.shape = (self.ny, self.nx)

    def get_centroid(self, img, x=0, y=0):

        shape = self.shape

        if (x == 0):
            x = np.arange(0, shape[1])
        if (y == 0):
            y = np.arange(0, shape[0])

        Ix = np.sum(img, axis=0)
        Iy = np.sum(img, axis=1)

        x_mean = 0
        y_mean = 0

        if (np.sum(Ix) != 0):
            x_mean = x[np.argmax(Ix)]

        if (np.sum(Iy) != 0):
            y_mean = y[np.argmax(Iy)]

        return (y_mean, x_mean)

# HDF5 functions


class HDFfile():

    def __init__(self, filename):
        # Define PVs
        self.filename = filename

    def initialize_hdf5(self):
        """Initialize a h5 file.

        Args:
            h5_filename (str): File name
        """
        with h5py.File(self.filename, "w") as f:
            f.attrs["begin time"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()
            )
            f.create_group("images")

    def end_hdf5(self):
        """Finish a h5 file.

        Args:
            h5_filename (str): File name
        """
        with h5py.File(self.filename, "a") as f:
            f.attrs["end time"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()
            )

    def create_group(self, group_name, group_attributes):
        """Create a group in h5 file.

        Args:
            h5_filename (str): File name
            group_name (str): Group name
            group_attributes (dict): Group attributes
        """
        with h5py.File(self.filename, "a") as f:
            group_images = f["images"].create_group(group_name)

            for i in range(len(group_attributes)):
                group_images.attrs[group_attributes[i][0]] = group_attributes[i][1]

    def append_image_to_hdf5(
        self, dataset_name, image, attributes):
        """Add image to h5 file.

        Args:
            h5_filename (str): File name
            group_name (str): Group name
            dataset_name (_type_): _description_
            image (_type_): _description_
            attributes (_type_): _description_
        """
        with h5py.File(self.filename, "a") as f:
            group = f["images"]
            dset = group.create_dataset(
                dataset_name, data=image, compression="gzip"
            )

            for i in range(len(attributes)):
                dset.attrs[attributes[i][0]] = attributes[i][1]
