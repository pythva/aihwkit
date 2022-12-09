import time
import pymysql
import cpppo
from cpppo.history import timestamp
from cpppo.server.enip import poll
from cpppo.server.enip.get_attribute import proxy_simple as device
import logging
import sys
import threading
import traceback

### CPPPO Historian Poller Code

# List of global PLC variables to read. Excludes *_Cmd_Run_Man and Motor_Power_On
# variables to save time, assumes the value of these based upon the Kivy button settings.
params	= [#('TC1_Cmd_Run_Man'),
           #('TC2_Cmd_Run_Man'),
           #('TC3_Cmd_Run_Man'),
           #('TC4_Cmd_Run_Man'),
           ('TC1_Cmd_SP_Man'),
           ('TC2_Cmd_SP_Man'),
           ('TC3_Cmd_SP_Man'),
           ('TC4_Cmd_SP_Man'),
           ('Motor_SP'),
           ('TC1_Out_Temp'),
           ('TC2_Out_Temp'),
           ('TC3_Out_Temp'),
           ('TC4_Out_Temp'),
           ('Motor_Tach_RPM'),
           #('Motor_Power_On'),
           ('Motor_Load_Current_PV'),
           ('Pressure_PV')]

# create failure and process value dictionaries
def failure( exc ):
    failure.string.append( str(exc) )
failure.string	= [] # [ <exc>, ... ]

def process( par, val ):
    process.values[par]	= val

# Device IP address as defined in Connected Components Workbench
hostname = ############# expcuded for privacy

# create device gateway and poller 
via = device(host = hostname, port = 44818, timeout = 0.7)
poller = threading.Thread(
    target=poll.poll, kwargs={
        'via': via,
        #'proxy_class':  device,
        #'address':      (hostname, 44818),
        'cycle':        1.0,
        #'timeout':      0.5,
        'process':      process,
        'failure':      failure,
        'params':       params,
    })
# start poller
process.done = False
process.values = {} # { <parameter>: <value>, ... }

def write_to_plc(plc_global_var, var_type, set_value):
    '''
    Protocol for writing to the global variables on the PLC. Recall that it is only
    possible to read/write global variables.
    Code is mostly borrowed from CPPPO: cpppo/server/enip/poll_example_many_with_write.py
    
    Inputs:
        plc_global_var:
            - Type: String
            - Value: Global variable name on PLC to write to
        var_type:
            - Type: String
            - Value: PLC variable type (BOOL, REAL, etc.)
        set_value:
            - Type: Integer or float
            - Value:
                * For BOOL: 1 = True, 0 = False
                * For REAL: any float value
    
    Outputs:
        None
    '''
    try:

        # create parameter command tag
        param = '%s = (%s)%s' % (plc_global_var, var_type, set_value)
        with via: # establish gateway, detects Exception (closing gateway)
            # sends command to plc
            val, = via.write(
                    via.parameter_substitution( param ), checking=True )
        print( "%s: %-32s == %s" % ( timestamp(), param, val ))
    except Exception as exc: 
        # log failure if write unsuccessful
        logging.detail( "Exception writing Parameter: %s, %s", exc, traceback.format_exc() )
        failure( exc )
        print( "Failed request: %s: %-32s == %s" % ( timestamp(), param, val ))
    return

if __name__ == '__main__':
    # if running this file as main:
    # start the poller
    poller.start()


    write_to_plc('TC1_Cmd_Run_Man', 'BOOL', 1)
    write_to_plc('TC1_Cmd_Stop_Man', 'BOOL', 0) # write command to the PLC 

    while True: # report the status of the PLC
        while process.values:
            par,val = process.values.popitem() 
            print( "%s: %16s == %r" % ( time.ctime(), par, val )) 
        print("next_times")
        med = int(input("stop ?1 "))
        if(med == 1):
            break
