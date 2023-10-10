import pandas as pd

class Run_Results_Calculator:

    # self.mean_queue_time_triage = 0
    # self.mean_queue_time_amu_bed = 0
    # self.mean_queue_time_sdec_slot = 0
    # self.mean_queue_time_virtual_slot = 0
    
    def __init__(self):
        # initialise the results dataframe for the run
        # this will contain a row per patient with data on their queue times
        self.results_df = pd.DataFrame()
        self.results_df["Patient_ID"] = []
        self.results_df.set_index("Patient_ID", inplace=True)

        self.results_df["Start_Q_Triage"] = []
        self.results_df["End_Q_Triage"] = []
        self.results_df["Queue_time_triage"] = []

        self.results_df["Start_Q_AMU"] = []
        self.results_df["End_Q_AMU"] = []
        self.results_df["Queue_time_amu"] = []

        self.results_df["Start_Q_SDEC"] = []
        self.results_df["End_Q_SDEC"] = []
        self.results_df["Queue_time_sdec"] = []

        self.results_df["Start_Q_virtual"] = []
        self.results_df["End_Q_virtual"] = []
        self.results_df["Queue_time_virtual"] = []



    def append_pat_results(self, df_to_add):

        self.results_df = pd.concat([self.results_df, df_to_add])



    def calculate_run_results(self):

        #csv_path = '/home/rebecca/HSMA/project/amu_modelling/rduh_model/'
        csv_path = 'run_results.csv'

        self.results_df.to_csv("run_results.csv")



 # A method that calculates the average queuing time for Triage
    def calculate_mean_q_time_triage(self):
        self.mean_queue_time_triage = (
                                    self.results_df["Queue_time_triage"].mean())


    # A method to write run results to file.  Here, we write the run number
    # against the the calculated mean queuing time for the AC across
    # patients in the run.  Again, we can call this at the end of each run
    def write_run_results(self, run_number):

        run_results_filename = f"results_run_{run_number}.csv"

        # Create a file to store trial results, and write the column headers
        with open(run_results_filename, "w") as f:
            writer = csv.writer(f, delimiter=",")
            column_headers = ["run", "mean_queue_time_triage"]
            writer.writerow(column_headers)

        with open("trial_results.csv", "a") as f:
            writer = csv.writer(f, delimiter=",")
            results_to_write = [self.run_number,
                                self.mean_queue_time_triage]
            writer.writerow(results_to_write)


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