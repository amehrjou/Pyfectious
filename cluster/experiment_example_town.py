# Import libs
import os
import sys
import time

# Get the process on the cluster
process = int(str(sys.argv[1]))

number_of_individual_runs = 16
number_of_town_folders = 1

j = process % number_of_individual_runs
process = process // number_of_individual_runs

i = process % number_of_town_folders
process = process // number_of_town_folders

print("--------------------")
print("Cluster Info:")
print("j is:" + str(j))
print("i is:" + str(i))
print("--------------------")

# Run in cluster folder
sys.path.insert(1, os.path.join(os.pardir, 'src'))


# Import and initialize the parser
from json_handle import Parser

experiment_folder = 'cluster_experiment_2'
parser = Parser(folder_name=os.path.join(experiment_folder, 'town_' + str(i)))

# Load Simulator from JSON file
simulator = parser.parse_simulator()

# Time generate model
init_time_generate_model = time.time()

# Generate the simulation model
simulator.generate_model()

time_generate_model = time.time() - init_time_generate_model

# Load Simulator Data from JSON file
end_time, spread_period, initialized_infected_ids, commands, observers = parser.parse_simulator_data()

# Time simulation
init_time_simulation = time.time()

# Run the simulation
simulator.simulate(end_time=end_time,
                   spread_period=spread_period,
                   initialized_infected_ids=initialized_infected_ids,
                   commands=commands,
                   observers=observers,
                   report_statistics=2,
                   database_name=(i, j))

time_simulation = time.time() - init_time_simulation

# Retrieve the plot data
from utils import Health_Condition
statistics_over_time, times = \
    observers[0].get_disease_statistics_during_time(Health_Condition.IS_INFECTED)

# Save as CSV
from cluster_utils import save_lists_csv
save_lists_csv(data_lists=[statistics_over_time, times, [time_simulation], [time_generate_model]],
               list_names=['statistics', 'time', 'simulation_time', 'generation_time'],
               file_name='data_node_' + str(j) + '_task_' + str(i),
               folder_name='data_town_' + str(i))

if i == 0 or i == 34:
    statistics_over_time, times = \
        observers[0].get_disease_statistics_during_time(Health_Condition.DEAD)

    save_lists_csv(data_lists=[statistics_over_time, times],
                   list_names=['statistics', 'time'],
                   file_name='data_node_' + str(j) + '_task_' + str(i),
                   folder_name='mortality_data')
