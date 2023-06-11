#Phil Debenham
#Hi Becky, this is code I used to generate variable hourly mean-interarrival times.  Which might help with you switching the flow off your sim at specific times.

# Add ths code to the g class
# Patient Arrivals (Hourly changes to Lambda coded here)
# Nested dictionary representing 3 patient flows into the DES (medical, surgical and review_in_ed)
# Each dictionary key represents an hour of the day, and associated variable represents the lambda (mean inter-arrival time for that hour)
    cdu_inter_arrivals = {
        'medical': {0: 72.974496, 1: 80.131789, 2: 97.061471, 3: 92.826982, 4: 93.443594, 5: 116.140372, 6: 125.434685, 7: 125.037574,
                    8: 165.250441, 9: 146.386538, 10: 114.015293, 11: 61.76585, 12: 35.539062, 13: 30.124357, 14: 32.594214,
                    15: 36.212983, 16: 37.342835, 17: 36.150941, 18: 32.303221, 19: 31.647321, 20: 33.089948,
                    21: 42.862079, 22: 54.813498, 23: 67.928859
                    },
        'surgical': {0: 193.13, 1: 221.9, 2: 252.2, 3: 275.7, 4: 356.8, 5: 311.6, 6: 432.4, 7: 410.7,
                     8: 370.2, 9: 405.2, 10: 347.7, 11: 297.6, 12: 268.0, 13: 238.4, 14: 176.4,
                     15: 149.3, 16: 145.1, 17: 169.5, 18: 147.4, 19: 169.0, 20: 173.8,
                     21: 145.1, 22: 168.0, 23: 200.7
                     },
        'review_in_ed': {0: 237.6, 1: 280.6, 2: 225.5, 3: 260.7, 4: 296.4, 5: 257.3, 6: 343.0, 7: 371.2,
                         8: 420.1, 9: 369.2, 10: 335.1, 11: 400.7, 12: 324.3, 13: 277.9, 14: 252.9,
                         15: 233.6, 16: 202.5, 17: 197.9, 18: 177.3, 19: 168.6, 20: 230.7,
                         21: 258.8, 22: 232.4, 23: 178.6
                         }}
# Add the following code to your model Class
# A method that converts sim time into hour of day for sampling from inter-arrival dictionaries
# Assumes sim time is in minutes
# I have used a 48 hour sim duration, so the else statement adjust for this. If you are simulating more than 48 hours, this will require adjustment
    def check_hour_of_day(self, current_sim_time):
        if current_sim_time < 1440:
            hour_to_sample = int(current_sim_time // 60)
        else:
            hour_to_sample = int((current_sim_time - 1440) // 60)
        return hour_to_sample
# Add this into your patient generators
 # example generator (arrival_route parsed by run method)
 def generate_cdu_arrivals(self, arrival_route):
            sampled_interval = random.expovariate(
                1.0 / g.cdu_inter_arrivals[arrival_route][self.check_hour_of_day(self.env.now)])
            # Freeze this function until the time has elapsed
            yield self.env.timeout(sampled_interval)
# snippet of run method to demonstrate how to generate 3 patient flows through the sim
 def run(self):
        # Start entity generators
        self.env.process(self.generate_cdu_arrivals('medical'))
        self.env.process(self.generate_cdu_arrivals('surgical'))
        self.env.process(self.generate_ed_referrals_to_see_in_ed('review_in_ed'))