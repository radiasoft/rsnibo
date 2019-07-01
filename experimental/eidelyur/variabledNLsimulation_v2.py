# 
# This script develops the script 'variabledNLsimulation_v1.py' (Yury)
#
#    Started at June 28, 2019
#
# The three laws to change the strengths 't' of all nonlinear lens are implemented.
# From initial value t_i to final value t_f during N stepsthese laws are follows.
# 1) Linear: for step number n
#           t(n) = t_0 + (t_f-t_0)*n/(N-1) for n = 0,1,...,N-1 .
# 2) Parabolic: for step number n
#           t(n) = t_0 + (t_f-t_0)*n^2/(N-1)^2 for n = 0,1,...,N-1 .
# 3) Smooth sign-function: for step number n
#           t(n) = .5*(t_0+t_f) + .5*(t_f-t_0)*tanh(x(n)), where
#           x(n) = (6*n-3*(N-1))/(N-1) for n=0,1,...,N-1 .
# In this approach x(0) = -3., x(N-1) = 3.; so, tanh(3.) = - tanh(-3.) = .9951
#

import synergia
import os, sys
import inspect
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import gridspec

import rssynergia 
from rssynergia.base_diagnostics import lfplot
from rssynergia.base_diagnostics import plotbeam
from rssynergia.base_diagnostics import pltbunch

def plotcoordDistr(bunchParticles):
#    
# Plot X-X', Y-Y', and X-Y distributions for 'bunchParticles'
#
# bunchParticles is a 'bunch' object;
# particles is 2D array: (numberOfParticles,(x,x',y,y',s,dp(?),ID);
#
    numbPartcls = bunchParticles.shape[0]
    particles = bunchParticles.real
    newCoordinates = np.zeros((6,numbPartcls))
    for k in range(numbPartcls):
        for j in range(6):
            newCoordinates[j,k] = 1.e3*particles[k,j]       # Units: mm and mrad 
    xmax = 1.15*np.max(abs(newCoordinates[0,:]))
    xpmax = 1.15*np.max(abs(newCoordinates[1,:]))
    ymax = 1.15*np.max(abs(newCoordinates[2,:]))
    ypmax = 1.15*np.max(abs(newCoordinates[3,:]))
    meanX = np.mean(newCoordinates[0,:])
    meanPX = np.mean(newCoordinates[1,:])
    stdX = np.std(newCoordinates[0,:])
    stdPX = np.std(newCoordinates[1,:])
    meanY = np.mean(newCoordinates[2,:])
    meanPY = np.mean(newCoordinates[3,:])
    stdY = np.std(newCoordinates[2,:])
    stdPY = np.std(newCoordinates[3,:])

# Another way - use gridspec
    fig = plt.figure(figsize=(15,5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,1]) 
    
    ax0 = plt.subplot(gs[0])
    plt.plot(newCoordinates[0,:],newCoordinates[2,:],'.',color='k')
    x0Title = "X,mm: <> = {:.3f} +- {:.3f}\nY,mm: <> = {:.3f} +- {:.3f}".format(meanX,stdX,meanY,stdY)
    ax0.set_title(x0Title,fontsize='16')
    ax0.set_xlim([-xmax,xmax])
    ax0.set_ylim([-ymax,ymax])
    ax0.set_xlabel('X, mm')
    ax0.set_ylabel('Y, mm')
    ax0.grid(True)
    
    ax1 = plt.subplot(gs[1])
    plt.plot(newCoordinates[0,:],newCoordinates[1,:],'.',color='b')
    x1Title = "X,mm: <> = {:.3f} +- {:.3f}\nX\',mrad: <> = {:.3f} +- {:.3f}".format(meanX,stdX,meanPX,stdPX)
    ax1.set_title(x1Title,fontsize='16')
    ax1.set_xlim([-xmax,xmax])
    ax1.set_ylim([-xpmax,xpmax])
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('X\', mrad')
    ax1.grid(True)
    
    ax2 = plt.subplot(gs[2])
    plt.plot(newCoordinates[2,:],newCoordinates[3,:],'.',color='r')
    x2Title = "Y,mm: <> = {:.3f} +- {:.3f}\nY\',mrad: <> = {:.3f} +- {:.3f}".format(meanY,stdY,meanPY,stdPY)
    ax2.set_title(x2Title,fontsize='16')
    ax2.set_xlim([-ymax,ymax])
    ax2.set_ylim([-ypmax,ypmax])
    ax2.set_xlabel('Y, mm')
    ax2.set_ylabel('Y\', mrad')
    ax2.grid(True)
    
