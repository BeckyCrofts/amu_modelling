#import csv
from datetime import datetime, time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_pdf import FigureCanvasPdf
#import plotly as px
#from reportlab.pdfgen.canvas import Canvas
#from reportlab.lib.pagesizes import letter
from reportlab.platypus import Frame, SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageTemplate, PageBreak, NextPageTemplate, BaseDocTemplate
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from io import StringIO, BytesIO
#import tkinter as tk
#from PIL import Image as PILImage, ImageTk


from results_calc import Trial_Results_Calculator
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
                                        help="!!help text here!!",
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
                                help="!!help text here!!",
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
                                    help="!!help text here!!",
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
                                    help="!!help text here!!",
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
        #st.session_state['sdec_open_time'] = time(0,0)
        st.session_state['sdec_open_time'] = G.sdec_open_time
    if 'virtual_open_time' not in st.session_state:
        #st.session_state['virtual_open_time'] = time(0,0)
        st.session_state['virtual_open_time'] = G.virtual_open_time
    if 'amu_close_time' not in st.session_state:
        st.session_state['amu_close_time'] = time(0,0)
    if 'sdec_close_time' not in st.session_state:
        #st.session_state['sdec_close_time'] = time(0,0)
        st.session_state['sdec_close_time'] = G.sdec_close_time
    if 'virtual_close_time' not in st.session_state:
        #st.session_state['virtual_close_time'] = time(0,0)
        st.session_state['virtual_close_time'] = G.virtual_close_time

    with col_amu1:
        st.session_state['amu_capacity'] = st.number_input(
                                                    label="AMU/MAU capacity",
                                                    help="!!help text here!!",
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
                                                    help="!!help text here!!",
                                                    min_value=1,
                                                    value=G.sdec_capacity,
                                                    key='num_sdec_capacity')

    with col_sdec2:
        st.session_state['sdec_open_time'] = st.time_input(
                                                    label="SDEC open time",
                                                    help="!!help text here!!",
                                                    value=G.sdec_open_time,
                                                    step=900,
                                                    key='time_sdec_open')

    with col_sdec3:
        st.session_state['sdec_close_time'] = st.time_input(
                                                    label="SDEC close time",
                                                    help="!!help text here!!",
                                                    value=G.sdec_close_time,
                                                    step=900,
                                                    key='time_sdec_close')

    with col_virt1:
        st.session_state['virtual_capacity'] = st.number_input(
                                                    label="Virtual capacity",
                                                    help="!!help text here!!",
                                                    min_value=1,
                                                    value=G.virtual_capacity,
                                                    key='num_virtual_capacity')

    with col_virt2:
        st.session_state['virtual_open_time'] = st.time_input(
                                                    label="Virtual open time",
                                                    help="!!help text here!!",
                                                    value=G.virtual_open_time,
                                                    step=900,
                                                    key='time_virtual_open')

    with col_virt3:
        st.session_state['virtual_close_time'] = st.time_input(
                                                    label="Virtual close time",
                                                    help="!!help text here!!",
                                                    value=G.virtual_close_time,
                                                    step=900,
                                                    key='time_virtual_close')


# Use main screen to show model output
st.title('RDUH Acute Medical Pathway Simulation')

st.markdown('Please use the sidebar to the left to set up the simulation as '
            'desired and click the \'Run simulation\' button below when done')


if st.button("Run simulation"):

# Spinner appears while model is running
    with st.spinner('Running simulation...'):

        # Create an instance of the Trial_Result_Calculator class
        my_trial_result_calc = Trial_Results_Calculator()

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

            # need to calculate relevant values for the run (ie means) and then
            # call a trial results calc per run method to append these to a
            # trial dataframe

            run_summary_df = my_model.run_result_calc.run_summary_results()
            my_trial_result_calc.append_run_results(run_summary_df)


        #st.dataframe(my_trial_result_calc.trial_results_df)
        #st.dataframe(my_trial_result_calc.trial_results_df.mean())
        #st.dataframe(run_summary_df)



        # my_trial_results_calculator.print_trial_results()
                
        # show results to the screen in a dataframe
        # print (my_trial_results_calculator.trial_results_df)
        #st.dataframe(my_trial_result_calc.trial_results_df.describe())

        st.header("Results")



        def pltfig_to_image(figure):

            buffer = BytesIO()
            figure.savefig(buffer, format='png', dpi=300)
            buffer.seek(0)
            x, y = figure.get_size_inches()
            image = Image(buffer, x * inch, y * inch)

            return image

        def df_to_table(df):

            return Table(
                [[Paragraph(col) for col in df.columns]]  + df.round(0).values.tolist(),
                style=[
                    ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])
                    ])

        def model_params():

            df_params = pd.DataFrame()

            df_params["Time period simulated (in days)"] = [int(st.session_state['sim_duration_time']/G.DAY_IN_MINS)]
            df_params["Simulation warm up time (% of simulation time)"] = [st.session_state['sim_warm_up_time']]
            df_params["Number of Admissions Coordinators / Triage Nurses"] = [st.session_state['adm_coord_capacity']]
            df_params["AMU/MAU capacity"] = [st.session_state['amu_capacity']]
            df_params["SDEC capacity"] = [st.session_state['sdec_capacity']]
            df_params["SDEC open time"] = [st.session_state['sdec_open_time']]
            df_params["SDEC close time"] = [st.session_state['sdec_close_time']]
            df_params["Virtual capacity"] = [st.session_state['virtual_capacity']]
            df_params["Virtual open time"] = [st.session_state['virtual_open_time']]
            df_params["Virtual close time"] = [st.session_state['virtual_close_time']]

            return Table(
                    [[Paragraph(col) for col in df_params.columns]] + df_params.values.tolist(),
                    style=[
                        ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])
                        ])

        def create_results_pdf(dttm, figure, df):
            
            pdf_buffer = BytesIO()

            pdf_doc = SimpleDocTemplate(pdf_buffer)

            styles = getSampleStyleSheet()

# to add:
# page break between sections
# page numbers
            pdf_content = [
                            Paragraph('RDUH Acute Medical Pathway Simulation', styles['Heading1']),
                            Paragraph(f"Simulation Results {dttm}", styles['Heading3']),
                            Paragraph('Queuing Data', styles['Heading2']),
                            pltfig_to_image(figure),
                            df_to_table(df),
                            Paragraph('Utilisation Data', styles['Heading2']),
                            Paragraph('Model Parameters', styles['Heading2']),
                            model_params()
                            ]

            pdf_doc.build(pdf_content)
            
            pdf_buffer.seek(0)

            return pdf_buffer.getvalue()






        describe_df = my_trial_result_calc.trial_results_df.mean()

        plt.style.use('seaborn')
        fig, ax = plt.subplots()

        ax.axhline(y=describe_df["Mean Triage Queue"],
                                        label='Mean Triage Queue')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Mean Triage Queue"], label='Mean Triage Queue')


        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean queue for triage (minutes)')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend()



        dttm_string = datetime.now().strftime("%Y%m%d%H%M%S")
        print_dttm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.download_button(label="Download results (pdf)",
                            data=create_results_pdf(print_dttm, fig, my_trial_result_calc.trial_results_df),
                            file_name=f"sim_results_{dttm_string}",
                            mime="application/pdf")

        #st.dataframe(my_model.run_result_calc.results_df)


        tab_wait, tab_util = st.tabs(["Queues", "Utilisation"])

        with tab_wait:
            st.header("Queues")

            st.dataframe(describe_df.round(0))

            st.pyplot(fig)



        with tab_util:
            st.header("Resource utilisation")

            
