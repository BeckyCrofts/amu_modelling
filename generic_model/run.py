from datetime import time
#import time
import itertools
import csv
import streamlit as st
import pandas as pd
import numpy as np

#from results_calc import Run_Results_Calculator, Trial_Results_Calculator
#from acute_med_pathway import AMUModel
from global_params import G


def validate_route_data():
    # check route names are unique
    # check numerical values within bounds (not <1)
    return


st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title('RDUH Acute Medical Pathway Simulation')

st.markdown('Welcome to the Royal Devon Acute Medical pathway interactive '
            'simulation!')
st.markdown('<- Please check the figures on the left hand side and alter as '
            'desired.')


# Use Streamlit sidebar to collect all the user inputs to the model
with st.sidebar:


    st.header("Simulation setup")

    with st.expander("Click for help"):
        # WRITE HELP TEXT
        st.write("Help text here")

# Set number of simulation runs
    if 'simulation_runs' not in st.session_state:
        st.session_state['simulation_runs'] = G.simulation_runs

    st.session_state['simulation_runs'] = st.number_input(
                                            label="Number of simulation runs",
                                            help="",
                                            min_value=1,
                                            max_value=50,
                                            key='num_sim_runs')
    
# Set time period (in days) for simulation to simulate
    if 'sim_duration_time' not in st.session_state:
        st.session_state['sim_duration_time'] = int(G.sim_duration_time
                                                        /G.DAY_IN_MINS)

# Model needs duration in minutes but day more sensible for users so convert
# all values to days before displaying and convert user input back to minutes
    st.session_state['sim_duration_time'] = int((G.DAY_IN_MINS)*
                            (st.number_input(
                                label="Time period to simulate (in days)",
                                help="",
                                min_value=int(G.WEEK_IN_MINS/G.DAY_IN_MINS),
                                max_value=int((G.WEEK_IN_MINS*52)
                                                /G.DAY_IN_MINS),
                                value=int(G.sim_duration_time/G.DAY_IN_MINS),
                                step=1,
                                key='num_sim_duration')))

# Set proportion of simulation run time to use as a 'warm up'
# Warm up allows the model to be in a realistic state before data starts being
# recorded
    if 'sim_warm_up_time' not in st.session_state:
        st.session_state['sim_warm_up_time'] = G.sim_warm_up_perc

    st.session_state['sim_warm_up_time'] = st.number_input(
                                    label="Simulation warm up time (as "
                                    "percentage of time period to simulate)",
                                    help="",
                                    min_value=5,
                                    max_value=50,
                                    value=G.sim_warm_up_perc,
                                    key='num_sim_warm_up')

# TESTING
    # with st.expander("Testing"):
    #     st.session_state['simulation_runs']
    #     st.session_state['sim_duration_time']
    #     st.session_state['sim_warm_up_time']


    st.header("Incoming patients (pre-triage)")

    with st.expander("Click for help"):
        # WRITE HELP TEXT
        st.write("Help text here")


    if 'df_pats_per_day' not in st.session_state:
                st.session_state['df_pats_per_day'] = pd.DataFrame()

    st.markdown("Average number of patients referred to triage per day")

    st.session_state['df_pats_per_day'] = st.data_editor(
                        data=G.df_blank_pats_per_day,
                        disabled=['Day'],
                        key='data_pat_per_day')
            
# TESTING
    # with st.expander("Testing"):
    #     st.session_state['df_pats_per_day']

# remove confidence/sensitivity questions for now - add back in if have time for
# this later
    # if 'conf_patients_per_day' not in st.session_state:
    #     st.session_state['conf_patients_per_day'] = 0

    # st.session_state['conf_patients_per_day'] = st.radio(
    #                     label="How confident are you about the values above?",
    #                     help="",
    #                     options=(0, 1, 2),
    #                     format_func=lambda x: G.confidence_options.get(x),
    #                     key='radio_conf_pat_per_day')

# think about whether we need this - better to just look at our data and decide
# distribution?
#    vary_patients_within_day = st.radio(
#                        label="Does the number of incoming patients vary "
#                            "significantly over the course of the day?",
#                        help="HELP TEXT HERE",
#                        options=('No', 'Yes'),
#                        index=0,
#                        key='radio_pat_within_day')


    st.header("Triage")

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

    if 'mean_triage_time' not in st.session_state:
        st.session_state['mean_triage_time'] = G.mean_triage_time

    st.session_state['mean_triage_time'] = st.number_input(
                                    label="Average patient triage time in "
                                    "minutes",
                                    help="",
                                    min_value=1,
                                    value=G.mean_triage_time,
                                    key='num_triage_time')

    if 'mean_rejected_referrals' not in st.session_state:
        st.session_state['mean_rejected_referrals'] = G.mean_rejected_referrals

    st.session_state['mean_rejected_referrals'] = st.number_input(
                                    label="Average number of referrals "
                                    "rejected per day",
                                    help="",
                                    min_value=0,
                                    value=G.mean_rejected_referrals,
                                    key='num_reject_refs')

