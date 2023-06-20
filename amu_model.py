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
    - build in unavailability to simulate other demands on time
does AC need unavailability too?

Constraints on AC capacity may mean pts suitable for SDEC/other pathway end up 
on AMU - need to simulate some type of timeout after which pt awaiting triage 
defaults to AMU route

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

AHAH:
capacity ???
are there 'opening hours', i.e. for accepting pts into service?
is AHAH really a direct sink of AC process or do pts always go somewhere
    like SDEC first?
"""

# Global parameters class
class g:

    # all time variables in minutes
    virtual_capacity = 1 # made up
    amu_capacity = 52
    #mtu_capacity = 6 - rolled into amu capacity for now
    sdec_capacity = 14
    adm_coordinator_capacity = 1 # assumed this for now
  
    patient_interarrival_time = 30 # made up
    probability_amu = 0.3 # made up
    mean_triage_time = 30 # made up

    mean_amu_stay_time = DAY_IN_MINS * 1.5 # 36h - made up
    mean_sdec_stay_time = 240 # made up
    mean_virtual_stay_time = 10 # made up

    sim_warm_up_time = DAY_IN_MINS
    sim_duration_time = WEEK_IN_MINS
    simulation_runs = 100


# Entity class
class patient:

    def __init__(self, patient_id, probability_amu):
        self.id = patient_id
        self.probability_amu = probability_amu
        self.amu_patient = False

        self.queue_for_triage = 0
        self.queue_for_amu_bed = 0
        self.queue_for_sdec_slot = 0

    def decide_route(self):
        if random.uniform(0, 1) < self.probability_amu:
            self.amu_patient = True


# Simulation environment class
class ACModel:
    """1"""
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env, capacity=g.adm_coordinator_capacity)
        self.amu_bed = simpy.Resource(self.env, capacity=g.amu_capacity)
        self.sdec_slot = simpy.Resource(self.env, capacity=g.sdec_capacity)
        self.virtual_slot = simpy.Resource(self.env, capacity = g.adm_coordinator_capacity)

        self.run_number = run_number

        self.mean_queue_time_triage = 0
        self.mean_queue_time_amu_bed = 0
        self.mean_queue_time_sdec_slot = 0
        self.mean_queue_time_virtual_slot = 0
        
        """2"""
        self.results_df = pd.DataFrame()
        self.results_df["Patient_ID"] = []
        self.results_df["Queue_time_triage"] = []
        self.results_df["Queue_time_amu_bed"] = []
        self.results_df["Queue_time_sdec_slot"] = []
        self.results_df.set_index("Patient_ID", inplace=True)

    # A method that generates patients arriving
    def generate_patients(self):
        # condense all incoming routes into one for now
        # but may need to revisit this
        while True:

            self.patient_counter +=1
            
            # Create a new patient
            pat = patient(self.patient_counter, g.probability_amu)

            # Determine the patient's AMU destiny by running the appropriate
            # method
            pat.decide_route()

            # Get the SimPy environment to run the ed_patient_journey method 
            # with this patient
            self.env.process(self.patient_pathway(pat))

            # Freeze this function until that time has elapsed
            yield self.env.timeout(random.expovariate(1.0 / g.patient_interarrival_time))

    def patient_pathway(self, patient):

        # Triage by Admissions Co-ordinator
        start_queue_triage = self.env.now

        # Requesting an Admissions Coordinator and freeze the function until the request for one can be met
        with self.adm_coordinator.request() as req:
            yield req

            # Record the time the patient finished queuing for the Admissions Coordinator, then calculate the time spent queuing and store with the patient
            end_queue_triage = self.env.now
            patient.queue_for_triage = end_queue_triage - start_queue_triage

            # Store the start and end queue times alongside the patient ID in
            # the Pandas DataFrame of the AC Model class
            df_to_add = pd.DataFrame({"Patient_ID":[patient.id],
                                      "Start_Q_Triage":[start_queue_triage],
                                      "End_Q_Triage":[end_queue_triage],
                                      "Queue_time_triage":[patient.queue_for_triage]})
            df_to_add.set_index("Patient_ID", inplace=True)
            print("Hello")
            pd.concat([self.results_df, df_to_add])
            print("Goodbye")
            
            # Randomly sample the time the patient will spend in triage
            # with the Admissions Coordinator  The mean is stored in the g class.            
            sampled_triage_duration = random.expovariate(1.0 / g.mean_triage_time)
            
            # Freeze this function until that time has elapsed
            yield self.env.timeout(sampled_triage_duration)

    """3"""
    # A method that calculates the average queuing time for an Admissions Coordinator (AC).  We can
    # call this at the end of each run
    def calculate_mean_q_time_triage(self):
        self.mean_queue_time_triage = (self.results_df["Queue_time_triage"].mean())
                    
    """4"""
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
        self.env.run(until=g.sim_duration_time)
        
        """5"""
        # Calculate run results
        self.calculate_mean_q_time_triage()
        
        # Write run results to file
        self.write_run_results()

"""6"""
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
for run in range(g.simulation_runs):
    print (f"Run {run+1} of {g.simulation_runs}")
    my_model = ACModel(run)
    my_model.run()
    print ()

# Once the trial is complete, we'll create an instance of the
# Trial_Result_Calculator class and run the print_trial_results method
"""8"""
my_trial_results_calculator = Trial_Results_Calculator()
my_trial_results_calculator.print_trial_results()

 















        # # AMU route
        # if patient.amu_patient is True:
        #     start_queue_amu_bed = self.env.now

        #     with self.amu_bed.request() as req:
        #         yield req

        #     end_queue_amu_bed = self.env.now
        #     patient.queue_for_amu_bed = end_queue_amu_bed - start_queue_amu_bed

        #     sampled_amu_stay_time = random.expovariate(1.0
        #                                                 / g.mean_amu_stay_time)
        #     yield self.env.timeout(sampled_amu_stay_time)

        # # SDEC route
        # else:
        #     start_queue_sdec_slot = self.env.now

        #     with self.sdec_slot.request() as req:
        #         yield req

        #     end_queue_sdec_slot = self.env.now
        #     patient.queue_for_sdec_slot = (end_queue_sdec_slot
        #                                     - start_queue_sdec_slot)

        #     sampled_sdec_stay_time = random.expovariate(1.0
        #                                                 / g.mean_sdec_stay_time)
        #     yield self.env.timeout(sampled_sdec_stay_time)
        
        # if self.env.now > g.sim_warm_up_time:
        #     self.store_patient_results(patient)

    # #def store_patient_results(self, patient):