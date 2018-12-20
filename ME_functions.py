import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

def custom_ME(stateMatrix, displayMatrices=False):
    N = stateMatrix.shape[1] # number of cells in 1D space
    
    # compute displacement 
    displacementMatrix = np.diff(stateMatrix, axis=0)

    # compute movement matrix
    movementMatrix = np.diff(displacementMatrix, axis=1)

      # boolean for ulterior indexing
    toKillLeft = displacementMatrix[:,:(N-1)] == 0
    toKillRight = displacementMatrix[:,1:] == 0

      # set to zero movement occurring where the left cell was stationary
    movementMatrix[toKillLeft] = 0

      # set to zero movement occurring where the right cell was stationary
    movementMatrix[toKillRight] = 0 

    # inspect matrices
    if displayMatrices:
        print('state matrix\n',stateMatrix)
        print('displacement matrix\n',displacementMatrix)
        print('movement matrix\n',movementMatrix)

    # compute motion energy (custom definition explained in above sections)
    return np.sum(movementMatrix, axis=1)

def map_time_to_frame(t, binSize):
    return int(np.floor(t/binSize))

def make_frame(t, ax1, ax2, stateMatrix, T, N, ME, fig):
    ax1.clear()
    tt = map_time_to_frame(t)
    xx=x[stateMatrix[np.mod(tt,T+1),:]==1]
    ax1.plot(xx, 0, 'bo')
    ax1.set_ylim(-.5, 0.5)
    ax1.set_xlim(0, N+1)
    
    #ax2.clear()
    ax2.plot(tt,ME[tt],'bo')

    return mplfig_to_npimage(fig)
