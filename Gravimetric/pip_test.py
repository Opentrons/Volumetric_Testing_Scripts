#!/usr/bin/env python

"""
Created by: Carlos Fernandez
Branch: Master
Last updated: 3/19/2018

"""


import os, sys
import time
import datetime
import optparse

import serial
import serial_communication as SC
import driver_3_0
import csv
import statistics

sys.path.insert(0, os.path.abspath('../Equipment'))
import Ragwag_Scale_Framework as SC

def uL_per_mm(pipette, volume, uL_mm):
    p_300 = ['P300', 'p300', 'p300_single']
    p_10 = ['P10', 'p10', 'p10_single']
    P300_Multi = ['P300_Multi', 'p300_multi, Multi_p300']
    P10_Multi = ['P10_Multi', 'p10_multi, Multi_p10']
    
    if pipette == p_10:
        pip_dist = (volume)/uL_mm
    elif pipette in p_300:
        pass
    elif pipette in P300_Multi:
        pass
    elif pipette in P10_Multi:
        pass
    else:
        pass
    return pip_dist
    
def set_relative(driver):
    driver._send_command('G91')

def set_absolute(driver):
    driver._send_command('G90')
    
def pipette_type(pipette):
    p_300 = ['P300', 'p300', 'p300_single']
    p_10 = ['P10', 'p10', 'p10_single']
    P300_Multi = ['P300_Multi', 'p300_multi', 'Multi_p300']
    P10_Multi = ['P10_Multi', 'p10_multi', 'Multi_p10']
    P_50  = ['P_50', 'P50', 'P50_Single']
    #Change these variables based on the setup
    print(pipette)
    if pipette in p_300:
        PIP_BOTTOM = 1
        BLOWOUT = -1
        raise_position = 70
        descend_position = 63
        pipette_speed = 5
        dispense_speed = 10
        A_axis_speed = 50
        print("P300-Single")
        return PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed
    elif pipette in P_50:
        PIP_BOTTOM = 2
        BLOWOUT = 0
        raise_position = 85
        descend_position = 80
        pipette_speed = 5
        dispense_speed = 10
        A_axis_speed = 50
        return PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed
    elif pipette in P300_Multi:
        PIP_BOTTOM = 2
        BLOWOUT = -1
        raise_position = 100
        descend_position = 90
        pipette_speed = 5
        dispense_speed = 10
        A_axis_speed = 50
        return PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed
    elif pipette in p_10:
        PIP_BOTTOM = 0
        BLOWOUT = -2
        raise_position = 68
        descend_position = 59
        pipette_speed = 5
        dispense_speed = 10
        A_axis_speed = 50
        print("P10-Single")
        return PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed
    elif pipette in P10_Multi:
        PIP_BOTTOM = 1
        BLOWOUT = -2
        raise_position = 84
        descend_position = 72
        pipette_speed = 5
        dispense_speed = 10
        A_axis_speed = 50
        return PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed
    else:
        print("Nothing set too")
        
def aspirate_action(aspirate_dist, backlash, relative=False):
    #Setting Variable for Pipettes
    PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed = pipette_type(options.pipette)
    
    if relative == True:
        #robot.home('b')
        set_absolute(robot)
        robot.move(c=PIP_BOTTOM)
        set_relative(robot)
        robot.move(c=backlash)
        set_absolute(robot)

        robot.move( a = descend_position, speed = A_axis_speed) #enter liquid
        set_relative(robot)
        robot.move( c = aspirate_dist, speed = pipette_speed)
        time.sleep(0.5)
        set_absolute(robot)

        robot.move( a = raise_position, speed = A_axis_speed) #exit liquid
        
    else:
        robot.move( c = PIP_BOTTOM)
        robot.move( c = backlash)
        robot.move( a = descend_position, speed = A_axis_speed) #enter liquid
        robot.move( c = aspirate_dist, speed = pipette_speed)
        robot.move( a = raise_position, speed = A_axis_speed) #exit liquid
        
    
def dispense_action(backlash, disp_dist, relative=False):

    PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed = pipette_type(options.pipette)
    
    if relative == True:
        relative_movement = -1 * (disp_dist)
        set_relative(robot)
        robot.move(c = relative_movement, speed = dispense_speed)
        set_absolute(robot)
    
    else:
        robot.move( a = descend_position+2, speed = A_axis_speed) #enter liquid
        robot.move( c = PIP_BOTTOM, speed = dispense_speed)
        robot.move( c = BLOWOUT, speed = 20)
        robot.move( a = raise_position, speed = A_axis_speed) #exit liquid  
        #robot.move( c = BLOWOUT, speed = dispense_speed)
        #robot.move(a = descend_position, speed = A_axis_speed)
        #robot.move(a = raise_position, speed = A_axis_speed)
       
        