# remove confidence/sensitivity questions for now - add back in if have time for
# this later
    # if 'conf_triage_time' not in st.session_state:
    #     st.session_state['conf_triage_time'] = 0

    # st.session_state['conf_triage_time'] = st.radio(
    #                     label="How confident are you about the value above?",
    #                     help="",
    #                     options=(0, 1, 2),
    #                     format_func=lambda x: G.confidence_options.get(x),
    #                     key='radio_conf_triage_time')

# TESTING
    # with st.expander("Testing"):
    #     st.session_state['adm_coord_capacity']
    #     st.session_state['mean_triage_time']


    st.header("Post-triage")

    with st.expander("Click for help"):
        # WRITE HELP TEXT
        st.write("Help text here")

# Initialise a dataframe to store variables related to each route
# Populate an example row to guide user
    if 'df_routes' not in st.session_state:
        st.session_state['df_routes'] = pd.DataFrame()

# EITHER GIVE USERS WAY TO ENTER LoS IN DAYS/HOURS OR PROVIDE A LITTLE HOURS/
# DAYS TO MINS CALCULATOR WIDGET

    if 'need_route_hours' not in st.session_state:
        st.session_state['need_route_hours'] = []

    with st.form(key='form_routes'):

        st.markdown("Create routes")

        with st.expander("See explanation"):
                st.write("\n- Route names must be unique"
                    "\n- Route capacity is the number of patients that route can "
                        "handle at once"
                    "\n- Route LoS is the mean length of stay in minutes of a "
                        "patient within the route")

# Let user input route data using Streamlit data editor widget
        df_routes = st.data_editor(
                        data=G.df_routes_example,
                        column_config={
                            '247': st.column_config.CheckboxColumn(
                                'Open 24/7?', default=False)},
                        num_rows="dynamic",
                        key='data_routes')

        submit_routes = st.form_submit_button('Submit')
        if submit_routes:
            #DO SOMETHING HERE TO CALL validate_route_data FUNCTION AND ONLY
            #PROCEED IF PASSES
            
            #NEED TO ADD A LINE TO THIS DF FOR THE 'REJECT REFERRAL ROUTE' - SEE
            #G.create_df_reject_route FUNCTION
            #DONT WANT USERS TO EDIT THIS ROW, HENCE NOT IN THIS DF, BUT NEED TO
            #HAVE AS A POSSIBLE TRIAGE OUTCOME

            st.session_state['df_routes'] = df_routes
            st.session_state['need_route_hours'] = df_routes.index[
                                            df_routes['247'] == False].tolist()

# TESTING
    # with st.expander("Routes testing"):
    #     st.dataframe(st.session_state['df_routes'])
    #     st.session_state['need_route_hours']


    if len(st.session_state['need_route_hours']) > 0:

        with st.form(key='form_route_hours'):

            st.markdown("Route opening hours")

            with st.expander("See explanation"):
                # WRITE HELP TEXT
                st.write("Help text here")

            if 'dict_df_route_hours' not in st.session_state:
                st.session_state['dict_df_route_hours'] = {}
            if 'df_mi_all_routes_hours' not in st.session_state:
                st.session_state['df_mi_all_routes_hours'] = {}

            dict_df_all_routes_hours = {}
            dict_all_routes_hours_blank = {}

            for route in st.session_state['need_route_hours']:
# Initialise a template dataframe for each route in dictionary to display
# later in Streamlit data editors
                dict_all_routes_hours_blank[route] = pd.DataFrame(
                                                    G.df_route_hours_example,
                                                    index=['Weekday',
                                                            'Weekend'])
                dict_all_routes_hours_blank[route].index.name = 'Day'
# Initialise placeholder dictionary to temporarily hold user-entered data until
# they click Submit button and commit data to session state
                dict_df_all_routes_hours[route] = pd.DataFrame()

# OPEN/CLOSED VALUES NaN RATHER THAN False BY DEFAULT - WHERE USER NEVER TOGGLES
# VALUE DF IS LEFT WITH NaN
# NEED TO MAKE THIS False BY DEFAULT OR FIND WAY TO OVERWRITE
            for route in dict_all_routes_hours_blank:
                st.markdown(f"{route} open days/hours")
                dict_df_all_routes_hours[route] = st.data_editor(
                        data=dict_all_routes_hours_blank[route],
                        column_config={
                            'Closed': st.column_config.CheckboxColumn(
                                'Closed all day?', width='small',
                                default=False),
                            'Open time': st.column_config.TimeColumn(
                                'Open time', width='small',
                                format='HH:mm', step=1),
                            'Close time': st.column_config.TimeColumn(
                                'Close time', width='small',
                                format='HH:mm', step=1)},
                        disabled=['Day'],
                        key=f"data_{route}_route_hours")

            submit_hours = st.form_submit_button('Submit')
            if submit_hours:
                st.session_state[
                            'dict_df_route_hours'] = dict_df_all_routes_hours

            #AGAIN NEED TO ADD AN ENTRY FOR THE 'REJECT REFERRAL ROUTE' WITH THE
            #NUMBER OF PATIENTS VALUE COLLECTED EARLIER AND OTHER VALUES
            #DEFAULTED IN

