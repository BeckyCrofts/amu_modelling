import random
import pandas as pd
import simpy


from global_params import G
from patient import Patient, AMU_Patient
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

        self.df_to_add = pd.DataFrame()
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
        self.amu_patient_counter = 0

        self.adm_coordinator = simpy.Resource(self.env,
                                    capacity = self.adm_coordinator_capacity)
        
        self.amu_bed = simpy.Resource(self.env, capacity = self.amu_capacity)
        
        self.sdec_slot = simpy.Resource(self.env, capacity = self.sdec_capacity)
        
        self.virtual_slot = simpy.Resource(self.env,
                                            capacity = self.virtual_capacity)


        self.run_result_calc = Run_Results_Calculator(self.run_number)


    def resource_utilisation(self, resource, name):
        while True:
            if self.env.now > self.sim_warm_up_time:
                item = (self.env.now,
                        name,
                        resource.capacity,
                        resource.users, # list of request events currently using the resource
                        resource.count, # number of users using the resource
                        len(resource.queue)) # queue of pending request events
                self.resource_data.append(item)
                #print(item)
                yield self.env.timeout(10)
            else:
                yield self.env.timeout(10)


    def check_day_and_hour(self, current_sim_time):
        
        #day_to_sample = G.days_of_week[
        #                        int((current_sim_time // G.DAY_IN_MINS) % 7)]
        
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
            patient = Patient(self.patient_counter)

            # Get the SimPy environment to run the patient_pathway method 
            # with this patient
            self.env.process(self.patient_pathway(patient))

            # Freeze this function until that time has elapsed
            yield self.env.timeout(random.expovariate(1.0 /
                                                G.patient_interarrival_time))

    def generate_amu_patients(self):
        while True:

            self.amu_patient_counter +=1

            amu_patient = AMU_Patient(self.amu_patient_counter)

            self.env.process(self.amu_patient(amu_patient))

            yield self.env.timeout(random.expovariate(1.0 /
                                                G.amu_only_interarrival_time))


    def patient_pathway(self, patient):

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

                self.decide_route(patient,
                                self.check_day_and_hour(self.env.now),
                                self.sdec_open_time, self.virtual_open_time,
                                self.sdec_close_time, self.virtual_close_time)


        # AMU route
        if patient.amu_patient is True:
            
            patient.start_queue_amu_bed = self.env.now

            #print(f"Patient {patient.id} is waiting for an AMU bed at {self.env.now}")

            with self.amu_bed.request() as req:
                yield req

                patient.end_queue_amu_bed = self.env.now
                patient.queue_for_amu_bed = (patient.end_queue_amu_bed -
                                                    patient.start_queue_amu_bed)
                #print(f"Patient {patient.id} waited {patient.queue_for_amu_bed} for an AMU bed")

                #print(f"Patient {patient.id} got an AMU bed at {patient.end_queue_amu_bed}")

                sampled_amu_stay_time = random.expovariate(1.0
                                                        / G.mean_amu_stay_time)
                yield self.env.timeout(sampled_amu_stay_time)

                #print(f"Patient {patient.id} in AMU bed for {self.env.now - patient.end_queue_amu_bed}")
                #print(f"Patient {patient.id} left AMU bed at {self.env.now}")


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


# AT SDEC CLOSE TIME ANY REMAINING PTS SHOULD TRANSFER TO AMU
# HOW TO IMPLEMENT THIS?

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


    def amu_patient(self, amu_patient):

        #print(f"amu only pt {amu_patient.id} waiting for bed")

        with self.amu_bed.request() as req:
            yield req

        sampled_amu_stay_time = random.expovariate(1.0
                                                    / G.mean_amu_stay_time)
        yield self.env.timeout(sampled_amu_stay_time)

        #print(f"amu only pt {amu_patient.id} left AMU")


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
                        "Patient ID":[patient.id],
                        #"Triage Queue: Start": [patient.start_queue_triage],
                        #"Triage Queue: End":[patient.end_queue_triage],
                        "Triage Queue Duration": [patient.queue_for_triage],
                        "Triage Queue Timeout": [patient.triage_queue_timeout],
                        #"Start_Q_AMU":[patient.start_queue_amu_bed],
                        #"End_Q_AMU":[patient.end_queue_amu_bed],
                        "AMU/MAU Queue Duration":[patient.queue_for_amu_bed],
                        #"Start_Q_SDEC":[patient.start_queue_sdec_slot],
                        #"End_Q_SDEC":[patient.end_queue_sdec_slot],
                        "SDEC Queue Duration":[patient.queue_for_sdec_slot],
                        #"Start_Q_virtual":[patient.start_queue_virtual_slot],
                        #"End_Q_virtual":[patient.end_queue_virtual_slot],
                        "VW/AHAH Queue Duration":[patient.queue_for_virtual_slot]
                                        })
        self.df_to_add.set_index("Patient ID", inplace=True)

        # Call method to append patient's results to master dataframe for the
        # run
        self.run_result_calc.append_pat_results(self.df_to_add)


    def run(self):
        # Start entity generators
        self.env.process(self.generate_patients())
        self.env.process(self.generate_amu_patients())

        # Log resource utilisation
        self.env.process(self.resource_utilisation(
                                            self.adm_coordinator, "Adm Coord"))
        self.env.process(self.resource_utilisation(self.amu_bed, "AMU bed"))
        self.env.process(self.resource_utilisation(self.sdec_slot, "SDEC slot"))
        self.env.process(self.resource_utilisation(
                                            self.virtual_slot, "Virtual slot"))

        # Run simulation
        self.env.run(until=self.sim_duration_time)

        #deal with this in Streamlit
        # Calculate run results
        #self.run_result_calc.calculate_run_results()