def connect():
    robot.connect()

def setup_pipette(pipette):

    PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed = pipette_type(pipette)
    robot._reset_from_error()
    robot.home('AC')
    robot.move( c = PIP_BOTTOM)

def record_data(dist, i_mass, f_mass, log_file, test_data, test):
    delta = i_mass - f_mass
    volume = delta*1000 #uL
    
    test_data['Dist_Travel'] = dist
    test_data['Initial_Weight(g)'] = i_mass
    test_data['Final_Weight(g)'] = f_mass
    test_data['Delta_Weight(g)'] = delta
    test_data['Volume(uL)'] = volume
    test_data['time'] = time.strftime("%H:%M:%S", time.localtime())
    
    if test == 1:
        test_data['uL/mm'] = volume/dist
    else:
        test_data['CV'] = None
        test_data['average'] = None
        test_data['std'] = None
        
    log_file.writerow(test_data)
    print("Distance: ", dist)
    print("Volume: ", volume)
    
    #'Dist_Travel': None, 'Inital_Weight(g)':None,'Final_Weight(g)':None, 'Delta_Weight(g)':None, 
    #'Volume(uL)':None, 'time':None, 'CV':None, 'average':None, 'std':None
def prewet(pipette):
    setup_pipette(options.pipette)
    max_dist = 16
    PIP_BOTTOM, BLOWOUT, raise_position, descend_position,pipette_speed, dispense_speed, A_axis_speed = pipette_type(options.pipette)
    print(PIP_BOTTOM)
    #descend_position = 50
    for prewet in range(1):
        set_absolute(robot)
        #Move Pip Motor Bottom Position
        robot.move(c = PIP_BOTTOM)
        #Descend Z Position
        input('Press enter after changing tip')
        robot.move(a = descend_position, speed = A_axis_speed)
        #Aspirate Volume
        robot.move(c = max_dist, speed = pipette_speed)
        #Raise Z Position
        robot.move(a = raise_position, speed = A_axis_speed)
        #Descend Z Position
        robot.move(a = descend_position+2, speed = A_axis_speed)
        #Despense
        robot.move(c = PIP_BOTTOM, speed = dispense_speed)
        #Blowout
        robot.move(c = BLOWOUT, speed = dispense_speed)
        #Raise Z Position
        robot.move(a = raise_position, speed = A_axis_speed)
 

#Aspirate by increments
def Gravimetric(max_distance, backlash = 0.5, blowout_backlash = 0, aspirate_dist = 1, offset = 0):
    #Home Pipette Axis and Z Axis
    setup_pipette(options.pipette)
    test_type = 1
    #Create a Name for CSV File
    file_name = "results/Pipette_Data_%s.csv" % (datetime.datetime.now().strftime("%m-%d-%y_%H-%M"))
    #Open file and create Headers
    with open(file_name, 'w', newline='') as f:
        test_data = {'Dist_Travel': None, 'Initial_Weight(g)':None,'Final_Weight(g)':None, 'Delta_Weight(g)':None, 'Volume(uL)':None, 'uL/mm':None, 'time':None}
        log_file = csv.DictWriter(f, test_data)
        log_file.writeheader()
        #Number of cycles to Run Formula
        cycles = int(max_distance/aspirate_dist)
        #Increment Value
        current_aspirate_dist = aspirate_dist + offset
        #Series of moves
        for cycle in range(cycles+1):
            print('current distance = ', current_aspirate_dist)
            #Pause for 2 Seconds
            time.sleep(2)
            #Take Initial Reading
            initial = GB_Scale.read_mass()
            time.sleep(2)
            #aspirate
            aspirate_action(current_aspirate_dist, backlash=backlash, relative=True)
            time.sleep(2)
            #take final reading
            final = GB_Scale.read_mass()
            #dispense
            dispense_action(disp_dist=current_aspirate_dist + 1, backlash=backlash, relative = False)
            #record and calculate values
            if cycle => 1:
                record_data(current_aspirate_dist, initial, final, log_file, test_data, 1)    
                #Increment aspirate dist        
                current_aspirate_dist += aspirate_dist
            else:
                pass
        
