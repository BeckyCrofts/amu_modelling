import simpy
import pandas as pd
import csv
import random

from global_params import G
from patient import Patient
from results_calc import Run_Results_Calculator#, Trial_Results_Calculator

# Simulation environment class
class AMUModel:
    def __init__(self, run_number,
                    sim_duration_time,
                    sim_warm_up_time,
                    adm_coordinator_capacity,
                    amu_capacity,
                    sdec_capacity,
                    virtual_capacity,
                    # amu_open_time,
                    sdec_open_time,
                    virtual_open_time,
                    # amu_close_time,
                    sdec_close_time,
                    virtual_close_time):
        
        # Setup the environment
        self.env = simpy.Environment()

        self.resource_data = []
        
        # Setup the values from the default values set
        self.run_number = run_number
        self.sim_duration_time = sim_duration_time
        self.sim_warm_up_time = int((sim_duration_time / 100) *
                                                            sim_warm_up_time)

        self.adm_coordinator_capacity = adm_coordinator_capacity

        self.amu_capacity = amu_capacity
        self.sdec_capacity = sdec_capacity
        self.virtual_capacity = virtual_capacity

        # self.amu_open_time = amu_open_time
        self.sdec_open_time = sdec_open_time
        self.virtual_open_time = virtual_open_time

        # self.amu_close_time = amu_close_time
        self.sdec_close_time = sdec_close_time
        self.virtual_close_time = virtual_close_time

        self.patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env,
                                    capacity = self.adm_coordinator_capacity)
        
        self.amu_bed = simpy.Resource(self.env,capacity = self.amu_capacity)
        
        self.sdec_slot = simpy.Resource(self.env, capacity = self.sdec_capacity)
        
        self.virtual_slot = simpy.Resource(self.env,
                                            capacity = self.virtual_capacity)


        self.run_result_calc = Run_Results_Calculator()

        ############## ^ ^ ###############

        # self.mean_queue_time_triage = 0
        # self.mean_queue_time_amu_bed = 0
        # self.mean_queue_time_sdec_slot = 0
        # self.mean_queue_time_virtual_slot = 0
        
        # initialise the results dataframe for the run
        # this will contain a row per patient with data on their queue times
        # self.results_df = pd.DataFrame()
        # self.results_df["Patient_ID"] = []

        # self.results_df["Start_Q_Triage"] = []
        # self.results_df["End_Q_Triage"] = []
        # self.results_df["Queue_time_triage"] = []

        # self.results_df["Start_Q_AMU"] = []
        # self.results_df["End_Q_AMU"] = []
        # self.results_df["Queue_time_amu_bed"] = []

        # self.results_df["Start_Q_SDEC"] = []
        # self.results_df["End_Q_SDEC"] = []
        # self.results_df["Queue_time_sdec_slot"] = []

        # self.results_df["Start_Q_virtual"] = []
        # self.results_df["End_Q_virtual"] = []
        # self.results_df["Queue_time_virtual_slot"] = []

        # self.results_df.set_index("Patient_ID", inplace=True)