#    fig.canvas.set_window_title('Synergia Phase Space Distribution')
    fig.tight_layout()
    plt.show()
    return

def plotTracks(tracksCoords,numberTracks):
#    
# Plot'numberTracks' tracks from 'tracksCoords'
#
# tracksCoords is 3D array: (totalTurns,particles,(x,y))
#
#    print "numberTracks = ",numberTracks
    trackColor = ['r','b','k','m','g']
    numbPoints = tracksCoords.shape[0]
#    print "numbPoints = ",numbPoints
    xmax = 1.15*np.max(np.max(abs(tracksCoords[:,0:numberTracks,0])))
    ymax = 1.15*np.max(np.max(abs(tracksCoords[:,0:numberTracks,1])))

    turn = np.arange(0,numbPoints)
# Another way - use gridspec
    fig = plt.figure(figsize=(15,5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1,1]) 
    
    ax0 = plt.subplot(gs[0])
    for prtcl in range(numberTracks):
        plt.plot(turn,tracksCoords[0:numbPoints,prtcl,0],'.-',color=trackColor[prtcl])
#    x0Title = "X,mm: <> = {:.3f} +- {:.3f}\nY,mm: <> = {:.3f} +- {:.3f}".format(meanX,stdX,meanY,stdY)
#    ax0.set_title(x0Title,fontsize='16')
    ax0.set_ylim([-xmax,xmax])
    ax0.set_xlabel('Turn')
    ax0.set_ylabel('X, mm')
    ax0.grid(True)

    ax1 = plt.subplot(gs[1])
    for prtcl in range(numberTracks):
        plt.plot(turn,tracksCoords[0:numbPoints,prtcl,1],'.-',color=trackColor[prtcl])
#    x0Title = "X,mm: <> = {:.3f} +- {:.3f}\nY,mm: <> = {:.3f} +- {:.3f}".format(meanX,stdX,meanY,stdY)
#    ax0.set_title(x0Title,fontsize='16')
    ax1.set_ylim([-ymax,ymax])
    ax1.set_xlabel('Turn')
    ax1.set_ylabel('Y, mm')
    ax1.grid(True)
       
#    fig.canvas.set_window_title('Synergia Phase Space Distribution')
    fig.tight_layout()
    plt.show()
    return

def printAttributes(object,name,title):
#
# List of all attributes of 'object' for checking:
#
    attrList = inspect.getmembers(object)
    strTitle = "\nattrList ("+name+" = "+title+"):\n{}\n"
    print strTitle.format(attrList)

def tracksCoords(bunchParticles):
#
# Preparation of the track coordinates:
#
# 'bunchParticle' is a 'bunch' object;
# 'particles' is 2D array: (numberParrticles,(x,x',y,y',s,dE,ID));
#
    numbPartcls = bunchParticles.shape[0]
    particles = bunchParticles.real
    trackCoordinates = np.zeros((numbPartcls,2))
    for prtcl in range(numbPartcls):
        trackCoordinates[prtcl,0] = 1.e3*particles[prtcl,0]       # x, mm
        trackCoordinates[prtcl,1] = 1.e3*particles[prtcl,2]       # y, mm
