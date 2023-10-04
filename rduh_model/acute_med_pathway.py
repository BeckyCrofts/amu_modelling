import simpy
import pandas as pd
import csv
import random

from global_params import G
from patient import Patient

# Simulation environment class
class AMUModel:
    def __init__(self, run_number,
                    virtual_capacity,
                    amu_capacity,
                    sdec_capacity,
                    adm_coordinator_capacity,
                    simulation_runs
                ):
        
        # Setup the environment
        self.env = simpy.Environment()
        
        # Setup the values from the default values set
        self.run_number = run_number
        self.virtual_capacity = virtual_capacity
        self.amu_capacity = amu_capacity
        self.sdec_capacity = sdec_capacity
        self.adm_coordinator_capacity = adm_coordinator_capacity
        self.simulation_runs = simulation_runs
        
        ######### WHAT ABOUT THE BELOW?? 
        self.patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env,
                                            capacity = adm_coordinator_capacity)
        
        self.amu_bed = simpy.Resource(self.env,capacity = amu_capacity)
        
        self.sdec_slot = simpy.Resource(self.env, capacity = sdec_capacity)
        
        self.virtual_slot = simpy.Resource(self.env,
                                                capacity = virtual_capacity)
        ############## ^ ^ ###############

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
                                    int((current_sim_time // G.DAY_IN_MINS) % 7)]
        
        hour_to_sample = int((current_sim_time -
                   (int(current_sim_time // G.DAY_IN_MINS) * G.DAY_IN_MINS)) // 60)
        
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


    def decide_route(self, patient, day_to_sample, hour_to_sample):
        # range of probabilities
        # [ | | | | | | | | | ]
        # 0        50        100
        # all other routes closed: P(amu) = 100%
        # [A|A|A|A|A|A|A|A|A|A]
        # if route_prob >= 0 and < P(amu) (1.0) then AMU
        # 0        50        100
        # [A|A|A|A| | | | | |V]
        # 0        50        100
        # if route_prob >= 0 and < P(amu) (0.4) then AMU
        # else if route_prob >= (1 - P(virtual)) (1 - 0.1 = 0.9) then virtual
        # otherwise SDEC

        patient.probability_amu = (G.hourly_route_probabilities['amu']
                                               [day_to_sample][hour_to_sample])
        patient.probability_sdec = (G.hourly_route_probabilities['sdec']
                                                [day_to_sample][hour_to_sample])
        patient.probability_virtual = (G.hourly_route_probabilities['virtual']
                                                [day_to_sample][hour_to_sample])
    
        if patient.route_probability  < patient.probability_amu:
            patient.amu_patient = True
        elif patient.route_probability >= (1 - patient.probability_virtual):
            patient.virtual_patient = True
        else:
            patient.sdec_patient = True


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


        self.decide_route(patient, *self.check_day_and_hour(self.env.now))

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
        if patient.sdec_patient is True:

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