#Aspirate with constant Volumes
def const_vol(cycles, backlash=0.5, blowout_backlash=0, aspirate_dist=10):
    setup_pipette(options.pipette)
    test_type = 0
    file_name = "results/Pipette_Data_%s.csv" % (datetime.datetime.now().strftime("%m-%d-%y_%H-%M"))
    with open(file_name, 'w', newline='') as f:
        test_data = { 'Dist_Travel': None, 'Initial_Weight(g)':None,'Final_Weight(g)':None, 'Delta_Weight(g)':None, 'Volume(uL)':None, 'time':None, 'CV':None, 'average':None, 'std':None}
        log_file = csv.DictWriter(f, test_data)
        log_file.writeheader()
        #aspirate_increment = aspirate_dist / cycles #0.1
        #current_aspirate_dist = aspirate_increment #+ 0.63
        current_aspirate_dist = aspirate_dist
        list_sum = []
        for cycle in range(cycles+1):
            print('current distance = ', current_aspirate_dist)
            time.sleep(3)
            initial = GB_Scale.read_mass()
            time.sleep(2)
            aspirate_action(current_aspirate_dist, backlash=backlash, relative=True)
            time.sleep(3)
            final = GB_Scale.read_mass()
            #input('press enter to dispense')
            dispense_action(disp_dist = current_aspirate_dist + 1, backlash=backlash, relative=False)
            if cycle => 1:
                record_data(current_aspirate_dist, initial, final, log_file, test_data, 0)
                volume = (final-initial)*1000
                list_sum.append(volume)
            else:
                pass
            
        list_sum.pop(0)
        print(list_sum)
        average = abs(sum(list_sum)/len(list_sum))
        std = statistics.stdev(list_sum)
        CV = (std/average)*100
        test_data['average'] = average
        test_data['std'] = std
        test_data['CV'] = CV
        log_file.writerow(test_data)
        print("CV:",CV)
            #current_aspirate_dist += aspirate_increment
        
if __name__ == '__main__':
    #options to pick from
    parser = optparse.OptionParser(usage='usage: %prog [options] ')
    parser.add_option("-s", "--speed", dest = "speed", type = 'int', default = 30, help = "Speed Value")
    parser.add_option("-c", "--cycles", dest = "cycles", type = 'int', default = 10, help = "Number of Cycles to run")
    parser.add_option("-S", "--scale_port", dest = "scale_port", type = 'str', default = 'COM7', help = "Scale COM Port")
    parser.add_option("-t", "--test", dest = "test", default = "Fixed", type = 'str', help = "Test Type, Gravi or Fixed")
    parser.add_option("-m", "--max", dest = "max_dist", default = 17.4, type = 'float', help = 'max distance to travel for Gravi(ONLY FOR GRAVI)')
    parser.add_option("-a", "--aspir_incre", dest = "aspir_incre", default = 1, help = 'Gravimetric Increment step 1mm = default(ONLY FOR GRAVI)')
    parser.add_option("-d", "--dist", dest = "dist", default = 13, type = 'float', help = 'Distance to travel for fixed(ONLY FOR FIXED)')
    parser.add_option("-p", "--p", dest = "pipette", default = 'P50', type = 'str', help = 'Pipette Type as string')
    parser.add_option("-v", "--v", dest = "volume", default = 10.3, type = 'float', help = 'volume for pipette')
    (options, args) = parser.parse_args(args = None, values = None)
    #print(options.scale_port)
    #GB_Scale = SC.Scale(port = options.scale_port)
    GB_Scale = SC.Ragwag_Scale(options.scale_port)
    #Create a variable to read Scale Readings
    reading = GB_Scale.read_mass()
    
    robot = driver_3_0.SmoothieDriver_3_0_0()
    
    try:
        #Fixed Volume
        constant = ['Fixed','fixed', 'fix']
        #Incremental Test
        gravimetric = ['Gravi', 'gravi', 'Gravimetric', 'gravimetric']
        pip_prewet = ['Prewet','prewet']
        robot.connect()
        #distance = uL_per_mm(options.pipette, options.volume)
        print("Start test")
        if options.test in constant:
            const_vol(options.cycles, backlash = 0.5, aspirate_dist = options.dist)
        elif options.test in gravimetric:
            Gravimetric(options.max_dist, backlash= 0.5, blowout_backlash=0, aspirate_dist = options.aspir_incre)
        elif options.test in pip_prewet:
            prewet(options.pipette)
        else: 
            print("No String Passed", options.test)
        
    except KeyboardInterrupt:
        robot.disable_motors()
        print("Test Cancelled")
    except Exception as e:
        print("ERROR OCCURED")
        #test_data['Errors'] = e
        #log_file.writerow(test_data)
        #f.flush()
        robot.disable_motors()
        raise e
    
    print("Test done")
    robot.disable_motors()