#        if prtcl < 3:
#            print "Particle {}: x = {} mm, y = {} mm". \
#            format(prtcl,trackCoordinates[prtcl,0],trackCoordinates[prtcl,1])
    return trackCoordinates 
    
# Pickle helper is not necessary but is retained for this example
class Pickle_helper:
    __getstate_manages_dict__ = 1
    def __init__(self, *args):
        self.args = args
    def __getinitargs__(self):
        return self.args
    def __getstate__(self):
        return self.__dict__
    def __setstate__(self, state):
        self.__dict__ = state
        
# Derived class to ramp quadrupoles

# Will be passed into propagator and called at each appropriate 'interval' (step, turn, action, etc...)

class Ramp_actions(synergia.simulation.Propagate_actions, Pickle_helper):
# The arguments to __init__ are what the Ramp_actions instance is initialized with
    def __init__(self, multiplier, outputFlag):
        selfObject = synergia.simulation.Propagate_actions.__init__(self)
# To recognize attributes of 'selfObject':
#        printAttributes(selfObject,'selfObject','synergia.simulation.Propagate_actions.__init__(self)')

# Pickling the arguments to the initializer allows the module to resume
# after checkpointing. They should be in the same order as the arguments to __init__.
        Pickle_helper.__init__(self, multiplier, outputFlag)
        self.multiplier = multiplier
        self.outputFlag = outputFlag
    def turn_end_action(self, stepper, bunch, turn_num):
#---------------------------
# For checking:
#        testObject = stepper.get_lattice_simulator().get_lattice()
# To recognize attributes of 'testObject':
#        printAttributes(testObject,'testObject','stepper.get_lattice_simulator().get_lattice()')
#        print "testName = '{}'".format(testObject.get_name())
#---------------------------
# Output title for checking of variables update:   
        if self.outputFlag == 1:
            print "Modifying lattice:"
        for element in stepper.get_lattice_simulator().get_lattice().get_elements():
            if element.get_type() == "nllens":
                old_knll = element.get_double_attribute("knll")
                element.set_double_attribute("knll", self.multiplier*old_knll)
# Output for checking of variables update checking nonlinear lens 'n.11' only:  
                if ((self.outputFlag == 1) and (element.get_name() == "n.11")):
                    print element.get_name(),":  knll=",old_knll,"-->",self.multiplier*old_knll
        stepper.get_lattice_simulator().update()

def lawsMagnification(mgnfctnFctr,steps):

# 1) Linear: for step number n
#           t(n) = t_0 + (t_f-t_0)*n/(N-1) for n = 0,1,...,N-1 .
    tLin = np.zeros(steps)
    for n in range(steps):
        tLin[n] = 1.+n*(mgnfctnFctr-1.)/(steps-1)
# 2) Parabolic: for step number n
#           t(n) = t_0 + (t_f-t_0)*n^2/(N-1)^2 for n = 0,1,...,N-1 .
    tPar= np.zeros(steps)
    for n in range(steps):
        tPar[n] = 1.+n**2*(mgnfctnFctr-1.)/(steps-1)**2
# 3) Smooth sign-function: for step number n
#           t(n) = .5*(t_0+t_f) + .5*(t_f-t_0)*tanh(x(n)), where
#           x(n) = (6*n-3*(N-1))/(N-1) for n=0,1,...,N-1 .
# In this approach x(0) = -3., x(N-1) = 3.; so, tanh(3.) = - tanh(-3.) = .9951
    tSSF= np.zeros(steps)
    for n in range(steps):
        x = (6.*n-3.*(steps-1))/(steps-1)
        tSSF[n] = .5*(1.+mgnfctnFctr)+.5*(mgnfctnFctr-1.)*np.tanh(x)
