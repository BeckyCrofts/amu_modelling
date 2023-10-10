import csv
import streamlit as st
import pandas as pd
from datetime import time
import matplotlib.pyplot as plt
import plotly.express as px

#from results_calc import Run_Results_Calculator, Trial_Results_Calculator
from acute_med_pathway import AMUModel
from global_params import G


# Page config - this has to be the first Streamlit command in the script
st.set_page_config(layout='wide', initial_sidebar_state='expanded')


# Use Streamlit sidebar to collect all the user inputs to the model
with st.sidebar:

    st.header("Simulation setup")

    with st.expander("Click for help"):
        # WRITE HELP TEXT
        st.write("Help text here")

# Set number of simulation runs
    if 'simulation_runs' not in st.session_state:
        st.session_state['simulation_runs'] = G.simulation_runs

    st.session_state['simulation_runs'] = st.slider(
                                        label="Number of simulation runs",
                                        help="",
                                        min_value=1,
                                        max_value=50,
                                        key='slid_sim_runs')

    # Number input rather than slider
    # st.session_state['simulation_runs'] = st.number_input(
    #                                     label="Number of simulation runs",
    #                                     help="",
    #                                     min_value=1,
    #                                     max_value=50,
    #                                     key='num_sim_runs')

# Set time period (in days) for simulation to simulate
    if 'sim_duration_time' not in st.session_state:
        st.session_state['sim_duration_time'] = int(G.sim_duration_time
                                                        /G.DAY_IN_MINS)

# Model needs duration in minutes but day more sensible for users so convert
# all values to days before displaying and convert user input back to minutes
    st.session_state['sim_duration_time'] = int((G.DAY_IN_MINS)*
                            (st.slider(
                                label="Time period to simulate (in days)",
                                help="",
                                min_value=int(G.WEEK_IN_MINS/G.DAY_IN_MINS),
                                max_value=int((G.WEEK_IN_MINS*52)
                                                /G.DAY_IN_MINS),
                                value=int(G.sim_duration_time/G.DAY_IN_MINS),
                                step=1,
                                key='slid_sim_duration')))

    # Number input rather than slider
    # st.session_state['sim_duration_time'] = int((G.DAY_IN_MINS)*
    #                         (st.number_input(
    #                             label="Time period to simulate (in days)",
    #                             help="",
    #                             min_value=int(G.WEEK_IN_MINS/G.DAY_IN_MINS),
    #                             max_value=int((G.WEEK_IN_MINS*52)
    #                                             /G.DAY_IN_MINS),
    #                             value=int(G.sim_duration_time/G.DAY_IN_MINS),
    #                             step=1,
    #                             key='num_sim_duration')))

