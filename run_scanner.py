#!/home/pi/berryconda3/bin/python

import os
import numpy as np
import time
import seabreeze.spectrometers as sb
from multiprocessing import Process
import logging

from openso2.scanner import Scanner, acquire_scan
from openso2.analyse_scan import analyse_scan
from openso2.call_gps import GPS
from openso2.program_setup import read_settings
from openso2.julian_time import hms_to_julian
from openso2.station_status import status_loop

#========================================================================================
#==================================== Set up logging ====================================
#========================================================================================

#############################################
import datetime
date = str(datetime.datetime.now().date())
#############################################

# Create log name
logname = f'log/{date}.log'
log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Make sure the log folder exists
if not os.path.exists('log'):
    os.makedirs('log')

# Create the logger
logging.basicConfig(filename=logname,
                    filemode = 'w',
                    format = log_fmt,
                    level = logging.INFO)

#========================================================================================
#=========================== Create comon and settings dicts ============================
#========================================================================================

# Create an empty dictionary to hold the comon parameters
common = {}

# Read in the station operation settings file
settings = read_settings('data_bases/station_settings.txt')

#========================================================================================
#============================= Connect to the spectrometer ==============================
#========================================================================================

# Find connected spectrometers
devices = sb.list_devices()

# Connect to spectrometer
spec = sb.Spectrometer(devices[0])

# Set intial integration time
spec.integration_time_micros(1.5e6)

# Record serial number in settings
settings['Spectrometer'] = str(spec.serial_number)
logging.info('Spectrometer ' + settings['Spectrometer'] + ' Connected')

#========================================================================================
#============================ Connect to the GPS and scanner ============================
#========================================================================================

# Connect to the GPS
gps = GPS()

# Connect to the scanner
scanner = Scanner()

#========================================================================================
#==================================== Start scanning ====================================
#========================================================================================

# Read in reference spectra
model_grid, common['so2_xsec'] = np.loadtxt('data_bases/Ref/so2.txt',  unpack = True)
model_grid, common['o3_xsec']  = np.loadtxt('data_bases/Ref/o3.txt',   unpack = True)
model_grid, common['no2_xsec'] = np.loadtxt('data_bases/Ref/no2.txt',  unpack = True)
model_grid, common['sol']      = np.loadtxt('data_bases/Ref/sol.txt',  unpack = True)
model_grid, common['ring']     = np.loadtxt('data_bases/Ref/ring.txt', unpack = True)
x, common['flat']              = np.loadtxt('data_bases/Ref/flat.txt', unpack = True)

# Set the model grid
common['model_grid'] = model_grid
common['wave_start'] = 305
common['wave_stop']  = 318

# Set the order of the background poly
common['poly_n'] = 3

# Add other parameters
common['params'] = [1.0, 1.0, 1.0, -0.2, 0.05, 1.0, 1.0e16, 1.0e17, 1.0e19]

# Set the station name
common['station_name'] = 'TEST'

# Create loop counter
common['scan_no'] = 0

# Create list to hold active processes
processes = []

#========================================================================================
#================================== Set up status loop ==================================
#========================================================================================

# Launch a seperate processs to keep the station status up to date
status_p = Process(target = status_loop)
status_p.start()

#========================================================================================
#=============================== Begin the scanning loop ================================
#========================================================================================

# Begin loop
while True:

    # Get scan start time
    lat, lon, alt, timestamp = gps.call_gps()
    jul_t = hms_to_julian(timestamp)

    # Create results folder if it doesn't exist
    datestamp = str(timestamp.date())
    common['fpath'] = 'Results/' + datestamp + '/'
    if not os.path.exists(common['fpath'] + 'so2/'):
        os.makedirs(common['fpath'] + 'so2/')
    if not os.path.exists(common['fpath'] + 'spectra/'):
        os.makedirs(common['fpath'] + 'spectra/')

    # Check if it is time to scan
    if jul_t > settings['start_time'] and jul_t < settings['stop_time']:

        logging.info('Begin scan ' + str(common['scan_no']))

        # Scan!
        common['scan_fpath'] = acquire_scan(scanner, gps, spec, common)

        # Clear any finished processes from the processes list
        processes = [pro for pro in processes if pro.is_alive()]

        # Check the number of processes. If there are more than two then don't start
        # another to prevent too many processes running at once
        if len(processes) <= 2:

            # Create new process to handle fitting of the last scan
            p = Process(target = analyse_scan, kwargs = common)

            # Add to array of active processes
            processes.append(p)

            # Begin the process
            p.start()

        else:
            # Log that the process was not started
            msg = f"Too many processes running, scan {common['scan_no']} not analysed"
            logging.warning(msg)

        common['scan_no'] += 1

    else:
        logging.info('Station sleeping')
        time.sleep(60)

