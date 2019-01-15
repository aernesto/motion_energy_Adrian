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

def map_frame_number_to_time_idx(frameNumber, T):
    return np.mod(frameNumber,T+1)

''' --- I didn't manage to put this function here instead of in the notebook :(
def make_frame(t, stateMatrix, ME, binSize, fig, ax1, ax2):

    # define quantities used later on
    _, N = stateMatrix.shape  # N is number of cells
    x = np.arange(N)+1        # 1D space
    T = _ - 1                 # T is time horizon (T = number of time steps - 1)

    frameNumber = map_time_to_frame(t, binSize)    
    time_idx = map_frame_number_to_time_idx(frameNumber, T)
    
    # plot particles
    ax1.clear()

    xx=x[stateMatrix[time_idx,:]==1]
    ax1.plot(xx, 0, 'bo')
    ax1.set_ylim(-.5, 0.5)
    ax1.set_xlim(0, N+1)
    
    #ax2.clear()
    if time_idx > 0:  # account for the fact that ME doesn't exist at time = 0
        ax2.plot(frameNumber,ME[time_idx - 1],'bo')

    return mplfig_to_npimage(fig)
'''