# Set proportion of simulation run time to use as a 'warm up'
# Warm up allows the model to be in a realistic state before data starts being
# recorded
    if 'sim_warm_up_time' not in st.session_state:
        st.session_state['sim_warm_up_time'] = G.sim_warm_up_perc

    st.session_state['sim_warm_up_time'] = st.slider(
                                    label="Simulation warm up time (as "
                                    "percentage of time period to simulate)",
                                    help="",
                                    min_value=5,
                                    max_value=50,
                                    value=G.sim_warm_up_perc,
                                    key='slid_sim_warm_up')

    # Number input rather than slider
    # st.session_state['sim_warm_up_time'] = st.number_input(
    #                                 label="Simulation warm up time (as "
    #                                 "percentage of time period to simulate)",
    #                                 help="",
    #                                 min_value=5,
    #                                 max_value=50,
    #                                 value=G.sim_warm_up_perc,
    #                                 key='num_sim_warm_up')

    #TESTING
    # with st.expander("Testing"):
    #     st.session_state['simulation_runs']
    #     st.session_state['sim_duration_time']
    #     st.session_state['sim_warm_up_time']

    st.divider()

    st.header("Model parameters")

    with st.expander("Click for help"):
        # WRITE HELP TEXT
        st.write("Help text here")

    if 'adm_coord_capacity' not in st.session_state:
        st.session_state['adm_coord_capacity'] = G.adm_coordinator_capacity

    st.session_state['adm_coord_capacity'] = st.number_input(
                                    label="Number of Admissions Coordinators / "
                                    "Triage Nurses",
                                    help="",
                                    min_value=1,
                                    value=G.adm_coordinator_capacity,
                                    key='num_adm_coord')


    col_amu1, col_amu2, col_amu3 = st.columns(3)
    col_sdec1, col_sdec2, col_sdec3 = st.columns(3)
    col_virt1, col_virt2, col_virt3 = st.columns(3)

    if 'amu_capacity' not in st.session_state:
        st.session_state['amu_capacity'] = G.amu_capacity
    if 'sdec_capacity' not in st.session_state:
        st.session_state['sdec_capacity'] = G.sdec_capacity
    if 'virtual_capacity' not in st.session_state:
        st.session_state['virtual_capacity'] = G.virtual_capacity
    if 'amu_open_time' not in st.session_state:
        st.session_state['amu_open_time'] = time(0,0)
    if 'sdec_open_time' not in st.session_state:
        st.session_state['sdec_open_time'] = time(0,0)
    if 'virtual_open_time' not in st.session_state:
        st.session_state['virtual_open_time'] = time(0,0)
    if 'amu_close_time' not in st.session_state:
        st.session_state['amu_close_time'] = time(0,0)
    if 'sdec_close_time' not in st.session_state:
        st.session_state['sdec_close_time'] = time(0,0)
    if 'virtual_close_time' not in st.session_state:
        st.session_state['virtual_close_time'] = time(0,0)

    with col_amu1:
        st.session_state['amu_capacity'] = st.number_input(
                                                    label="AMU/MAU capacity",
                                                    help="",
                                                    min_value=1,
                                                    value=G.amu_capacity,
                                                    key='num_amu_capacity')

    # with col_amu2:
    #     st.session_state['amu_open_time'] = st.time_input(
    #                                                 label="AMU/MAU open time",
    #                                                 help="",
    #                                                 value=time(0,0),
    #                                                 key='time_amu_open')
    
    # with col_amu3:
    #     st.session_state['amu_close_time'] = st.time_input(
    #                                                 label="AMU/MAU close time",
    #                                                 help="",
    #                                                 value=time(0,0),
    #                                                 key='time_amu_close')


    with col_sdec1:
        st.session_state['sdec_capacity'] = st.number_input(
                                                    label="SDEC capacity",
                                                    help="",
                                                    min_value=1,
                                                    value=G.sdec_capacity,
                                                    key='num_sdec_capacity')

    with col_sdec2:
        st.session_state['sdec_open_time'] = st.time_input(
                                                    label="SDEC open time",
                                                    help="",
                                                    value=time(0,0),
                                                    step=3600,
                                                    key='time_sdec_open')

    with col_sdec3:
        st.session_state['sdec_close_time'] = st.time_input(
                                                    label="SDEC close time",
                                                    help="",
                                                    value=time(0,0),
                                                    step=3600,
                                                    key='time_sdec_close')

    with col_virt1:
        st.session_state['virtual_capacity'] = st.number_input(
                                                    label="Virtual capacity",
                                                    help="",
                                                    min_value=1,
                                                    value=G.virtual_capacity,
                                                    key='num_virtual_capacity')

    with col_virt2:
        st.session_state['virtual_open_time'] = st.time_input(
                                                    label="Virtual open time",
                                                    help="",
                                                    value=time(0,0),
                                                    step=3600,
                                                    key='time_virtual_open')

    with col_virt3:
        st.session_state['virtual_close_time'] = st.time_input(
                                                    label="Virtual close time",
                                                    help="",
                                                    value=time(0,0),
                                                    step=3600,
                                                    key='time_virtual_close')















# Use main screen to show model output
st.title('RDUH Acute Medical Pathway Simulation')

st.markdown('Please use the sidebar to the left to set up the simulation as '
            'desired and click the \'Run simulation\' button below when done')


if st.button("Run simulation"):

# Spinner appears while model is running
    with st.spinner('Running simulation...'):

# MOVE THIS TO RESULTS CALC?

        # Create a file to store trial results, and write the column headers
        # 7
        # with open("trial_results.csv", "w") as f:
        #     writer = csv.writer(f, delimiter=",")
        #     column_headers = ["Run", "mean_queue_time_triage"]
        #     writer.writerow(column_headers)

        # For the number of runs specified by the user, create an instance of
        # the AMUModel class, and call its run method
        for run in range(st.session_state['simulation_runs']):
            my_model = AMUModel(run,
                                st.session_state['sim_duration_time'],
                                st.session_state['sim_warm_up_time'],
                                st.session_state['adm_coord_capacity'],
                                st.session_state['amu_capacity'],
                                st.session_state['sdec_capacity'],
                                st.session_state['virtual_capacity'],
                                # st.session_state['amu_open_time'],
                                st.session_state['sdec_open_time'],
                                st.session_state['virtual_open_time'],
                                # st.session_state['amu_close_time'],
                                st.session_state['sdec_close_time'],
                                st.session_state['virtual_close_time'])
            my_model.run()

        # Once the trial is complete, we'll create an instance of the
        # Trial_Result_Calculator class and run the print_trial_results method
        # 8
        # my_trial_results_calculator = Trial_Results_Calculator()
        # my_trial_results_calculator.print_trial_results()
                
        st.success('Simulation complete')
        # show results to the screen in a dataframe
        # print (my_trial_results_calculator.trial_results_df)
        # st.dataframe(my_trial_results_calculator.trial_results_df.describe())

        fig, ax = plt.subplots()
        my_model.run_result_calc.results_df["Queue_time_triage"].plot(kind='bar', x='Name', ax=ax)

        st.pyplot(fig)