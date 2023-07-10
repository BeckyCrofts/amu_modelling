#Becky Crofts & Kayleigh Haydock

import random
import csv
import pandas as pd
import simpy

# Constants
# Timeframe = minutes
# These save having to manually calculate common time units in minutes
DAY_IN_MINS = 1440
WEEK_IN_MINS = 10080


"""
Admissions Co-ordinator:
weekdays 10:00-20:00
weekends 07:00-19:30
AMU nurse in charge outside of these times
    - what is their availability like?
    - build in unavailability to simulate other demands on time?
does AC need unavailability too?

Constraints on AC capacity may mean pts suitable for SDEC/other pathway end up 
on AMU - need to simulate some type of timeout after which pt awaiting triage 
defaults to AMU route?

Are pts referred to triage hub ever rejected or sent to an entirely different
pathway outside of this model? If so need to identify the proportion and build
in as sink directly from the triage process - perhaps even need a different mean
triage duration?

SDEC:
capacity 14
weekdays 10:00-00:00
weekends 10:00-18:00
stops accepting new pts 3h before closing time
At closing time pts must be moved to either an AMU or base ward bed.
Technically there are cases where this can't happen and SDEC can't close on 
time - how regular and does this matter for the model?

AMU/MTU:
capacity 52
24/7

Ambulatory:
capacity 3
weekdays 09:00-18:00
closed weekends
might not be useful to model if all pre-booked or follow-up
    - is this really a sink for entities through AC process?

AHAH (virtual ward):
capacity ???
AHAH nurses working 7 days a week
weekday: 08:00-20:00 East, 08:00-18:00 North
weekend & BH: 08:00-18:00 East
out of hours support via Eastern team
do these hours correspond to 'opening hours' where referrals are accepted?
do patients go directly to AHAH or do they go somewhere like SDEC first?
should we be keeping AHAH pts alive in the model or should going to AHAH become
    a sink from the model?
    - pts not using bed resource
    - do they have any real contact with the system after triage and initial
        review with AHAH nurse?
"""

# Global parameters class
class G:

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
    days_of_week = {0: "week", 1: "week", 2: "week", 3: "week", 4: "week",
                    5: "weekend", 6: "weekend"}

    mean_amu_stay_time = DAY_IN_MINS * 1.5 # 36h - made up
    mean_sdec_stay_time = 240 # made up
    mean_virtual_stay_time = 10 # made up

    sim_warm_up_time = DAY_IN_MINS * 2
    sim_duration_time = WEEK_IN_MINS * 2
    simulation_runs = 1


# Entity class
class Patient:

    #def __init__(self, patient_id, probability_amu, probability_virtual):
    def __init__(self, patient_id):
        self.id = patient_id
        # self.probability_amu = probability_amu
        # self.probability_virtual = probability_virtual
        # self.amu_patient = False
        # self.virtual_patient = False
        # self.route_probability = random.uniform(0, 1)

        self.start_queue_triage = 0
        self.end_queue_triage = 0
        self.queue_for_triage = 0

        self.start_queue_amu_bed = 0
        self.end_queue_amu_bed = 0
        self.queue_for_amu_bed = 0

        self.start_queue_sdec_slot = 0
        self.end_queue_sdec_slot = 0
        self.queue_for_sdec_slot = 0

        self.start_queue_virtual_slot = 0
        self.end_queue_virtual_slot = 0
        self.queue_for_virtual_slot = 0

    # def decide_route(self):
    #     if self.route_probability  < self.probability_amu:
    #         self.amu_patient = True
    #     elif self.route_probability > (1 - self.probability_virtual):
    #         self.virtual_patient = True