# Plotting all cases:
    step = range(steps)
    tMin = .975*min(tLin)
    tMax = 1.025*max(tLin)
    fig = plt.figure(figsize=(15,5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,1]) 
    
    ax0 = plt.subplot(gs[0])
    plt.plot(step,tLin,'-x',color='r')
    x0Title = 'Linear magnification'
    ax0.set_title(x0Title,fontsize='16')
    ax0.set_xlim([-1,steps+1])
    ax0.set_ylim([tMin,tMax])
    ax0.set_xlabel('Step n')
    ax0.set_ylabel('t')
    ax0.grid(True)
    
    ax1 = plt.subplot(gs[1])
    plt.plot(step,tPar,'-x',color='r')
    x1Title = 'Parabolic magnification'
    ax1.set_title(x1Title,fontsize='16')
    ax1.set_xlim([-1,steps+1])
    ax1.set_ylim([tMin,tMax])
    ax1.set_xlabel('Step n')
    ax1.set_ylabel('t')
    ax1.grid(True)
    
    ax2 = plt.subplot(gs[2])
    plt.plot(step,tSSF,'-x',color='r')
    x2Title = 'Smooth sign-function magnification'
    ax2.set_title(x2Title,fontsize='16')
    ax2.set_xlim([-1,steps+1])
    ax2.set_ylim([tMin,tMax])
    ax2.set_xlabel('Step n')
    ax2.set_ylabel('t')
    ax2.grid(True)

    fig.tight_layout()
    plt.show()
    selection = int(raw_input("\nYour selection of the law magnification \
    \n(1 - linear, 2 - parabolic, 3 - smooth sign-function; -1 - exit): "))
    return selection
   
# Main method 'simulation'
#
def simulation():        
#
# Interactive input of parameters:
#
    particlesInBunch = int(raw_input('\nTotal number if particles (= -1 to interrupt simulation):')) 
    if particlesInBunch == -1:
        return

    totalTurns = int(raw_input('\nTotal number if turns (= -1 to interrupt simulation):')) 
    if totalTurns == -1:
        return

    updateAfterTurns = int(raw_input( \
    '\nPeriodicity (in turns) of changing of parameters and distribution plots \n(nonlinear structure; = -1 to interrupt simulation)'))
    if updateAfterTurns == -1:
        return
    stepsInMgnfctn = int(totalTurns/updateAfterTurns)+1
    print "steps for magnification: ",stepsInMgnfctn

    updateOutputFlag = int(raw_input('\nupdateOutputFlag (0 - no, 1 - yes, -1  - to interrupt simulation):'))
    if updateOutputFlag == -1:
        return

    mgnfctnFctr = float(raw_input( \
    "\nRelative magnification (RF) of the strength 't' of nonlinear lens \n (RF = t_final/t_initial; -1.  - to interrupt simulation):"))
    if mgnfctnFctr == -1.:
        return
    else: 
        law = lawsMagnification(mgnfctnFctr,stepsInMgnfctn)
        print 'Your selection of law magnification: ', law
    if law == -1:
        return

    print "     Parameters: \nparticlesInBunch = ",particlesInBunch
    print "totalTurns = ",totalTurns
    print "updateAfterTurns = ",updateAfterTurns
    print "Relative magnification (RF) = ",mgnfctnFctr
    laws = ['linear', 'parabolic', 'smooth sign-function']
    print "Law of magnification: ",laws[law-1]
    print "steps in magnification: ",stepsInMgnfctn
 
    strengthLens = np.zeros(stepsInMgnfctn)
    magnifications = np.zeros(stepsInMgnfctn)
    for n in range(stepsInMgnfctn):
        if law == 1:
# 1) Linear: for step number n
#           t(n) = t_0 + (t_f-t_0)*n/(N-1) for n = 0,1,...,N-1 .
            strengthLens[n] = 1.+n*(mgnfctnFctr-1.)/(stepsInMgnfctn-1)
        elif law == 2:
# 2) Parabolic: for step number n
#           t(n) = t_0 + (t_f-t_0)*n^2/(N-1)^2 for n = 0,1,...,N-1 .
            strengthLens[n] = 1.+n**2*(mgnfctnFctr-1.)/(stepsInMgnfctn-1)**2
        elif law == 3:
