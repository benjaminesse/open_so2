# -*- coding: utf-8 -*-
"""
Module to convert traditional time stamps to Julian time (decimal hours or 
days) and back
"""

import numpy as np
import datetime as dt

#==============================================================================
#=============================== hms_to_julian ================================
#==============================================================================

def hms_to_julian(times, str_format = None, out_format = 'decimal hours'):
    
    '''
    Function to convert an array of datetime objects or strings to julian time
    
    **Parameters:**
        
    times : array, datetime.datetime or str
        Origional time objects
        
    str_format : str (optional)
        Time format if converting from strings. Default is None
        
    out_format : str (optional)
        Format of output. Must be either "decimal hours" or "decimal days". 
        Default is decimal hours
                   
    **Returns:**
        
    jul_time : array
        Array of julian time values calculated form the input array
    '''
    
    # Check if output format is correct
    if out_format not in ['decimal days', 'decimal hours']:
        msg = 'out_format value is not supported. '  + \
              'Only supported values are:\n    decimal days\n    decimal hours'
        raise ValueError(msg)
    
    # If single value, convert to list
    if type(times) in [str, dt.datetime, dt.time]:
        times = [times]
        single_flag = True
    else:
        single_flag = False
    
    # Make julian time array object to populate
    jul_time = np.zeros(len(times))
    
    # Iterate through time array and convert
    for n, time in enumerate(times):

        # If format is given, use this to convert to datetime object
        if str_format != None:
            try:
                time = dt.datetime.strptime(str(time), str_format)
            except ValueError:
                try:
                    time = dt.datetime.strptime(str(time), '%H:%M:%S')
                except ValueError:
                    time = dt.datetime.strptime(str(time), '%H:%M:%S.%f')
                
        
        # Extract individual hour, minute, second and microsecond info
        hours = time.hour
        mins  = time.minute
        secs  = time.second
        usecs = time.microsecond
        
        # Convert to either decimal days or decimal hours
        if out_format == 'decimal days':
            jul_time[n] = (hours/24) + (mins/1440) + (secs/86400) + (usecs/8.64e10)
        if out_format == 'decimal hours':
            jul_time[n] = (hours) + (mins/60) + (secs/3600) + (usecs/3.6e+9)
    
    if single_flag:
        return jul_time[0]
    else:
        return jul_time
            
#==============================================================================
#=============================== julian_to_hms ================================
#==============================================================================
        
def julian_to_hms(time_arr, input_format = 'decimal hours', 
                  output_format = 'datetime'):

    '''
    Function to convert an array of Julian times into hh:mm:ss datetime objects
    
    **Parameters:**
        
    time_arr : arrray
        Origional julan time values
        
    input_format : str (optional)
        Describes the format of the input Julian time values. Either "decimal 
        days" (default) or "decimal hours"
        
    output_format : str (optional)
        Describes the format of the output:
            - "datetime": Returns a datetime.datetime object (default)
            - "hms":      Returns a string in the format of "HH:MM:SS"
                    
    **Returns:**
        
    time : array
        Datetime objects
    '''

    # Check if intput and output formats are correct
    if input_format not in ['decimal days', 'decimal hours']:
        msg = 'input_format value is not supported. '  + \
              'Only supported values are:\n    decimal days\n    decimal hours'
        raise ValueError(msg) 
    if output_format not in ['datetime', 'hms']:
        msg = 'output_format value is not supported. '  + \
              'Only supported values are:\n    datetime\n    hms'
        raise ValueError(msg)
    
    # If single value, convert to list
    if type(time_arr) not in [list, np.array]:
        time_arr = [time_arr]
        single_flag = True
    else:
        single_flag = False
        
    # Make array to hold datetime objects
    time = []
    
    # Cycle through the input array to produce datetime objects
    for n, t in enumerate(time_arr):
        
        # Get hour data, depending on whether its decomal days or hours
        if input_format == 'decimal days':
            
            hours = t * 24
            h = int(hours)
            delta_h = hours - h
            
        if input_format == 'decimal hours':
            
            h = int(t)
            delta_h = t - h
        
        # Extract minute, second and microsecond info 
        mins = delta_h * 60
        m = int(mins)
        delta_m = mins - m
        
        secs = delta_m * 60
        s = int(secs)
        delta_s = secs - s
        
        usecs = delta_s * 1e6
        u = int(usecs)
        
        # Combine to form a time object
        if output_format == 'datetime':
            time.append(dt.datetime(1900, 1, 1, h, m, s, u).time())
        if output_format == 'hms':
            time.append(f'{h:02}:{m:02}:{s:02}')
    
    if single_flag:
        return time[0]
    else:
        return time
            
#==============================================================================
#=============================== julian_to_str ================================
#==============================================================================
