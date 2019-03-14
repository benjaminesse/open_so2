# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 15:34:46 2018

@author: mqbpwbe2
"""

import numpy as np
import logging
import board
import atexit
import digitalio
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time

class Scanner:

    '''
    Scanner class used to control the scanner head which consists of a stepper motor and
    a microswitch

    INPUTS
    ------
    uswitch_pin, int (optional)
        The GPIO pin that connects to the microswitch. Default is 21

    METHODS
    -------
    find_home
        Function that rotates the scanner to the home position

    move
        Moves the scanner by a specified number of steps
    '''

    # Initialise
    def __init__(self, uswitch_pin = 21):

        # Define the GPIO pins
        gpio_pin = {'4':  board.D4,
                    '5':  board.D5,
                    '6':  board.D6,
                    '12': board.D12,
                    '13': board.D13,
                    '16': board.D16,
                    '17': board.D17,
                    '18': board.D18,
                    '19': board.D19,
                    '20': board.D20,
                    '21': board.D21,
                    '22': board.D22,
                    '23': board.D23,
                    '24': board.D24,
                    '25': board.D25,
                    '27': board.D27}

        # Connect to the micro switch
        self.uswitch = digitalio.DigitalInOut(gpio_pin[str(uswitch_pin)])
        self.uswitch.direction = digitalio.Direction.INPUT
        self.uswitch.pull = digitalio.Pull.UP

        # Connect to the stepper motor
        self.motor = MotorKit().stepper1

        # Define function to release the stepper at exit
        def release_motor():
            self.motor.release()
        atexit.register(release_motor)

        # Set the motor position to zero
        self.position = 0

#========================================================================================
#======================================= Find Home ======================================
#========================================================================================

    def find_home(self):

        '''
        Function to rotate the scanner head to the home position

        INPUTS
        ------
        motor, motor object
            The object for the stepper motor

        uswitch, micro switch object
            The object for the micro switch

        OUTPUTS
        -------
        None
        '''

        # First check if the switch is turned on
        if not self.uswitch.value:

            # Rotate until it is on
            self.step(steps = 100, steptype = 'interleave')

        # Step the motor until the switch turns off
        home = False
        i = 0
        while not home:

            # Move the motor one step
            self.step(steptype = 'interleave')
            i += 1
            # Check if the scanner is home. Connection with switch can fail, so check
            # after 1 second
            if not self.uswitch.value:

                # Sleep one second
                time.sleep(1)

                # Check if really home
                if not self.uswitch.value:
                    home = True
                    logging.info('Steps to home: ' + str(i))

        # Once home set the motor position to 0
        self.position = 0

#========================================================================================
#======================================= Move Motor =====================================
#========================================================================================

    def step(self, steps = 1, steptype = 'interleave', direction = 'backward'):

        '''
        Function to move the motor by a given number of steps

        INPUTS
        ------
        motor, motor object
            The object for the stepper motor

        steps, int
            Number of steps to move

        steptype, str
            Stepping type. Must be one of:
                - single;     single step (lowest power)
                - double;     double step (more power but stronger)
                - interleave; finer control, has double the steps of single
                - micro;      slower but with much higher precision (8x)

        direction, str
            Stepping direction, either 'forward' or 'backward'

        OUTPUTS
        -------
        None
        '''

        # Set stepping mode dict
        step_mode = {'single':     stepper.SINGLE,
                     'double':     stepper.DOUBLE,
                     'interleave': stepper.INTERLEAVE,
                     'micro':      stepper.MICROSTEP}

        # Set stepping direction dict
        step_dir = {'forward':  stepper.FORWARD,
                    'backward': stepper.BACKWARD}

        for i in range(steps):
            self.motor.onestep(direction = step_dir[direction],
                               style = step_mode[steptype])

        # Update the motor postion
        if direction == 'backward':
            self.position -= steps
        elif direction == 'forward':
            self.position += steps

        # Write position to file
        try:
            with open('Station/position.txt', 'w') as w:
                w.write(str(self.position))
        except:
            pass

#========================================================================================
#===================================== Acuire Scan ======================================
#========================================================================================

def acquire_scan(Scanner, GPS, Spectrometer, common):

    '''
    Function to perform a scan. Simultaneously analyses the spectra from the previous
    scan while aquiring the current one

    INPUTS
    ------
    GUI, tk.Tk object
        Object for the main GUI of the control program

    Scanner, openso2 Scanner object
        Object to control the scanner head consisting of a stepper motor and a
        microswitch

    GPS, openso2 GPS object
        Object to control the GPS module for location and date/time information

    Spectrometer, Seabreeze.Spectrometer object
        Object to control the spectrometer

    OUPUTS
    ------
    fpath, str
        File path to the saved scan

    Written by Ben Esse, January 2019
    '''

    # Create array to hold scan data
    scan_data = np.zeros((101, 2055))

    # Return the scanner position to home
    Scanner.find_home()

    # Take the dark spectrum
    dark = Spectrometer.intensities()
    scan_data[0] = np.append(np.array([0, 0, 0, 0, Scanner.position, 0, 0]), dark)

    # Move scanner to start position
    logging.info('Moving to start position')
    Scanner.step(steps = 50)

    # Begin stepping through the scan
    for step_no in range(1, 101):

        # Acquire spectrum
        spec_int = Spectrometer.intensities()

        # Get time
        y, mo, d, h, m, s = GPS.get_time()

        # Add the data to the array
        # Has the format N_acq, Hour, Min, Sec, MotorPos, Coadds, Int time
        scan_data[step_no] = np.append(np.array([step_no, h, m, s, Scanner.position,0,0]),
                                       spec_int)

        # Step the scanner
        Scanner.step(2)

    # Scan complete
    logging.info('Scan complete')

    # Save the scan data
    fname = str(y) + str(mo) + str(d) + '_' + str(h) + str(m) + str(s) + '_' + \
            common['station_name'] + '_v_1_1_Block' + str(common['scan_no']) + '.npy'
    fpath = common['fpath'] + 'spectra/' + fname

    np.save(fpath, scan_data.astype('float16'))

    # Return the filepath to the save scan
    return fpath
