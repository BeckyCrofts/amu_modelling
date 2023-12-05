import csv
import pandas as pd

from results_calc import Run_Results_Calculator, Trial_Results_Calculator
from acute_med_pathway import AMUModel
from global_params import G



# For the number of runs specified in the g class, create an instance of the
# GP_Surgery_Model class, and call its run method
for run in range(G.simulation_runs):
    print (f"Run {run+1} of {G.simulation_runs}")
    my_model = AMUModel(run,
                        # virtual_capacity = VIRTUAL_CAPACITY,
                        # amu_capacity = AMU_CAPACITY,
                        # sdec_capacity = SDEC_CAPACITY,
                        # adm_coordinator_capacity = ADM_COORDINATOR_CAPACITY,
                        # simulation_runs = SIMULATION_RUNS 
                        )
    my_model.run()
    # do something here to call Run Results Calc
    my_run_results_calc = Run_Results_Calculator()

# Once the trial is complete, we'll create an instance of the
# Trial_Result_Calculator class and run the print_trial_results method
my_trial_results_calculator = Trial_Results_Calculator()
my_trial_results_calculator.print_trial_results()