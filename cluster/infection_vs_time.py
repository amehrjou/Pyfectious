# Import libs
import os
import sys

# Get the process on the cluster
process = int(str(sys.argv[1]))

# Run in cluster folder
sys.path.insert(1, os.path.join(os.pardir, 'src'))

# Import and initialize the parser
from json_handle import Parser

parser = Parser(folder_name='town')

# Load Simulator from JSON file
simulator = parser.parse_simulator()

# Generate the simulation model
simulator.generate_model()

# Load Simulator Data from JSON file
end_time, spread_period, initialized_infected_ids, commands, observers = parser.parse_simulator_data()

# Run the simulation
simulator.simulate(end_time=end_time,
                   spread_period=spread_period,
                   initialized_infected_ids=initialized_infected_ids,
                   commands=commands,
                   observers=observers,
                   report_statistics=0)


# Retrieve the plot data
from utils import Health_Condition
statistics_over_time, times = \
    observers[0].get_disease_statistics_during_time(Health_Condition.IS_INFECTED)

# Save as CSV
from cluster_utils import save_lists_csv
save_lists_csv(data_lists=[statistics_over_time, times],
               list_names=['statistics', 'time'],
               file_name='node_data_' + str(process),
               folder_name='data')


