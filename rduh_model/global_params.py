# Global parameters class
class G:

    # constants
    DAY_IN_MINS = 1440
    WEEK_IN_MINS = 10080

    # all time variables in minutes
    virtual_capacity = 100 # made up - in reality there may not be a capacity limit
    amu_capacity = 52
    #mtu_capacity = 6 - rolled into amu capacity for now - not clear on distinction
    sdec_capacity = 14
    adm_coordinator_capacity = 1 # assumed this for now
  
    patient_interarrival_time = 30 # made up
    mean_triage_time = 30 # made up

    # these need to be replaced with hourly probabilities to simulate SDEC being
    # closed and AMU picking up those patients
    # also need different values for week/weekend as sdec open hours differ
        # numbers of referrals in may differ on this too
    # may also need similar for AHAH if that route isn't available overnight
    #probability_amu = 0.4 # made up
    #probability_virtual = 0.1 # made up

    # nested dictionary with probabilities of patients going down a certain
    # route depending on week day v weekend day and hour of day
    # value of 0 represents a route being closed at that time
    # values across all pathways should sum to 1.0 for each given time of day
    hourly_route_probabilities = {
        'sdec': {
                'week':     {#SDEC closed
                            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0,
                            8: 0, 9: 0,
                            #SDEC open
                            10: 0.5, 11: 0.5, 12: 0.5, 13: 0.5, 14: 0.5,
                            15: 0.5, 16: 0.5, 17: 0.5, 18: 0.5, 19: 0.5,
                            20: 0.5,
                            #SDEC closed
                            21: 0, 22: 0, 23: 0},
                'weekend':  {#SDEC closed
                            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0,
                            8: 0, 9: 0,
                            #SDEC open
                            10: 0.5, 11: 0.5, 12: 0.5, 13: 0.5, 14: 0.5,
                            #SDEC closed
                            15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0,
                            21: 0, 22: 0, 23: 0}
                },
        'amu': {
                'week':     {#SDEC and virtual closed
                            0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
                            6: 1.0, 7: 1.0,
                            #SDEC closed, virtual open
                            8: 0.9, 9: 0.9,
                            #SDEC and virtual open
                            10: 0.4, 11: 0.4, 12: 0.4, 13: 0.4, 14: 0.4,
                            15: 0.4, 16: 0.4, 17: 0.4, 18: 0.4, 19: 0.4,
                            20: 0.4,
                            #SDEC and virtual closed
                            21: 1.0, 22: 1.0, 23: 1.0},
                'weekend':  {#SDEC and virtual closed
                            0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
                            6: 1.0, 7: 1.0,
                            #SDEC closed, virtual open
                            8: 0.9, 9: 0.9,
                            #SDEC and virtual open
                            10: 0.4, 11: 0.4, 12: 0.4, 13: 0.4, 14: 0.4,
                            #SDEC closed, virtual open
                            15: 0.9, 16: 0.9, 17: 0.9,
                            #SDEC and virtual closed
                            18: 1.0, 19: 1.0, 20: 1.0, 21: 1.0, 22: 1.0,
                            23: 1.0}
                },
        'virtual':{
                'week':     {#virtual closed
                            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0,
                            #virtual open
                            8: 0.1, 9: 0.1, 10: 0.1, 11: 0.1, 12: 0.1, 13: 0.1,
                            14: 0.1, 15: 0.1, 16: 0.1, 17: 0.1, 18: 0.1,
                            19: 0.1,
                            #virtual closed
                            20: 0, 21: 0, 22: 0, 23: 0},
                'weekend':  {#virtual closed
                            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0,
                            #virtual open
                            8: 0.1, 9: 0.1, 10: 0.1, 11: 0.1, 12: 0.1, 13: 0.1,
                            14: 0.1, 15: 0.1, 16: 0.1, 17: 0.1,
                            #virtual closed
                            18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0}
                }
    } # all of these values are made up and just for testing
    # assumed virtual route opening hours

    # used by check_day_and_hour function in model class to determine whether to
    # use week day or weekend day opening hours
    # assumes week starts on a Monday
    days_of_week = {0: 'week', 1: 'week', 2: 'week', 3: 'week', 4: 'week',
                    5: 'weekend', 6: 'weekend'}

    mean_amu_stay_time = DAY_IN_MINS * 1.5 # 36h - made up
    mean_sdec_stay_time = 240 # made up
    mean_virtual_stay_time = 10 # made up

    sim_warm_up_time = DAY_IN_MINS * 2
    sim_warm_up_perc = 10
    sim_duration_time = WEEK_IN_MINS * 2
    simulation_runs = 1