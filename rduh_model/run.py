#import csv
from datetime import datetime, time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageTemplate, PageBreak, NextPageTemplate, BaseDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from PIL import Image as PILImage


from results_calc import Trial_Results_Calculator
from acute_med_pathway import AMUModel
from global_params import G


# Page config - this has to be the first Streamlit command in the script
st.set_page_config(layout='wide', initial_sidebar_state='expanded')


# Use Streamlit sidebar to collect all the user inputs to the model
with st.sidebar:

    st.header("Simulation setup")

    with st.expander("Click for help"):
        st.write("- **Number of simulation runs:** Select the number of times the simulation should repeat. The results will show the average values across all of these repeats. \n "
                 "- **Time period to simulate:** Select how long each run of the simulation should go on for. \n "
                 "- **Simulation warm up time:** This allows patients to populate the model before data starts being recorded. Please leave as default if unsure.")

# Set number of simulation runs
    if 'simulation_runs' not in st.session_state:
        st.session_state['simulation_runs'] = G.simulation_runs

    st.session_state['simulation_runs'] = st.slider(
                                        label="Number of simulation runs",
                                        help="!!help text here!!",
                                        min_value=5,
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
                                    min_value=10,
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

#    with st.expander("Click for help"):
#        st.write("")

    col_but_east, col_but_north = st.columns(2)
# placeholders - need to write functions to populate relevent default values
    with col_but_east:
        st.button(label="Eastern defaults")
    with col_but_north:
        st.button(label="Northern defaults")

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
trust_logo = PILImage.open('rduh_model/images/trust_logo.png')
diagram = PILImage.open('rduh_model/images/diagram.png')

col_blank0, col_blank1, col_logo = st.columns(3)

with col_logo:
    st.image(trust_logo, width=200)

st.title('Acute Medical Pathway Simulation')

st.markdown(':warning: Please note this model is **under development** and is currently '
            '**not validated** for real world use.')

col_explanation, col_diagram = st.columns([0.3, 0.7])

with col_explanation:
    st.markdown('''This simulation allows the user to model the performance of
                the incoming acute medical pathway. Users can customise
                certain parameters to test their effect on performance. 
                Results will appear on the screen when the simulation has
                completed and will be available to download as a PDF.''')

with col_diagram:
    st.image(diagram, width=600)


st.markdown('Please use the sidebar to the left to set up the simulation as '
            'desired and click the \'Run simulation\' button below when done')


if st.button("Run simulation", type="primary"):

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
                [[Paragraph(col) for col in df.columns]]  + df.values.astype(int).tolist(),
                style=[
                    ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])
                    ])


        def sim_setup():

            df_setup = pd.DataFrame()

            df_setup["Time period simulated (in days)"] = [int(st.session_state['sim_duration_time']/G.DAY_IN_MINS)]
            df_setup["Simulation warm up time (% of simulation time)"] = [st.session_state['sim_warm_up_time']]

            return Table(
                        [[Paragraph(col) for col in df_setup.columns]] + df_setup.values.tolist(),
                        style=[
                            ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 1, colors.black),
                            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])
                            ])


        def model_params():

            df_params = pd.DataFrame()

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


        def on_page(canvas, pdf_doc, pagesize=A4):
            page_num = canvas.getPageNumber()
            canvas.drawCentredString(pagesize[0]/2, 50, str(page_num))


        def create_results_pdf(dttm, figure_triage_queue, figure_triage_timeout,
                                figure_amu_mau_queue, figure_sdec_timeout,
                                figure_vw_ahah_timeout, df):

            padding = dict(
                            leftPadding=72, 
                            rightPadding=72,
                            topPadding=72,
                            bottomPadding=18)

            portrait_frame = Frame(0, 0, *A4, **padding)

            portrait_template = PageTemplate(
                                            id='portrait',
                                            frames=portrait_frame,
                                            onPage=on_page,
                                            pagesize=A4)

            pdf_buffer = BytesIO()

            pdf_doc = BaseDocTemplate(pdf_buffer,
                                        pageTemplates=portrait_template)

            styles = getSampleStyleSheet()

            pdf_content = [
                            Paragraph('RDUH Acute Medical Pathway Simulation', styles['Heading1']),
                            Paragraph(f"Simulation Results {dttm}", styles['Heading3']),
                            Paragraph('Simulation Setup & Model Parameters', styles['Heading2']),
                            sim_setup(),
                            model_params(),
                            PageBreak(),
                            Paragraph('Queuing Data', styles['Heading2']),
                            df_to_table(df),
                            pltfig_to_image(figure_triage_queue),
                            pltfig_to_image(figure_triage_timeout),
                            PageBreak(),
                            pltfig_to_image(figure_amu_mau_queue),
                            pltfig_to_image(figure_sdec_timeout),
                            pltfig_to_image(figure_vw_ahah_timeout),
                            PageBreak(),
                            Paragraph('Utilisation Data', styles['Heading2'])
                            ]

            pdf_doc.build(pdf_content)
            
            pdf_buffer.seek(0)

            return pdf_buffer.getvalue()




        trial_queue_df = my_trial_result_calc.trial_results_df.mean().round(0).to_frame().T
        describe_df = my_trial_result_calc.trial_results_df.mean()


        #  This is the graph for: Mean queue
        plt.style.use('seaborn')
        fig_triage_queue, ax = plt.subplots()
        plt.title("Triage Queues", fontweight="bold")

        ax.axhline(y=describe_df["Mean Triage Queue"],
                                        label='Overall mean queue for triage')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Mean Triage Queue"], label='Mean queue for triage (per run)', alpha=0.4)
        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean queue for triage (minutes)')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend(frameon=True, loc='lower right')


        # This is the graph for: Triage Timeouts
        plt.style.use('seaborn')
        fig_triage_timeout, ax = plt.subplots()
        plt.title("Triage Timeouts", fontweight="bold")

        ax.axhline(y=describe_df["Count Triage Timeout"],
                                        label='Overall mean triage timeouts')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Count Triage Timeout"], label='Mean triage timeouts (per run)', alpha=0.4)
        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean number of triage timeouts')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend(frameon=True, loc='lower right')


        # This is the graph for: AMU
        plt.style.use('seaborn')
        fig_amu_queue, ax = plt.subplots()
        plt.title("AMU/MAU Queues", fontweight="bold")

        ax.axhline(y=describe_df["Mean AMU/MAU Queue"],
                                        label='Overall mean queue for AMU/MAU admission')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Mean AMU/MAU Queue"], label='Mean queue for AMU/MAU admission (per run)', alpha=0.4)
        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean number of triage timeouts')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend(frameon=True, loc='lower right')


        # This is the graph for: SDEC
        plt.style.use('seaborn')
        fig_sdec_queue, ax = plt.subplots()
        plt.title("SDEC Queues", fontweight="bold")

        ax.axhline(y=describe_df["Mean SDEC Queue"],
                                        label='Overall mean queue for SDEC admission')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Mean SDEC Queue"], label='Mean queue for SDEC admission (per run)', alpha=0.4)
        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean queue for SDEC (minutes)')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend(frameon=True, loc='lower right')


        # This is the graph for: Virtual
        plt.style.use('seaborn')
        fig_vw_ahah_queue, ax = plt.subplots()
        plt.title("Virtual Queues", fontweight="bold")

        ax.axhline(y=describe_df["Mean VW/AHAH Queue"],
                                        label='Overall mean queue for VW/AHAH admission')
        ax.bar(my_trial_result_calc.trial_results_df.index,
            my_trial_result_calc.trial_results_df["Mean VW/AHAH Queue"], label='Mean queue for Virtual admission (per run)', alpha=0.4)
        ax.set_xlabel('Simulation run')
        ax.set_ylabel('Mean queue for Virtual (minutes)')
        # Go up in steps of 25 on the x axis so it's not all
        # clumped together
        ax.set_xticks(my_trial_result_calc.trial_results_df.index)
        ax.legend(frameon=True, loc='lower right')



        

        dttm_string = datetime.now().strftime("%Y%m%d%H%M%S")
        print_dttm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.download_button(label="Download results (pdf)",
                            data=create_results_pdf(print_dttm, fig_triage_queue, fig_triage_timeout, fig_amu_queue, fig_sdec_queue, fig_vw_ahah_queue, trial_queue_df),
                            #data=create_results_pdf(print_dttm, fig_triage_queue, fig_triage_timeout, my_trial_result_calc.trial_results_df),
                            file_name=f"sim_results_{dttm_string}",
                            mime="application/pdf")

        #st.dataframe(my_model.run_result_calc.results_df)


        tab_wait, tab_util = st.tabs(["Queues", "Utilisation"])

        with tab_wait:
            st.header("Queues")

            #st.markdown('The results below show the mean values across all runs of the simulation')

