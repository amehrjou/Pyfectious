from datetime import timedelta, datetime
from typing import Dict, Tuple

from hyperopt import tpe, STATUS_OK, fmin, Trials
from hyperopt.pyll import Apply

from commands import Restrict_Certain_Roles
from conditions import Time_Point_Condition
from json_handle import Parser
from logging_settings import logger
from time_handle import Time
from utils import Health_Condition


def quarantine_optimization_function(params, index: int = 0):
    """A sample objective function to quarantine certain roles.

    Args:
        index (int): The index of the running object, if applicable on cluster.
        params (Dict): The set of input parameters dictionary.
    """
    simulator = Parser(folder_name='town_optimization').parse_simulator()
    end_time, spread_period, initialized_infected_ids, commands, observers = \
        Parser(folder_name='town_optimization').parse_simulator_data()

    simulator.load_model('town_optimization')

    commands.clear()
    quarantine_effective_day = 2

    condition_student = Time_Point_Condition(deadline=Time(timedelta(days=quarantine_effective_day)))
    condition_worker = Time_Point_Condition(deadline=Time(timedelta(days=quarantine_effective_day)))
    condition_customer = Time_Point_Condition(deadline=Time(timedelta(days=quarantine_effective_day)))

    commands.append(Restrict_Certain_Roles(condition=condition_student,
                                           role_name='Student',
                                           restriction_ratio=params['student_restriction_ratio']))

    commands.append(Restrict_Certain_Roles(condition=condition_worker,
                                           role_name='Worker',
                                           restriction_ratio=params['worker_restriction_ratio']))

    commands.append(Restrict_Certain_Roles(condition=condition_customer,
                                           role_name='Customer',
                                           restriction_ratio=1.4 - params['worker_restriction_ratio'] - params['student_restriction_ratio']))

    logger.info(f'Restriction ratios are {[(command.role_name, command.restriction_ratio) for command in commands]}')
    logger.info(f'Quarantine starts at day {quarantine_effective_day}')

    simulator.simulate(end_time=Time(delta_time=timedelta(days=20),
                                     init_date_time=datetime.now()),
                       spread_period=spread_period,
                       initialized_infected_ids=initialized_infected_ids,
                       commands=commands,
                       observers=observers,
                       report_statistics=1)

    stats, times = observers[0].get_disease_statistics_during_time(Health_Condition.IS_INFECTED)

    loss = max(stats)
    optimization_index = loss
    logger.info(f'Peak height is {loss}, and parameters are {params}')

    from cluster_utils import save_lists_csv
    save_lists_csv(data_lists=[stats, times],
                   list_names=['statistics', 'time'],
                   file_name='data_node_' + str(index) + '_' + str(optimization_index),
                   folder_name='data_optimization')

    return {'loss': loss, 'params': params, 'status': STATUS_OK}


class Hyper_Optimization:
    """Optimize hyper-parameters of an objective function.

    This class benefits from the hyperopt library to optimize a set of hyper=parameters
    over a given space, using bayesian optimization.

    Attributes:
        objective_function (Function, optional): The objective function to be optimized.
        Defaults to None, may be set afterward.

        space (Dict[str, Apply], optional): The optimization space for the optimizer.
        Defaults to None, may be set afterward.

        algorithm (Function, optional): The algorithm of optimization. Defaults
        to tpe.suggest.

        max_evaluations(int, optional): Maximum times of evaluation.
    """

    def __init__(self, space: Dict[str, Apply] = None, objective_function=None,
                 algorithm=tpe.suggest, max_evaluations: int = 20):
        """Initialize a hyper optimizer object.

        Args:
            objective_function (Function, optional): The objective function to be optimized.
            Defaults to None, may be set afterward.

            space (Dict[str, Apply], optional): The optimization space for the optimizer.
            Defaults to None, may be set afterward.

            algorithm (Function, optional): The algorithm of optimization. Defaults
            to tpe.suggest.

            max_evaluations(int, optional): Maximum times of evaluation.
        """
        self.objective_function = None
        if objective_function is not None:
            self.set_objective_function(objective_function)

        self.algorithm = algorithm
        self.max_evaluations = max_evaluations

        self.space = dict()
        if space is not None:
            self.space = space

    def optimize(self) -> Tuple[dict, Trials]:
        """Optimize the objective based on the space and algorithm.

        Returns:
            Dict, Trials: The optimization results.
        """
        trials = Trials()
        best = fmin(self.objective_function, self.space, algo=self.algorithm,
                    max_evals=self.max_evaluations, trials=trials, show_progressbar=False)
        return best, trials

    def set_objective_function(self, objective_function):
        """Set a new objective function.
        Args:
            objective_function (Function): The new objective function.
        """
        self.objective_function = objective_function

    def add_parameter(self, name: str, apply: Apply):
        """Add a new parameter to the space.

        Args:
            name (str): The name of the parameter.
            apply (Apply): The distribution of the parameter.
        """
        self.space[name] = apply
