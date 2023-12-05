import random

# Entity classes

class Patient:
# These entities are the patients going through the triage process and who
# we're collecing data on

    def __init__(self, patient_id):
        self.id = patient_id

        self.store_results = False

        self.amu_patient = False
        self.sdec_patient = False
        self.virtual_patient = False
        # random.uniform produces values in the range [a, b) meaning the
        # possible range includes a exactly, but not b exactly
        # therefore for us our values range from 0 to 0.999...
        # need to consider this when producing our real probabilities
        self.route_probability = random.uniform(0, 1)

        self.start_queue_triage = 0
        self.end_queue_triage = 0
        self.queue_for_triage = 0
        self.triage_queue_timeout = False

        self.start_queue_amu_bed = 0
        self.end_queue_amu_bed = 0
        self.queue_for_amu_bed = 0

        self.start_queue_sdec_slot = 0
        self.end_queue_sdec_slot = 0
        self.queue_for_sdec_slot = 0

        self.start_queue_virtual_slot = 0
        self.end_queue_virtual_slot = 0
        self.queue_for_virtual_slot = 0


class AMU_Patient:
# These entities are patients coming into AMU through other routes
# (e.g. direct from ED, from a Comm Hosp). We're not collecting data on them,
# they're generated just to use some of the AMU bed resource

    def __init__(self, amu_pat_id):
        self.id = amu_pat_id
        self.store_results = False
        self.amu_patient = True