# 3) Smooth sign-function: for step number n
#           t(n) = .5*(t_0+t_f) + .5*(t_f-t_0)*tanh(x(n)), where
#           x(n) = (6*n-3*(N-1))/(N-1) for n=0,1,...,N-1 .
# In this approach x(0) = -3., x(N-1) = 3.; so, tanh(3.) = - tanh(-3.) = .9951
            x = (6.*n-3.*(stepsInMgnfctn-1))/(stepsInMgnfctn-1)
            strengthLens[n] = .5*(1.+mgnfctnFctr)+.5*(mgnfctnFctr-1.)*np.tanh(x)
# For checking:
#    for n in range(stepsInMgnfctn):
#        print "strengthLens[{}] = {}".format(n,strengthLens[n])
    totalMgnfcn = 1.
    for n in range(stepsInMgnfctn):
        if n == 0:
            magnifications[n] = strengthLens[n]
        else:
            magnifications[n] = strengthLens[n]/strengthLens[n-1]
#        print "magnifications[{}] = {}".format(n,magnifications[n])
        totalMgnfcn *= magnifications[n]
    print "Total relative magnification (RF) will be = ",totalMgnfcn
    
# Lattice:

    fileIOTA = ".../ioptics/ioptics/lattices/Iota8-2/lattice_1IO_nll_center.madx"
    print "\nIOTA Nonlinear lattice: {} \n".format(fileIOTA)
    lattice = synergia.lattice.MadX_reader().get_lattice("iota", \
    "../ioptics/ioptics/lattices/Iota8-2/lattice_1IO_nll_center.madx")


#    fileIOTA = ".../ioptics/ioptics/lattices/Iota8-4/lattice_8-4_1IO_nll_forTest.madx"
#    print "\nIOTA Nonlinear lattice: {} \n".format(fileIOTA)
#    lattice = synergia.lattice.MadX_reader().get_lattice("iota", \
#    "../ioptics/ioptics/lattices/Iota8-4/lattice_8-4_1IO_nll_forTest.madx")


#----------------------------------
# To recognize attributes of 'lattice':
#     printAttributes(lattice,'lattice','synergia.lattice.MadX_reader().get_lattice')

#     madxAttributes = synergia.lattice.MadX_reader()
# To recognize attributes of 'doubleAttributes':
#     printAttributes(madxAttributes,'madxAttributes','synergia.lattice.MadX_reader()')

#     doubleVariable = madxAttributes.get_double_variable()
# To recognize attributes of 'doubleVariable':
#     printAttributes(doubleVariable,'doubleVariable','madxAttributes.get_double_variablte()')
#     print "doubleVariable = ", doubleVariable
#---------------------------------


# For checking only:
#    k = 0
#    for elem in lattice.get_elements():
#        if k == 0:
#            printAttributes(elem,'elem','lattice.get_elements')
#       k += 1
#        if elem.get_type() == 'nllens':
#            elem.set_string_attribute("extractor_type", "chef_propagate")
#        else:
#            elem.set_string_attribute("extractor_type", "chef_map")
#        print "elem ({}): name = {}, type = {}, stringAttrbt ={}". \
#              format(k,elem.get_name(),elem.get_type(),elem.get_string_attribute("extractor_type"))
    

# Original version:
#     lattice_simulator = synergia.simulation.Lattice_simulator(lattice, 2)
# Bunch:
#     bunch = synergia.optics.generate_matched_bunch_transverse(lattice_simulator, 1e-6, \
#                                                          1e-6, 1e-3, 1e-4, 1e9, 10000, seed=1234)

# YuE version:
    stepperCrrnt = synergia.simulation.Independent_stepper_elements(lattice,2,3)
    lattice_simulator_Crrnt = stepperCrrnt.get_lattice_simulator()