#RENAME THESE VALUES, EG COUNT TRIAGE TIMEOUT IS A MEAN BY THIS POINT
            with st.expander("Click for column definitions"):
                    st.markdown("- **Mean Triage Queue:** An average of all patients waiting for triage across all runs of the simulation. \n"
                                "- **Count Triage Timeout:** A count of patients who were admitted to the acute medical ward by default after reaching a timeout threshold waiting for triage. This value is averaged across all simulation runs. \n"
                                "- **Mean AMU/MAU Queue:** An average of all patients waiting for admission to the acute medical ward across all runs of the simulation. \n"
                                "- **Mean SDEC Queue:** An average of all patients waiting to access the same day emergency care service across all runs of the simulation. \n"
                                "- **Mean VW/AHAH Queue:** An average of all patients waiting for admission to the virtual ward/acute hospital at home across all runs of the simulation."
                            )


            #st.dataframe(my_trial_result_calc.trial_results_df)


            st.dataframe(trial_queue_df, hide_index=True)


            st.subheader("Charts")

            col_graph1, col_graph2 = st.columns(2)

            with col_graph1:
                st.pyplot(fig_triage_queue)
                st.pyplot(fig_amu_queue)
                st.pyplot(fig_vw_ahah_queue)

            
            with col_graph2:
                st.pyplot(fig_triage_timeout)
                st.pyplot(fig_sdec_queue)
            
            #st.divider()



        with tab_util:
            st.header("Resource utilisation")

            
