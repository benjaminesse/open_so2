# -*- coding: utf-8 -*-
"""
Module to generate spectrometer instrument line shapes (ILS).
"""

import numpy as np
from scipy.special import gamma

#==============================================================================
#=================================== make_ils =================================
#==============================================================================

def make_ils(interval, FWEM, k = 2, a_w = 0, a_k = 0):

    '''
    Function to generate a synthetic instrument line shape based on a super 
    gaussian function:

                     { exp(-| x / (w-a_w) | ^ (k-a_k)) for x <= 0
    G(x) = A(w, k) * {
                     { exp(-| x / (w+a_w) | ^ (k+a_k)) for x > 0

    where A(w, k) = k / (2 * w * Gamma(1/k)).

    See Beirle et al (2017) for more details: doi:10.5194/amt-10-581-2017

    **Paramters:**
        
    interval : int
        The spacing of the wavelength grid on which the ILS is built

    FWEM : float
        The Full Width eth Maximum of the lineshape, defined as 2*w = FWEM

    k : float
        Controls the shape of the lineshape (default = 2):
            - k < 2 -> sharp point and wide tails
            - k = 2 -> normal Gaussian
            - k > 2 -> flat top, approaches boxcar at k -> inf

    a_w and a_k : float
        Controls the asymetry of the lineshape

    **Returns:**
        
    ils : numpy array
        The calculated ILS function on a wavelength grid of the given spacing 
        and 5 times the width of the supplied FWEM
    '''

    # Create a grid 6 times that of the width
    grid = np.arange(-FWEM * 2, FWEM * 2, interval)

    # Calculate w as half of the FWEM
    w = 0.5 * FWEM

    # Form empty array
    super_g = np.zeros(len(grid))

    # Calculate A
    A = k / (FWEM * gamma(1/k))

    # Split the x grid into =ve and -ve arrays
    neg_idx = np.where(grid <= 0)
    pos_idx = np.where(grid > 0)
    neg_grid = grid[neg_idx]
    pos_grid = grid[pos_idx]

    # Calculate the asymetric supergaussian function
    neg_g = np.multiply(A, np.exp(-np.power(np.abs((neg_grid) / (w - a_w) ), 
                                            k - a_k)))
    pos_g = np.multiply(A, np.exp(-np.power(np.abs((pos_grid) / (w + a_w) ), 
                                            k + a_k)))

    # Combine
    super_g = np.append(neg_g, pos_g)

    super_g = np.divide(super_g, sum(super_g))

    return super_g

