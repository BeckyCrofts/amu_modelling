from datetime import time
import pandas as pd
#import global_params as G

df_routes = pd.DataFrame([
            {'Route name': 'AMU',
                'Capacity': 40, 'LoS': 2160, '247': True},
            {'Route name': 'SDEC',
                'Capacity': 20, 'LoS': 120, '247': False},
            {'Route name': 'Virtual',
                'Capacity': 80, 'LoS': 8640, '247': False}])
df_routes.set_index('Route name', inplace=True)


DICT_DAYS_TO_WEEKDAY = {0: 'Weekday', 1: 'Weekday', 2: 'Weekday',
                            3: 'Weekday', 4: 'Weekday', 5: 'Weekend',
                            6: 'Weekend'}

day_to_sample = 2

weekday_or_weekend = DICT_DAYS_TO_WEEKDAY[2]

# df_sdec_hours = pd.DataFrame([{'Day': 'Weekday', 'Closed': True,
#                                             'Open time': time(0,0),
#                                             'Close time': time(0,0),
#                                             'Number of patients': 1},
#                                 {'Day': 'Weekend', 'Closed': False,
#                                             'Open time': time(0,0),
#                                             'Close time': time(0,0),
#                                             'Number of patients': 0}])
# df_sdec_hours.set_index('Day', inplace=True)

# df_virtual_hours = pd.DataFrame([{'Day': 'Weekday', 'Closed': False,
#                                             'Open time': time(0,0),
#                                             'Close time': time(0,0),
#                                             'Number of patients': 0},
#                                 {'Day': 'Weekend', 'Closed': False,
#                                             'Open time': time(0,0),
#                                             'Close time': time(0,0),
#                                             'Number of patients': 0}])
# df_virtual_hours.set_index('Day', inplace=True)

#dict_df_route_hours = {'SDEC': df_sdec_hours, 'Virtual': df_virtual_hours}

df_all_routes_hours = pd.DataFrame([{'Route': 'SDEC',
                                    'Day': 'Weekday',
                                            'Closed': True,
                                            'Open time': time(0,0),
                                            'Close time': time(0,0),
                                            'Number of patients': 1},
                                {'Route': 'SDEC',
                                    'Day': 'Weekend',
                                            'Closed': False,
                                            'Open time': time(0,0),
                                            'Close time': time(0,0),
                                            'Number of patients': 0},
                                {'Route': 'Virtual',
                                    'Day': 'Weekday',
                                            'Closed': False,
                                            'Open time': time(0,0),
                                            'Close time': time(0,0),
                                            'Number of patients': 0},
                                {'Route': 'Virtual',
                                    'Day': 'Weekend',
                                            'Closed': False,
                                            'Open time': time(0,0),
                                            'Close time': time(0,0),
                                            'Number of patients': 0}])
df_all_routes_hours.set_index(['Route', 'Day'], inplace=True)

mask_not_247 = df_routes['247'] == False
list_not_247_routes = df_routes[mask_not_247].index.to_list()
dict_route_probability = {route: 0 for route in list_not_247_routes}

# print(f"df_routes: \n {df_routes}")
# print(f"\n")
# print(f"df_routes masked: \n {df_routes[mask_not_247]}")
# print(f"\n")
# print(f"list_not_247_routes: \n {list_not_247_routes}")
# print(f"\n")
# print(f"dict_route_probability: \n {dict_route_probability}")
# print(f"\n")


#for route, row in df_route_247.iterrows():
for route in dict_route_probability:
    mask_route_day = ((df_all_routes_hours.index.get_level_values('Route')
                                                                    == route)
                    & (df_all_routes_hours.index.get_level_values('Day')
                                                        == weekday_or_weekend))

    #print(f"{route}: \n {df_all_routes_hours[mask_route_day]} \n")

    #print(f"df_hours_day: \n {df_hours_day}")
    #print(f"row 0: \n {df_all_routes_hours[mask_route_day].iloc[0]}")
    #print(f"row 0, col 0: \n {df_all_routes_hours[mask_route_day].iloc[0, 0]}")
    #print(df_all_routes_hours[mask_route_day].iloc[0, 0].dtype)

    if df_all_routes_hours[mask_route_day].iloc[0, 0] == True:
        dict_route_probability[route] = 0
    elif df_all_routes_hours[mask_route_day].iloc[0, 0] == False:
        dict_route_probability[route] = 1

print(dict_route_probability)




sim_time_1 = 1530 * 60
#sim_time_2 = 2970 * 60
sim_time_3 = 3090 * 60
sim_time_1_in_sec = time.gmtime(sim_time_1)
#sim_time_2_in_sec = time.gmtime(sim_time_2)
sim_time_3_in_sec = time.gmtime(sim_time_3)
#print(f"in secs: {sim_time_1_in_sec}")
#print(f"in secs: {sim_time_2_in_sec}")
#print(f"in secs: {sim_time_3_in_sec}")
#time_1 = time.strftime("%H:%M", sim_time_1_in_sec)
#time_2 = time.strftime("%H:%M", sim_time_2_in_sec)
#time_3 = time.strftime("%H:%M", sim_time_3_in_sec)
#print(f"formatted: {time_1}")
#print(f"formatted: {time_2}")
#print(f"formatted: {time_3}")




# 1530 minutes = 01:30, 2nd day
# 2970 minutes = 01:30, 3rd day
# 3090 minutes = 03:30, 3rd day

import datetime
from datetime import time
import pandas as pd

df_route_hours_example = pd.DataFrame([{'Closed': False,
                                            'Open time': time(2,0),
                                            'Close time': time(17,0),
                                            'Number of patients': 0}])

#print(df_route_hours_example)
#print(df_route_hours_example.iloc[0, 1])

sim_time_1 = 3090
timedelta_1 = datetime.timedelta(minutes=sim_time_1)
time1 = (datetime.datetime.min + timedelta_1).time()

open_time_1 = df_route_hours_example.iloc[0,1]
#print(open_time_1)
close_time_1 = df_route_hours_example.iloc[0,2]
#print(close_time_1)
#open_time_2 = datetime.time(hour=5, minute=0)
#close_time_2 = datetime.time(hour=10, minute=30)

if time1 >= open_time_1 and time1 < close_time_1:
    time_1_in_range_1 = True
else:
    time_1_in_range_1 = False

#if time1 >= open_time_2 and time1 < close_time_2:
#    time_1_in_range_2 = True
#else:
#    time_1_in_range_2 = False

print(f"compare time 1 with o/c times 1: \n"
        f"time 1: {time1} \n open: {open_time_1} \n close: {close_time_1} \n"
        f"result: {time_1_in_range_1} \n")
#print(f"compare time 1 with o/c times 2: \n"
#        f"time 1: {time1} \n open: {open_time_2} \n close: {close_time_2} \n"
#        f"result: {time_1_in_range_2} \n")