# Simulation environment class
class AMUModel:

    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env,
                                            capacity=G.adm_coordinator_capacity)
        self.amu_bed = simpy.Resource(self.env,capacity=G.amu_capacity)
        self.sdec_slot = simpy.Resource(self.env, capacity=G.sdec_capacity)
        self.virtual_slot = simpy.Resource(self.env,
                                                capacity = G.virtual_capacity)

        self.run_number = run_number

        self.mean_queue_time_triage = 0
        self.mean_queue_time_amu_bed = 0
        self.mean_queue_time_sdec_slot = 0
        self.mean_queue_time_virtual_slot = 0
        
        # initialise the results dataframe for the run
        # this will contain a row per patient with data on their queue times
        self.results_df = pd.DataFrame()
        self.results_df["Patient_ID"] = []

        self.results_df["Start_Q_Triage"] = []
        self.results_df["End_Q_Triage"] = []
        self.results_df["Queue_time_triage"] = []

        self.results_df["Start_Q_AMU"] = []
        self.results_df["End_Q_AMU"] = []
        self.results_df["Queue_time_amu_bed"] = []

        self.results_df["Start_Q_SDEC"] = []
        self.results_df["End_Q_SDEC"] = []
        self.results_df["Queue_time_sdec_slot"] = []

        self.results_df["Start_Q_virtual"] = []
        self.results_df["End_Q_virtual"] = []
        self.results_df["Queue_time_virtual_slot"] = []

        self.results_df.set_index("Patient_ID", inplace=True)

    def check_day_and_hour(self, current_sim_time):
        
        day_to_sample = G.days_of_week[
                                    int((current_sim_time // DAY_IN_MINS) % 7)]
        
        hour_to_sample = int((current_sim_time -
                   (int(current_sim_time // DAY_IN_MINS) * DAY_IN_MINS)) // 60)
        
        return day_to_sample, hour_to_sample

    # A method that generates patients arriving
    def generate_patients(self):
        # condense all incoming routes into one for now
        # but may need to revisit this
        while True:

            self.patient_counter +=1
            
            # Create a new patient
            # pat = Patient(self.patient_counter, G.probability_amu,
            #                                             G.probability_virtual)
            pat = Patient(self.patient_counter)

            # Determine the patient's AMU destiny by running the appropriate
            # method
            # pat.decide_route()

            # Get the SimPy environment to run the patient_pathway method 
            # with this patient
            self.env.process(self.patient_pathway(pat))

            # Freeze this function until that time has elapsed
            yield self.env.timeout(random.expovariate(1.0 /
                                                G.patient_interarrival_time))

    def patient_pathway(self, patient):


        # Triage by Admissions Co-ordinator
        start_queue_triage = self.env.now
        #print(f"Patient number {patient.id}: "
        #        f"start queue for triage at {start_queue_triage}")

        # Requesting an Admissions Coordinator and freeze the function until the
        # request for one can be met
        with self.adm_coordinator.request() as req:
            yield req

            # Record the time the patient finished queuing for the Admissions
            # Coordinator, then calculate the time spent queuing and store with
            # the patient
            end_queue_triage = self.env.now
            #print(f"Patient number {patient.id}: "
            #        f"end queue for triage at {end_queue_triage}")
            patient.queue_for_triage = end_queue_triage - start_queue_triage
            print(f"Patient {patient.id} waited {patient.queue_for_triage} "
                    f"for triage")

            # Randomly sample the time the patient will spend in triage
            # with the Admissions Coordinator  The mean is stored in the g class
            sampled_triage_duration = random.expovariate(1.0 /
                                                            G.mean_triage_time)

            # Freeze this function until that time has elapsed
            yield self.env.timeout(sampled_triage_duration)

        
        # AMU route
        if patient.amu_patient is True:
            
            start_queue_amu_bed = self.env.now

            print(f"Patient {patient.id} is waiting for an AMU bed")

            with self.amu_bed.request() as req:
                yield req

            end_queue_amu_bed = self.env.now
            patient.queue_for_amu_bed = end_queue_amu_bed - start_queue_amu_bed
            print(f"Patient {patient.id} waited {patient.queue_for_amu_bed} "
                    "for an AMU bed")

            sampled_amu_stay_time = random.expovariate(1.0
                                                        / G.mean_amu_stay_time)
            yield self.env.timeout(sampled_amu_stay_time)

        # Virtual ward route
        if patient.virtual_patient is True:

            start_queue_virtual_slot = self.env.now

            print(f"Patient {patient.id} is waiting for a Virtual ward slot")

            with self.virtual_slot.request() as req:
                yield req

            end_queue_virtual_slot = self.env.now
            patient.queue_for_virtual_slot = (end_queue_virtual_slot -
                                                    start_queue_virtual_slot)
            print(f"Patient {patient.id} waited "
                    f"{patient.queue_for_virtual_slot} for a Virtual ward slot")

            sampled_virtual_stay_time = random.expovariate(1.0 /
                                                    G.mean_virtual_stay_time)
            yield self.env.timeout(sampled_virtual_stay_time)

        # SDEC route
        else:

            start_queue_sdec_slot = self.env.now

            print(f"Patient {patient.id} is waiting for an SDEC slot")

            with self.sdec_slot.request() as req:
                yield req

            end_queue_sdec_slot = self.env.now
            patient.queue_for_sdec_slot = (end_queue_sdec_slot
                                            - start_queue_sdec_slot)
            print(f"Patient {patient.id} waited {patient.queue_for_sdec_slot} "
                    f"for an SDEC slot")

            sampled_sdec_stay_time = random.expovariate(1.0
                                                        / G.mean_sdec_stay_time)
            yield self.env.timeout(sampled_sdec_stay_time)
        

            # only store the queue times for the patient if the run has finished
            # the warm up period
            if self.env.now > G.sim_warm_up_time:
                self.store_patient_results(patient)

    def store_patient_results(self, patient):

        if patient.amu_patient is True:
            patient.queue_for_sdec_slot = float("nan")
            patient.queue_for_virtual_slot = float("nan")
        elif patient.virtual_patient is True:
            patient.queue_for_sdec_slot = float("nan")
            patient.queue_for_amu_bed = float("nan")
        else:
            patient.queue_for_amu_bed = float("nan")
            patient.queue_for_virtual_slot = float("nan")

        # Store the start and end queue times alongside the patient ID in
        # the Pandas DataFrame of the AC Model class
        df_to_add = pd.DataFrame({"Patient_ID":[patient.id],
                                    "Start_Q_Triage":
                                                [patient.start_queue_triage],
                                    "End_Q_Triage":[patient.end_queue_triage],
                                    "Queue_time_triage":
                                                [patient.queue_for_triage]})
        df_to_add.set_index("Patient_ID", inplace=True)

        print(f"Patient number {patient.id} dataframe: {df_to_add}")

        self.results_df = pd.concat([self.results_df, df_to_add])


    # A method that calculates the average queuing time for an Admissions Coordinator (AC).  We can
    # call this at the end of each run
    def calculate_mean_q_time_triage(self):
        self.mean_queue_time_triage = (
                                    self.results_df["Queue_time_triage"].mean())


    # A method to write run results to file.  Here, we write the run number
    # against the the calculated mean queuing time for the AC across
    # patients in the run.  Again, we can call this at the end of each run
    def write_run_results(self):
        with open("trial_results.csv", "a") as f:
            writer = csv.writer(f, delimiter=",")
            results_to_write = [self.run_number,
                                self.mean_queue_time_triage]
            writer.writerow(results_to_write)


    # The run method starts up the entity generators, and tells SimPy to start
    # running the environment for the duration specified in the g class. After
    # the simulation has run, it calls the methods that calculate run
    # results, and the method that writes these results to file
    def run(self):
        # Start entity generators
        self.env.process(self.generate_patients())
        
        # Run simulation
        self.env.run(until=G.sim_duration_time)
        
        # Calculate run results
        self.calculate_mean_q_time_triage()
        
        # Write run results to file
        self.write_run_results()


# Class to store, calculate and manipulate trial results in a Pandas DataFrame
class Trial_Results_Calculator:
    # The constructor creates a new Pandas DataFrame, and stores this as an
    # attribute of the class instance
    def __init__(self):
        self.trial_results_df = pd.DataFrame()
        
    # A method to read in the trial results (that we wrote out elsewhere in the
    # code) and print them for the user
    def print_trial_results(self):
        print ("TRIAL RESULTS")
        print ("-------------")
        
        # Read in results from each run into our DataFrame
        self.trial_results_df = pd.read_csv("trial_results.csv")
        
        # Take average over runs
        trial_mean_q_time_ac = (
            self.trial_results_df["mean_queue_time_triage"].mean())
        
        print ("Mean Queuing Time for Triage Trial:",
               f"{trial_mean_q_time_ac:.2f}")

# Everything above is definition of classes and functions, but here's where
# the code will start actively doing things.        

# Create a file to store trial results, and write the column headers
"""7"""
with open("trial_results.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    column_headers = ["Run", "mean_queue_time_triage"]
    writer.writerow(column_headers)

# For the number of runs specified in the g class, create an instance of the
# GP_Surgery_Model class, and call its run method
for run in range(G.simulation_runs):
    print (f"Run {run+1} of {G.simulation_runs}")
    my_model = AMUModel(run)
    my_model.run()
    print ()

# Once the trial is complete, we'll create an instance of the
# Trial_Result_Calculator class and run the print_trial_results method
"""8"""
my_trial_results_calculator = Trial_Results_Calculator()
my_trial_results_calculator.print_trial_results()