# Import libs
import os
import pickle
import sys
from functools import partial

# Always run in 'cluster' folder
sys.path.insert(1, os.path.join(os.pardir, 'src'))

from hyperopt import hp
from json_handle import Parser
from optimization import Hyper_Optimization, quarantine_optimization_function

# Get the process on the cluster
MAX_EVAL = 30
process = 0  # int(str(sys.argv[1]))

number_of_individual_runs = 32

j = process % number_of_individual_runs
process = process // number_of_individual_runs

print("--------------------")
print("Cluster Info:")
print("j is: " + str(j))
print("--------------------")

sample_space = {
    'student_restriction_ratio': hp.quniform('trr', 0.1, 0.7, 0.1),
    'worker_restriction_ratio': hp.quniform('wrr', 0.1, 0.7, 0.1)
}

simulator = Parser(folder_name='town_optimization').parse_simulator()
end_time, spread_period, initialized_infected_ids, commands, observers = \
    Parser(folder_name='town_optimization').parse_simulator_data()

simulator.generate_model()
simulator.save_model('town_optimization')

objective_function = partial(quarantine_optimization_function, index=j)

optimizer = Hyper_Optimization(space=sample_space,
                               objective_function=objective_function,
                               max_evaluations=MAX_EVAL)

best, trials = optimizer.optimize()

with open('trials_run_' + str(j) + '.pickle', 'wb') as f:
    pickle.dump(trials, f)

print('\n############## The best choice is ################')
print(best)