# Bunch:
    bunch_origin = synergia.optics.generate_matched_bunch_transverse(lattice_simulator_Crrnt, 1e-6, \
                                                          1e-6, 1e-3, 1e-4, 1e9, particlesInBunch, seed=1234)
# For checking:
# To recognize attributes of 'bunch_origin':
#     printAttributes(bunch_origin,'bunch_origin','synergia.optics.generate_matched_bunch_transverse')
#     particlesTmp = bunch_origin.get_local_particles()
# To recognize attributes of 'particlesTmp':
#     printAttributes(particlesTmp,'particlesTmp','bunch_origin.get_local_particles')
# 'particlesCrrnt' is 2D array: (numberoFParticle,(x,x',y,y',s,dE,ID));
#     particlesCrrnt = particlesTmp.real
#     print "                 particlesCrrnt:"
#     for prtcl in range(5):
#         print "x (m) for particle {}: {}".format(prtcl,particlesCrrnt[prtcl,0])
#         print "y (m) for particle {}: {}".format(prtcl,particlesCrrnt[prtcl,2])
#         print "s (m) for particle {}: {}".format(prtcl,particlesCrrnt[prtcl,4])
# End of checking


#-------------------------------------------------
# For checking only:
#
# 1) Attributes:
#     printAttributes(bunch,'bunch','synergia.optics.generate_matched_bunch_transverse')
# 2) Distributions X-Y, X-X', Y-Y' using method 'pltbunch.plot_bunch':
    loclTitle = "\nThese distributions were constructed using \
    'synergia.optics.generated_matched_bunch_transverse' method:\n"
    print loclTitle
    pltbunch.plot_bunch(bunch_origin)     
# 3) Distributions X-Y, X-X', Y-Y' using method 'plotcoordDistr':
    bunchParticles = bunch_origin.get_local_particles()
# To recognize attributes of 'bunchParticles':
#     printAttributes(bunchParticles,'bunchParticles', 'bunch.get_local_particles()')
    plotcoordDistr(bunchParticles)
#--------------------------------------------------

# Steppers (YuE: both case 'splitoperator' and 'independent' work properly!):
#     stepper = 'splitoperator'
    stepper = 'independent'
    if stepper == "splitoperator":
# Use the Split operator stepper with a dummy collective operator (with evenly-spaced steps)
        no_op = synergia.simulation.Dummy_collective_operator("stub")
        stepper = synergia.simulation.Split_operator_stepper(
                            lattice_simulator_Crrnt, no_op, 4)
    elif stepper == "independent":
# Use the Independent particle stepper (by element)
        stepper = synergia.simulation.Independent_stepper_elements(
                            lattice_simulator_Crrnt, 4)
    else:
        sys.stderr.write("fodo.py: stepper must be either 'independent' or 'splitoperator'\n")
        exit(1)

# Bunch simulator:
    bunch_simulator = synergia.simulation.Bunch_simulator(bunch_origin)


# This diagnostics does not use!
# Diagnostics:
#    diagnostic_flag = 'None'
#    for part in range(0, 0):
#        bunch_simulator.add_per_step(synergia.bunch.Diagnostics_track("step_track_%02d.h5" % part,
#                                                                   part))
#    if diagnostic_flag == 'step_full2':
#        bunch_simulator.add_per_step(synergia.bunch.Diagnostics_full2("step_full2.h5"))
#    if diagnostic_flag == 'step_particles':
#        bunch_simulator.add_per_step(synergia.bunch.Diagnostics_particles("step_particles.h5"))
#    for part in range(0, 0):
#        bunch_simulator.add_per_turn(synergia.bunch.Diagnostics_track("turn_track_%02d.h5" % part,
#                                                                   part))
#    if diagnostic_flag == 'turn_full2':
#    bunch_simulator.add_per_turn(synergia.bunch.Diagnostics_full2("turn_full2.h5"))
#    if diagnostic_flag == 'turn_particles':
#        bunch_simulator.add_per_turn(synergia.bunch.Diagnostics_particles("turn_particles.h5"))
    

