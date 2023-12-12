# amu_modelling

Royal Devon University Healthcare NHS Foundation Trust 

Becky Crofts & Kayleigh Haydock 


This is a first draft of a Discrete Event Simulation model using Python to help simulate the acute medical pathway. This involves wards such as the AMU/MAU, Virtual and SDEC wards.

The aim would be to open this model up to any trusts whereby users can unput their own trust setup i.e. parameters such as: Capacity, Triage Coordinators, Ward opening times etc. 

The models aim is to simulate changes to the parameters to see what difference appears to the outcome. 

Released under the MIT license.

If you want to clone this repository, run pip install -r requirements.txt to install the required dependencies.

![Process_Map](https://github.com/BeckyCrofts/amu_modelling/assets/26609637/dd41dcb7-d5bf-466e-8c48-3ff8e21b1fd5)

## Future developments:
- Validate the model by comparing its performance to real-world data
- Refine the model based on validation findings
- Implement utilisation data collection, e.g. bed usage
- Open up more model parameters to user control via Streamlit app
- Further Streamlit development, e.g. allowing the user to compare model runs with different settings within the same Streamlit session
- Add sensitivity analysis for user-entered parameter values
