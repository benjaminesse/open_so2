# -*- coding: utf-8 -*-
"""
Module to read in settings files to initiate the main program.
"""

from tkinter import filedialog as fd

#==============================================================================
#================================= read_setttings =============================
#==============================================================================

def read_settings(fname, settings = None):

    '''
    Fuction to read in the settings file
    
    **Parameters:**
        
    fname : str
        File path to settings file

    settings : dict (optional)
        Dictionary of GUI settings. If None then one is created.

    **Returns:**
        
    settings : dict (optional)
        Setting dictionary created or updated with setings from the file. 

    Written by Ben Esse, January 2019
    '''

    # Create the settings dictionary if not given
    if settings == None:
        settings = {}

    # Open the settings file
    with open(fname, 'r') as r:

        # Read data line by line
        data = r.readlines()

        # Unpack and save to dictionary
        for i in data:
            name, val, dtype = i.strip().split(';')

            # Get the parameter value and change to correct variable type
            if dtype == "<class 'float'>":
                settings[name] = float(val)


            if dtype == "<class 'int'>":
                settings[name] = int(val)


            if dtype == "<class 'bool'>":
                if val == 'True':
                    settings[name] = True
                if val == 'False':
                    settings[name] = False


            if dtype == "<class 'str'>":
                settings[name] = str(val)

    return settings

#==============================================================================
#============================== Get Station Info ==============================
#==============================================================================

def get_station_info(fpath):

    '''
    Function to read in the station information and complile it into a 
    dictionary

    **Parameters:**
        
    fpath : str
        File path to the station info text file

    **Returns:**
        
    station_info : dict
        Dictionary of all the station information required by the main program. 
        Each station is its own dictionary within station_info

    Written by Ben Esse, January 2019
    '''

    # Create dictoinary to populate
    station_info = {}

    # Open the file
    with open(fpath, 'r') as r:

        # Read the header line
        r.readline()

        # Read in the rest of the data
        data = r.readlines()

        # Unpack the information
        for line in data:

            # Split the data in the line
            name, host, username, password = line.strip().split(';')

            # Add this data to the dictionary, removing any whitespace
            name = name.strip()
            station_info[name] = {'host':     host.strip(),
                                  'username': username.strip(),
                                  'password': password.strip()}

    return station_info

#==============================================================================
#=========================== Update results folder ============================
#==============================================================================

def update_resfp(self):

    '''
    Function to change the results file location

    **Parameters:**
        
    self : tk.Tk
        Program object containing parameters

    **Returns:**
        
    None
    '''

    # Open dialouge to get files
    fpath = fd.askdirectory()

    if fpath != '':
        self.res_fpath.set(fpath + '/')

#==============================================================================
#============================= Update scan files ==============================
#==============================================================================

def update_scanfp(self):

    '''
    Function to change the scans to analyse

    **Parameters:**
        
    self : tk.Tk
        Program object containing parameters

    **Returns:**
        
    None
    '''

    # Open dialouge to get files
    fpaths = fd.askopenfilenames()

    if fpaths != '':
        self.scan_fpaths = []
        for f in fpaths:
            self.scan_fpaths.append(str(f))
            
        self.scan_ent.set(str(len(self.scan_fpaths)) + ' scans selected')