# THIS ISNT WORKING - REPORTS CAPACITY CORRECTLY BUT NOT THE ITEMS THAT WOULD ACTUALLY BE USEFUL
    # def resource_utilisation(self, resource):
    #     while True:
    #         if self.env.now > self.sim_warm_up_time:
    #             item = (self.env.now,
    #                     resource.capacity,
    #                     resource.users,
    #                     resource.count,
    #                     len(resource.queue))
    #             self.resource_data.append(item)
    #             print(item)
    #             yield self.env.timeout(30)
    #         else:
    #             yield self.env.timeout(30)

    def check_day_and_hour(self, current_sim_time):
        
        day_to_sample = G.days_of_week[
                                int((current_sim_time // G.DAY_IN_MINS) % 7)]
        
        hour_to_sample = int((current_sim_time -
                (int(current_sim_time // G.DAY_IN_MINS) * G.DAY_IN_MINS)) // 60)
        
        #return day_to_sample, hour_to_sample
        return hour_to_sample


    def decide_route(self, patient, hour_to_sample, sdec_open_time,
                    virtual_open_time, sdec_close_time, virtual_close_time):
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

        if (hour_to_sample >= sdec_open_time.hour
            and hour_to_sample < sdec_close_time.hour
            and hour_to_sample >= virtual_open_time.hour
            and hour_to_sample < virtual_close_time.hour):

            patient.probability_amu = 0.2
            patient.probability_sdec = 0.4
            patient.probability_virtual = 0.4

        elif (hour_to_sample >= sdec_open_time.hour
            and hour_to_sample < sdec_close_time.hour
            and (hour_to_sample < virtual_open_time.hour
                or hour_to_sample >= virtual_close_time.hour)):

            patient.probability_amu = 0.4
            patient.probability_sdec = 0.6
            patient.probability_virtual = 0

        elif ((hour_to_sample < sdec_open_time.hour
                or hour_to_sample >= sdec_close_time.hour)
            and hour_to_sample >= virtual_open_time.hour
            and hour_to_sample < virtual_close_time.hour):

            patient.probability_amu = 0.6
            patient.probability_sdec = 0
            patient.probability_virtual = 0.4

        else:

            patient.probability_amu = 1
            patient.probability_sdec = 0
            patient.probability_virtual = 0

        if patient.route_probability  < patient.probability_amu:
            patient.amu_patient = True
        elif patient.route_probability >= (1 - patient.probability_virtual):
            patient.virtual_patient = True
        else:
            patient.sdec_patient = True


    # A method that generates patients arriving
    def generate_patients(self):
        # condense all incoming routes into one for now
        # but may need to revisit this
        while True:

            self.patient_counter +=1
            
            # Create a new patient
            # pat = Patient(self.patient_counter, G.probability_amu,
            #                                             G.probability_virtual)
            patient = Patient(self.patient_counter)

            # Get the SimPy environment to run the patient_pathway method 
            # with this patient
            self.env.process(self.patient_pathway(patient))

            # Freeze this function until that time has elapsed
            yield self.env.timeout(random.expovariate(1.0 /
                                                G.patient_interarrival_time))

# DO WE NEED A SECOND GENERATOR JUST CREATING AMU PATIENTS TO REFLECT PTS COMING STRAIGHT FROM ED

    def patient_pathway(self, patient):

# AC PROBABLY NOT 24/7, SO DO WE NEED LOGIC HERE TO JUST SEND PT TO AMU WHEN OUTSIDE OF AC HOURS??

        # only store the queue times for the patient if the run has finished
        # the warm up period
        if self.env.now > self.sim_warm_up_time:
            patient.store_results = True

        # Triage by Admissions Co-ordinator
        patient.start_queue_triage = self.env.now
        #print(f"Patient number {patient.id}: "
        #        f"start queue for triage at {start_queue_triage}")

        # Requesting an Admissions Coordinator and freeze the function until the
        # request for one can be met or the patient has waited too long so
        # defaults to AMU
        with self.adm_coordinator.request() as req:
            yield req | self.env.timeout(G.triage_wait_timeout)

            #print(f"Patient {patient.id} waited {patient.queue_for_triage} "
            #        f"for triage")
            # Record the time the patient finished queuing for the Admissions
            # Coordinator, then calculate the time spent queuing and store with
            # the patient
            patient.end_queue_triage = self.env.now
            #print(f"Patient number {patient.id}: "
            #        f"end queue for triage at {end_queue_triage}")
            patient.queue_for_triage = (patient.end_queue_triage -
                                                patient.start_queue_triage)

            if not req.triggered:
                # send pt straight to AMU
                patient.triage_queue_timeout = True
                patient.amu_patient = True

            else:
                # Randomly sample the time the patient will spend in triage
                # with the Admissions Coordinator  The mean is stored in the g class
                sampled_triage_duration = random.expovariate(1.0 /
                                                            G.mean_triage_time)

                # Freeze this function until that time has elapsed
                yield self.env.timeout(sampled_triage_duration)


        # self.decide_route(patient, *self.check_day_and_hour(self.env.now),
        #                         self.sdec_open_time, self.virtual_open_time,
        #                         self.sdec_close_time, self.virtual_close_time)

        self.decide_route(patient, self.check_day_and_hour(self.env.now),
                        self.sdec_open_time, self.virtual_open_time,
                        self.sdec_close_time, self.virtual_close_time)

        # AMU route
        if patient.amu_patient is True:
            
            patient.start_queue_amu_bed = self.env.now

            #print(f"Patient {patient.id} is waiting for an AMU bed")

            with self.amu_bed.request() as req:
                yield req

            patient.end_queue_amu_bed = self.env.now
            patient.queue_for_amu_bed = (patient.end_queue_amu_bed -
                                                    patient.start_queue_amu_bed)
            #print(f"Patient {patient.id} waited {patient.queue_for_amu_bed} "
            #        "for an AMU bed")

            sampled_amu_stay_time = random.expovariate(1.0
                                                        / G.mean_amu_stay_time)
            yield self.env.timeout(sampled_amu_stay_time)

            print(f"pat {patient.id} in AMU bed for {self.env.now - patient.end_queue_amu_bed}")

        # Virtual ward route
        if patient.virtual_patient is True:

            patient.start_queue_virtual_slot = self.env.now

            #print(f"Patient {patient.id} is waiting for a Virtual ward slot")

            with self.virtual_slot.request() as req:
                yield req

            patient.end_queue_virtual_slot = self.env.now
            patient.queue_for_virtual_slot = (patient.end_queue_virtual_slot -
                                            patient.start_queue_virtual_slot)
            #print(f"Patient {patient.id} waited "
            #        f"{patient.queue_for_virtual_slot} for a Virtual ward slot")

            sampled_virtual_stay_time = random.expovariate(1.0 /
                                                    G.mean_virtual_stay_time)
            yield self.env.timeout(sampled_virtual_stay_time)

        # SDEC route
        if patient.sdec_patient is True:

            patient.start_queue_sdec_slot = self.env.now

            #print(f"Patient {patient.id} is waiting for an SDEC slot")

            with self.sdec_slot.request() as req:
                yield req

            patient.end_queue_sdec_slot = self.env.now
            patient.queue_for_sdec_slot = (patient.end_queue_sdec_slot
                                                - patient.start_queue_sdec_slot)
            #print(f"Patient {patient.id} waited {patient.queue_for_sdec_slot} "
            #        f"for an SDEC slot")

            sampled_sdec_stay_time = random.expovariate(1.0
                                                        / G.mean_sdec_stay_time)
            yield self.env.timeout(sampled_sdec_stay_time)
        

        if patient.store_results is True:
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

        # Store the patient ID and their queuing data in a dataframe
        self.df_to_add = pd.DataFrame({
                        "Patient_ID":[patient.id],
                        "Start_Q_Triage": [patient.start_queue_triage],
                        "End_Q_Triage":[patient.end_queue_triage],
                        "Queue_time_triage": [patient.queue_for_triage],
                        "Triage_queue_timeout": [patient.triage_queue_timeout],
                        "Start_Q_AMU":[patient.start_queue_amu_bed],
                        "End_Q_AMU":[patient.end_queue_amu_bed],
                        "Queue_time_amu":[patient.queue_for_amu_bed],
                        "Start_Q_SDEC":[patient.start_queue_sdec_slot],
                        "End_Q_SDEC":[patient.end_queue_sdec_slot],
                        "Queue_time_sdec":[patient.queue_for_sdec_slot],
                        "Start_Q_virtual":[patient.start_queue_virtual_slot],
                        "End_Q_virtual":[patient.end_queue_virtual_slot],
                        "Queue_time_virtual":[patient.queue_for_virtual_slot]
                                        })
        self.df_to_add.set_index("Patient_ID", inplace=True)

        # Call method to append patient's results to master dataframe for the
        # run
        self.run_result_calc.append_pat_results(self.df_to_add)


    def run(self):
        # Start entity generators
        self.env.process(self.generate_patients())

# see function - this isnt working
        # Log resource utilisation
        # self.env.process(self.resource_utilisation(self.amu_bed))

        # Run simulation
        self.env.run(until=self.sim_duration_time)

        # Calculate run results
        self.run_result_calc.calculate_run_results()