#---------------------------
# Propagate
#---------------------------
# Ramp action is instantiated and passed to the propagator instance during the propagate method

    print "\n-------------------\n"
    print "           Nonlinear parameters will be CHANGED after each {} turns".format(updateAfterTurns)
    print "\n-------------------\n"

# Кe-setting the original 'bunch_origin' object, because it was changed (for some unknown reason) 
# while pulling a 'bunch' object through a fixed number of turns in a linear structure
    bunch_origin = synergia.optics.generate_matched_bunch_transverse(lattice_simulator_Crrnt, 1e-6, \
                                                          1e-6, 1e-3, 1e-4, 1e9, particlesInBunch, seed=1234)
# For checking (to verify that particles from "old" and "new" 'bunch_origin' objects are the same):
#     particlesOrg4 = bunch_origin.get_local_particles()
# To recognize attributes of 'particlesOrg2':
#     printAttributes(particlesOrg4,'particlesOrg4','bunch_origin.get_local_particles')
# End of checking (result: particles in both "old" and "new" objects are the same!)

    bunch = bunch_origin
# For checking:
#     particlesTmp2 = bunch.get_local_particles()
# To recognize attributes of 'particlesTmp2':
#     printAttributes(particlesTmp2,'particlesTmp2','bunch.get_local_particles')
#     particlesCrrnt2 = particlesTmp2.real
#     print "                 particlesCrrnt (again for nonlinear):"
#     for prtcl in range(5):
#         print "x (m) for particle {}: {}".format(prtcl,particlesCrrnt2[prtcl,0])
#         print "y (m) for particle {}: {}".format(prtcl,particlesCrrnt2[prtcl,2])
# End of checking

    bunch_simulator = synergia.simulation.Bunch_simulator(bunch)

    propagator = synergia.simulation.Propagator(stepper)
#     propagator.set_checkpoint_period(0)
#     propagator.set_checkpoint_with_xml(True)

# tracksNonLinear is 3D array: (totalTurns,bunchParticles,(x,y)) 
    tracksNonLinear = np.zeros((totalTurns,particlesInBunch,2))

    nUpdate = 0
    stepOfMgnfcn = 0
    totalTimeCPU = 0.
    for turnCrrnt in range(totalTurns):
        timeStart = os.times()
        propagatorCrrnt = propagator.propagate(bunch_simulator, 1, 1, 0)
# To recognize attributes of 'propagatorCrrnt':
#        printAttributes(propagatorCrrnt,'propagatorCrrnt', \
#                    'propagator.propagate(bunch_simulator, ramp_actions, 1, 1, 0)')
# bunchParticles is 2D array: (numberParrticles,(x,x',y,y',s,dE,ID))
        bunchParticles = bunch.get_local_particles()
# coordsTracks is 2D array: (bunchParticles,(x,y)) 
        coordsTracks = tracksCoords(bunchParticles)
        numbPartcls = bunchParticles.shape[0]
        for prtcl in range(numbPartcls):
            for k in range(2):
                tracksNonLinear[turnCrrnt,prtcl,k] = coordsTracks[prtcl,k]
#            if prtcl < 3:
#                print "tracksNonLinear (turn {}) for particle {}: x = {} mm, y = {} mm". \
#                format(turnCrrnt,prtcl,tracksNonLinear[turnCrrnt,prtcl,0], \
#                       tracksNonLinear[turnCrrnt,prtcl,1])
        turnNumber = turnCrrnt+1
        timeEnd = os.times()
        timeOfTurn = float(timeEnd[0] - timeStart[0])              # CPU time in seconds
        totalTimeCPU += timeOfTurn
        print ('Turn %3d is completed (CPU time = %6.3f seconds)' % (turnNumber, timeOfTurn))
        sys.stdout.flush()
        nUpdate += 1
        if nUpdate == updateAfterTurns:
            timeStart = os.times()
            plotcoordDistr(bunchParticles)
