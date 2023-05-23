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

SDEC:
capacity 14
weekdays 10:00-00:00
weekends 10:00-18:00
stopd accepting new pts 3h before closing time

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
class G:

    # all time variables in minutes

    amu_capacity = 52
    #mtu_capacity = 6 - rolled into amu capacity for now
    sdec_capacity = 14
    adm_coordinator_capacity = 1 # assumed this for now
  
    patient_interarrival_time = 30 # made up
    probability_amu = 0.3 # made up
    mean_triage_time = 30 # made up

    mean_amu_stay_time = DAY_IN_MINS * 1.5 # 36h - made up
    mean_sdec_stay_time = 240 # made up

    sim_warm_up_time = DAY_IN_MINS
    sim_duration_time = WEEK_IN_MINS
    simulation_runs = 2


# Entity class
class Patient:

    def __init__(self, patient_id, probability_amu):
        self.id = patient_id
        self.probability_amu = probability_amu
        self.amu_patient = False

        self.queue_for_triage = 0
        self.queue_for_bed = 0

    def decide_route(self):
        if random.uniform(0, 1) < self.probability_amu:
            self.amu_patient = True


# Simulation environment class
class AMUModel:

    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env, 
                                            capacity=G.adm_coordinator_capacity)
        self.amu_bed = simpy.Resource(self.env, capacity=G.amu_capacity)
        self.sdec_bed = simpy.Resource(self.env, capacity=G.sdec_capacity)

        self.run_number = run_number

        self.mean_queue_time_triage = 0
        self.mean_queue_time_bed = 0

        self.results_df = pd.DataFrame()
        self.results_df["Patient_ID"] = []
        self.results_df["Queue_time_triage"] = []
        self.results_df["Queue_time_bed"] = []
        self.results_df.set_index("Patient_ID", inplace=True)

    def generate_patients(self):
        # condense all incoming routes into one for now
        # but may need to revisit this
        while True:

            self.patient_counter +=1

            pat = Patient(self.patient_counter, g.probability_amu)

            pat.decide_route()

            self.env.process(self.patient_pathway(pat))

            yield self.env.timeout(random.expovariate(1.0 /
                                                G.patient_interarrival_time))

    def patient_pathway(self, patient):

        # Triage by Admissions Co-ordinator
        start_queue_triage = self.env.now

        with self.adm_coordinator.request() as req:
            yield req

            end_queue_triage = self.env.now
            patient.queue_for_triage = end_queue_triage - start_queue_triage

            sampled_triage_duration = random.expovariate(1.0 / 
                                                            G.mean_triage_time)
            yield self.env.timeout(sampled_triage_duration)

            # AMU route


            # SDEC route