#TESTING
        # with st.expander("Route hours testing"):
        #     G.df_route_hours_example
        #     st.session_state['dict_df_route_hours']
        #     dict_df_all_routes_hours
        #     dict_all_routes_hours_blank

        #     print("G.df_route_hours_example:")
        #     print(G.df_route_hours_example)
        #     print("st.session_state['dict_df_route_hours']")
        #     print(st.session_state['dict_df_route_hours'])
        #     print("dict_df_all_routes_hours")
        #     print(dict_df_all_routes_hours)
        #     print("dict_all_routes_hours_blank")
        #     print(dict_all_routes_hours_blank)
        



    with st.form(key='form_route_crossover'):

        st.markdown("Route crossover")

        list_route_names = st.session_state['df_routes'].index.tolist()

# Create a list of tuples for each route pairing, e.g.
# With list: routes = [a, b, c]
# produce a list of tuples like:
#   tuples = [(a,b), (a,c), (b,a), (b,c), (c,a), (c,b)]
# Use this to ask user for number of patients for each crossover possibility
        list_crossover_tuples = list(
                                    itertools.permutations(list_route_names, 2))

        if 'dict_crossover_rates' not in st.session_state:
                st.session_state['dict_crossover_rates'] = {}
        dict_crossover_rates = {}

        for pair in list_crossover_tuples:
            dict_crossover_rates[pair] = st.number_input(
                                        label=f"Patients moving from {pair[0]} "
                                            f"to {pair[1]} per day "
                                            f"(0 if doesn't happen)",
                                        value=0,
                                        min_value=0,
                                        key=f"num_{pair}_crossover_rate")

        submit_crossover = st.form_submit_button('Submit')
        if submit_crossover:
            st.session_state['dict_crossover_rates'] = dict_crossover_rates

# TESTING
#     with st.expander("Route crossover testing"):
#         list_crossover_tuples
# # print these to console as Streamlit can't render a dict with a tuple as key
#     print(dict_crossover_rates)
#     print(st.session_state['dict_crossover_rates'])




# REUSE CODE BELOW TO LET USER DOWNLOAD CURRENT SETTINGS OR BYPASS SET UP BY
# UPLOADING A PREVIOUS SAVE

    # def dict_to_df_csv(dict):
    # # DF CREATION HERE TO MOVE TO FUNCTION ABOVE
    #     df = pd.DataFrame.from_dict({
    #                 (day,hour): G.hourly_route_probabilities[day][hour]
    #                     for day in G.hourly_route_probabilities.keys()
    #                     for hour in G.hourly_route_probabilities[day].keys()},
    #                     orient="index")
    #     return df.to_csv().encode('utf-8')

    # st.download_button(label="Download example file (CSV)",
    #                     data=dict_to_df_csv(G.hourly_route_probabilities),
    #                     file_name="example_route_probabilites.csv",
    #                     mime="text/csv")

    # with st.expander("See explanation"):
    #     # WRITE HELP TEXT
    #     st.write("Help text here")

    # # Allow user to upload a csv of route probabilities
    # uploaded_file = st.file_uploader(label="Upload route probabilities file",
    #                                     label_visibility="collapsed")

    # # Read data from csv into a dataframe and display
    # if uploaded_file is not None:
    #     df_user_route_probabilities = pd.read_csv(uploaded_file,
    #                                                 index_col=[0,1])
    #     st.write(df_user_route_probabilities)




if st.button("Start simulation"):

    with st.spinner("Running simulation"):

        # convert the dictionary of dataframes into a multiindex dataframe where
        # the dictionary key becomes the first index
        # Streamlit's data editor widget can't use multiindex so this can't be
        # done until we're sure the user is finished with data entry, i.e when
        # they click the start simulation button
        df_all_routes_hours = pd.concat(st.session_state['dict_df_route_hours'])
        df_all_routes_hours.index.names = ['Route', 'Day']

        # for run in range(st.session_state['simulation_runs']):

            # my_model = AMUModel(run,
            #                     st.session_state['sim_duration_time'],
            #                     st.session_state['sim_warm_up_time'],
            #                     st.session_state['df_pats_per_day'],
            #                     st.session_state['adm_coord_capacity'],
            #                     st.session_state['mean_triage_time'],
            #                     st.session_state['df_routes'],
            #                     df_all_routes_hours,
            #                     st.session_state['dict_crossover_rates'])

