import pandas as pd
import csv

class Run_Results_Calculator:
   
    def __init__(self, run_number):
        self.run_number = run_number

        # initialise the results dataframe for the run
        # this will contain a row per patient
        self.results_df = pd.DataFrame()

        self.results_df["Patient ID"] = []
        self.results_df.set_index("Patient ID", inplace=True)

        self.results_df["Triage Queue Duration"] = []
        self.results_df["Triage Queue Timeout"] = []

        self.results_df["AMU/MAU Queue Duration"] = []

        self.results_df["SDEC Queue Duration"] = []

        self.results_df["VW/AHAH Queue Duration"] = []


        # initialise the summary results dataframe for the run
        # this will contain aggregated data across the run
        self.summary_results_df = pd.DataFrame()
        
        self.summary_results_df["Run Number"] = self.run_number
        self.summary_results_df.set_index("Run Number", inplace=True)

        self.summary_results_df["Mean Triage Queue"] = []
        self.summary_results_df["Count Triage Timeout"] = []

        self.summary_results_df["Mean AMU/MAU Queue"] = []

        self.summary_results_df["Mean SDEC Queue"] = []

        self.summary_results_df["Mean VW/AHAH Queue"] = []

        print(self.summary_results_df)


    def append_pat_results(self, df_to_add):

        self.results_df = pd.concat([self.results_df, df_to_add])


# take run's results_df and produce a summary df
# mean of duration columns, sum of timeout column
    def run_summary_results(self):

        self.summary_results_df["Mean Triage Queue"] = [self.results_df[
                                            "Triage Queue Duration"].mean()]
        self.summary_results_df["Count Triage Timeout"] = [self.results_df[
                                            "Triage Queue Timeout"].sum()]

        self.summary_results_df["Mean AMU/MAU Queue"] = [self.results_df[
                                            "AMU/MAU Queue Duration"].mean()]

        self.summary_results_df["Mean SDEC Queue"] = [self.results_df[
                                            "SDEC Queue Duration"].mean()]

        self.summary_results_df["Mean VW/AHAH Queue"] = [self.results_df[
                                            "VW/AHAH Queue Duration"].mean()]
        
        return self.summary_results_df


    def run_results_to_csv(self):

        self.results_df.to_csv(f"run_{self.run_number + 1}_results.csv")

# Hopefully don't need this kind of function - just calculate in Streamlit run.py
 # A method that calculates the average queuing time for Triage
#    def calculate_mean_q_time_triage(self):
#        self.mean_queue_time_triage = (
#                                    self.results_df["Queue_time_triage"].mean())

#        return self.mean_queue_time_triage



# Class to store, calculate and manipulate trial results in a Pandas DataFrame
class Trial_Results_Calculator:
    # The constructor creates a new Pandas DataFrame, and stores this as an
    # attribute of the class instance
    def __init__(self):
        self.trial_results_df = pd.DataFrame()
        self.trial_results_df["Run Number"] = []
        self.trial_results_df.set_index("Run Number", inplace=True)

        self.trial_results_df["Mean Triage Queue"] = []
        self.trial_results_df["Count Triage Timeout"] = []

        self.trial_results_df["Mean AMU/MAU Queue"] = []

        self.trial_results_df["Mean SDEC Queue"] = []

        self.trial_results_df["Mean VW/AHAH Queue"] = []

        
    def append_run_results(self, df_to_add):

        self.trial_results_df = pd.concat([self.trial_results_df, df_to_add])

# df 
#   run no  |   tr q mean   |   amu q mean  |   sdec q mean |   vw q mean















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