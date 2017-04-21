import sys
import os
import scipy.io as sio
import glob
import numpy as np
import matplotlib.pyplot as plt
import libtim.zern as zern
from visualization import  zern_display, IMshow_pupil
from skimage.restoration import unwrap_phase
from psf_tools import *
from Phase_retrieval import PSF_PF


def load_mat(mat_path):
    '''
    load matlab data file (*.mat).
    '''
    if os.path.exists(mat_path):
        try:
            im_stack_raw = sio.loadmat(mat_path)['data']
            im_stack = np.transpose(im_stack_raw,(2,0,1))
            return im_stack.astype('float64') # only keep the data of the dictionary
        except IOError:
            print("Could not read the file:", mat_path)
            sys.exit()



def group_retrieval(path_root):

    psf_list = glob.glob(path_root+"*.mat")
    psf_list.sort(key = os.path.getmtime)
    Strehl = []
    FWHM = []

    for fname in psf_list:
        session_name = os.path.split(fname)[-1][:-4] # show the psf filename
        print("psf:", session_name)
        psf_name = session_name
        psf_stack = load_mat(fname)
        figv, fhwm = psf_lineplot(psf_stack)
        figv.savefig(path_root+session_name+'_line')
        fl_nikon = 1000*200.0/60.0

        FWHM.append(fhwm)
        pr = PSF_PF(psf_stack, dx=0.0800, dz=0.20, ld=0.520, nrefrac=1.33, NA=1.27, fl=fl_nikon, nIt=11)
        k_max = pr.PF.k_pxl
        print("k_max:", k_max)
        pr.retrievePF(bscale = 1.00, psf_diam = 20)
        pupil_final = pr.pf_phase
        Strehl.append(pr.strehl_ratio())
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.imshow(pupil_final, cmap = 'RdBu_r')
        ax.set_title(psf_name)
        plt.tight_layout()
        plt.axis('off')
        fig.savefig(path_root+psf_name+'_obj3')
        pf_crop = pupil_final[20-k_max:20+k_max, 20-k_max:20+k_max]
        print(pf_crop.shape)
        zfit = zern.fit_zernike(pf_crop,rad = k_max,nmodes = 17)[0]/(2*np.pi)
        zfit[:4] = 0.0
        resync = zern.calc_zernike(zfit,rad = 2*k_max, mask = True)
        figr = IMshow_pupil(resync, axnum = False)
        figr.savefig(path_root+psf_name+'_zf_resync_obj3')
        figz = zern_display(zfit, z0 = 4, ylim = [-0.005,0.02])
        print("zshape:",zfit.shape)
        figz.savefig(path_root+psf_name+'_zfit_obj3')







if __name__ == '__main__':

    path_root = '/home/sillycat/Documents/Light_sheet/Data/Oblique/'
    group_retrieval(path_root)