#== #
#== # Possibility to redefine parameters inside simulation:
#== #
#==             if updateInsideSmlnFlag == 1:
#==                 print "Old multiplyier for knl = {}".format(knlMultiplier)
#== # Multiplier 'knlMultiplier' is the same for all nonlinear lenses:   
#==                 knlMultiplier = float(raw_input('\nNew multiplyier for knl:'))
#==                 print "Old multiplyier for cnll = {}".format(cnllMultiplier)
#== # Multiplier 'cnllMultiplier' is the same for all nonlinear lenses:   
#==                 cnllMultiplier = float(raw_input('\nNew multiplyier for cnll:'))

#
# Args of 'Ramp_actions' method are: multiplier for knl and outputFlag 
#
            stepOfMgnfcn += 1
            knlMultiplier = magnifications[stepOfMgnfcn]
            print "strengthLens[",stepOfMgnfcn,"] = ",strengthLens[stepOfMgnfcn]
            nUpdate = 0
            print "\n              After {} turns:\n".format(turnNumber)
            ramp_actions = Ramp_actions(knlMultiplier, updateOutputFlag)   
            propagatorCrrnt = propagator.propagate(bunch_simulator, ramp_actions, 1, 1, 0)
            timeEnd = os.times()
            timeUpdateAndPlot = float(timeEnd[0] - timeStart[0])              # CPU time in seconds
            totalTimeCPU += timeUpdateAndPlot
            print ('\nUpdate and plotting are completed (CPU time = %6.3f seconds)\n' % timeUpdateAndPlot)
#     for prtcl in range(5):
#         print "x (mm) for particle {}: {}".format(prtcl,tracksNonLinear[:,prtcl,0])
#         print "y (mm) for particle {}: {}".format(prtcl,tracksNonLinear[:,prtcl,1])
    plotTracks(tracksNonLinear,5)
    print ('\nFor %5d turns CPU time = %6.3f seconds\n' % (totalTurns, totalTimeCPU))
    return
#
# End of main method 'simulation'

fileIOTA = ".../ioptics/ioptics/lattices/Iota8-2/lattice_1IO_nll_center.madx"
print "\nIOTA Nonlinear lattice: {} \n".format(fileIOTA)
lattice = synergia.lattice.MadX_reader().get_lattice("iota", \
    "../ioptics/ioptics/lattices/Iota8-2/lattice_1IO_nll_center.madx")

stepperCrrnt = synergia.simulation.Independent_stepper_elements(lattice,2,3)
lattice_simulator_Crrnt = stepperCrrnt.get_lattice_simulator()
# Bunch:
bunch_origin = synergia.optics.generate_matched_bunch_transverse(lattice_simulator_Crrnt, 1e-6, \
                                                          1e-6, 1e-3, 1e-4, 1e9, 1000, seed=1234)
#
# To compare two methods for drawing of the particles distributions:
#
loclTitle = "\nThese distributions were constructed using \
'synergia.optics.generated_matched_bunch_transverse' method"
loclTitle = loclTitle + \
"\nand plotted using two methods - 'pltbunch.plot_bunch' from the code synergia \nand 'plotcoordDistr' \
from this script (to verify method 'plotcoordDistr'):"
print loclTitle
pltbunch.plot_bunch(bunch_origin)     
# Distributions X-Y, X-X', Y-Y' using method 'plotcoordDistr':
bunchParticles = bunch_origin.get_local_particles()
# To recognize attributes of 'bunchParticles':
#     printAttributes(bunchParticles,'bunchParticles', 'bunch.get_local_particles()')
plotcoordDistr(bunchParticles)

selection = 'loop'
while selection == 'loop':
    simulation() 
    selection = raw_input("\nTo continue the simulation ('yes' or 'no'):")
    print'Your selection is ',selection
    if selection == 'yes':
        selection = 'loop'
#    if selection == 'no':
#        exit(0)