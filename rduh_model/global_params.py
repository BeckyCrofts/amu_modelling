from datetime import time


# Global parameters class
class G:

    # constants
    DAY_IN_MINS = 1440
    WEEK_IN_MINS = 10080

    # all time variables in minutes
    virtual_capacity = 100 # made up - in reality there may not be a capacity limit
    virtual_open_time = time(8,0) # according to intranet
    virtual_close_time = time(20,0) # according to intranet
    amu_capacity = 46
    #mtu_capacity = 6
    sdec_capacity = 14
    sdec_open_time = time(8,30) # according to intranet
    sdec_close_time = time(20,0) # double check - closes later but stops accepting pts a few hours before closing time
    adm_coordinator_capacity = 1 # assumed this for now
    triage_wait_timeout = 60 # made up - how long a pt waits for triage before defaulting to AMU
  
    patient_interarrival_time = 30 # made up
    mean_triage_time = 30 # made up

    amu_only_interarrival_time = 30 # made up

    # used by check_day_and_hour function in model class to determine whether to
    # use week day or weekend day opening hours
    # assumes week starts on a Monday
    days_of_week = {0: 'week', 1: 'week', 2: 'week', 3: 'week', 4: 'week',
                    5: 'weekend', 6: 'weekend'}

    mean_amu_stay_time = DAY_IN_MINS * 1.5 # 36h - made up
    #mean_amu_stay_time = DAY_IN_MINS * 4 # 4d - made up
    mean_sdec_stay_time = 240 # 4h - made up
    mean_virtual_stay_time = DAY_IN_MINS * 5 # made up

    sim_warm_up_time = DAY_IN_MINS * 2
    sim_warm_up_perc = 10
    sim_duration_time = WEEK_IN_MINS * 2
    simulation_runs = 1