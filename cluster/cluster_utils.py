import json
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict

import hyperopt
import pandas as pd
from dateutil import parser

import sys
sys.path.insert(1, os.path.join(os.pardir, 'src'))

from json_handle import Parser, ComplexEncoder
from logging_settings import logger
from time_handle import Time


def build_experiment_results_data_dict(number_of_experiments: int = 16,
                                       experiment_name_constant_part: str = 'data_town_',
                                       folder_name: str = 'data',
                                       experiment_folder: str or None = 'cluster_experiment_1',
                                       add_time: bool = False) -> Dict[int, List[Dict]]:
    """Build a dictionary containing the experiment folders at the first level and the individual
    executions in the second level.

    Note: The function assumes that the data is either stored in the same path as the
    function's execution path, or in the data folder and in the same path.

    TODO: This function needs a huge refactor afterward.

    Args:
        add_time (bool, optional): Add the times to the dictionary separately if required.
        experiment_folder (str, optional): The folder under json to determine the experiment
        configuration sets. Defaults to 'cluster_experiment_1'.

        number_of_experiments (int, optional): The total number of experiment folders in the data.

        experiment_name_constant_part: The beginning string of experiment result folders. Defaults
        to 'data_town_', e.g., data_town_0.

        folder_name(str, optional) The folder name of the experiments. Defaults to 'data'.
        It's also possible to just copy the data into cluster folder.

    Returns:
        Dict[int, List[Dict]]: The major dictionary containing the results and some specifications
        of all the experiments.
    """
    # Change directory to the data folder (if exists)
    if os.path.exists(folder_name):
        os.chdir(folder_name)

    # Build the grand dictionary of data
    towns_data_dict: Dict[int, List[Dict]] = dict()

    for file_index in range(number_of_experiments):
        folder_name = experiment_name_constant_part + str(file_index)
        logger.info(f'Entering the {folder_name} directory')

        single_town_data_list = list()
        for file_name in os.listdir(folder_name):
            data_dict = dict()

            # TODO: change the following lines later.
            data = read_lists_csv(list_names=['statistics', 'time'],
                                  file_name=file_name,
                                  folder_name=folder_name)
            statistics, times = data

            data_dict['statistics'] = statistics[: len(statistics) - 1]
            data_dict['time'] = convert_time_str_to_datetime(times[: len(times) - 1])

            if add_time:
                data_dict['simulation_time'] = float(times[-1])
                data_dict['generation_time'] = statistics[-1]

            single_town_data_list.append(data_dict)

        towns_data_dict[file_index] = single_town_data_list

    # Move to cluster directory
    if not os.path.exists('data'):
        os.chdir(os.path.join(os.getcwd(), os.pardir))

    # Use parser to complete the dicts
    if experiment_folder is not None:
        for folder_index in towns_data_dict:
            json_parser = Parser(os.path.join(experiment_folder, 'town_' + str(folder_index)))
            simulator = json_parser.parse_simulator()

            population_size = simulator.population_generator.population_size
            immunity_distribution_dict = simulator.disease_properties.immunity_distribution.parameters_dict
            infectious_rate_dict = simulator.disease_properties.infectious_rate_distribution.parameters_dict

            for data_dict in towns_data_dict[folder_index]:
                data_dict['population_size'] = population_size
                data_dict['immunity_distribution_dict'] = immunity_distribution_dict
                data_dict['infectious_rate_dict'] = infectious_rate_dict

    return towns_data_dict


def retrieve_executions_as_dataframe(experiments_data_dict: Dict[int, List[Dict]],
                                     town_index: int,
                                     execution_ids: List[int]) -> pd.DataFrame:
    """Retrieve the statistics and times of certain executions from the towns data dictionary.

    Args:
        experiments_data_dict (Dict[int, List[Dict]]): The main dictionary built to store the
        data from experiments.

        town_index (int): The index of town to retrieve its data.
        execution_ids (List[int]): The list of execution indices to be included in the dataframe.

    Returns:
        Dataframe: The obtained dataframe of statistics with respect to the execution ids.
    """
    infection = dict()
    times = list()

    for i, data_dict in enumerate(experiments_data_dict[town_index]):
        if i in execution_ids:
            if len(data_dict['time']) > len(times):
                times = data_dict['time']

            infection['execution ' + str(i)] = data_dict['statistics']

    infection['time'] = times
    return pd.DataFrame(infection)


def convert_time_str_to_datetime(times: List[str]) -> List[datetime]:
    """Convert an str datetime to datetime object.
    Args:
        times (List[time]): The input data in the string format.

    Returns:
        List[datetime]: The list of converted times in the datetime format.

    """
    if not isinstance(times[0], str):
        logger.critical('Times are not in str format')
    return [parser.parse(time_str) for time_str in times]


def read_lists_csv(list_names: List[str], file_name: str, folder_name: str = 'data') -> List[List]:
    """Read the stored lists from a specific csv file.

    Args:
        list_names (List[str]): Column names to be retrieved.
        file_name (str): Name of the csv file.
        folder_name (str, optional): Name of the folder. Defaults to 'data'.

    Returns:
        List[List]: The lists stored in the file.
    """
    if file_name.endswith('.csv'):
        df = pd.read_csv(os.path.join(folder_name, file_name))
    else:
        df = pd.read_csv(os.path.join(folder_name, file_name + '.csv'))

    try:
        data_lists = list()
        for list_name in list_names:
            data_list = df[list_name].to_list()
            data_lists.append(data_list)

    except KeyError:
        logger.critical(f'The given list name {list_name} not recorded in the file')
    return data_lists


def save_lists_csv(data_lists: List[List], list_names: List[str], file_name: str = 'cluster_data',
                   folder_name: str = 'data'):
    """Save a list as pickle with a specific name in the determined folder.

    Args:
        file_name (str, optional): Name of the CSV file. Defaults to 'cluster_data.csv'.
        data_lists (List[List]): The data needed to be stored.
        list_names (List[str]): Name of the data.
        folder_name (str, optional): Name of the data folder. Defaults to data.
    """

    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass

    maximum_list_len = max([len(data_list) for data_list in data_lists])
    for data_list in data_lists:
        if len(data_list) != maximum_list_len:
            data_list += [None for _ in range(maximum_list_len - len(data_list))]

    csv_data = dict()
    for data_list, list_name in zip(data_lists, list_names):
        csv_data[list_name] = data_list

    df = pd.DataFrame(csv_data, columns=list_names)

    if file_name.endswith('.csv'):
        df.to_csv(os.path.join(folder_name, file_name))
    else:
        df.to_csv(os.path.join(folder_name, file_name + '.csv'))


def parse_optimization_trials_result(folder_name: str = 'trials') -> List[hyperopt.base.Trials]:
    """Extract trial objects from pickle files.

    From the documentation of trials we have that:
        trials.trials - a list of dictionaries representing
        everything about the search.
        trials.results - a list of dictionaries returned by
        'objective' during the search.
        trials.losses() - a list of losses (float for each 'ok' trial)
        trials.statuses() - a list of status strings

    Args:
        folder_name (str, optional): The name of trials folder. Defaults to trials.

    Returns:
        List[hyperopt.base.Trials]: The parsed trial obejects.

    """
    trials_list: List[hyperopt.base.Trials] = list()

    logger.info(f'Entering the {folder_name} directory')

    for file_name in os.listdir(folder_name):
        with open(os.path.join(folder_name, file_name), 'rb') as trial_file:
            trials_list.append(pickle.load(trial_file))

    return trials_list


if __name__ == '__main__':

    # Change a parameter in all settings
    # towns_index_list = range(25)
    # for folder_index in towns_index_list:
    #     json_parser = Parser(os.path.join('cluster_experiment_0', 'town_' + str(folder_index)))
    #     disease_properties = json_parser.parse_disease_properties()
    #
    #     disease_properties.immunity_distribution = \
    #         Immunity_Distribution(parameters_dict={"lower_bound": 0.02, "upper_bound": 0.1})
    #
    #     json_parser.build_json(disease_properties)
    #     json_parser.save_json()

    towns_index_list = range(38)
    for folder_index in towns_index_list:
        json_parser = Parser('cluster_experiment_2/town_' + str(folder_index))
        _, spread_period, initialized_infected_ids, commands, observers = \
            json_parser.parse_simulator_data()

        end_time = Time(delta_time=timedelta(days=300), init_date_time=datetime.now())

        json_parser.json_name = 'Simulator'
        json_parser.build_path()

        with open(json_parser.path, 'r') as f:
            json_dict = json.load(f)

        json_dict["end_time"] = end_time.to_json()

        json_str_main = json.dumps(json_dict, cls=ComplexEncoder,
                                   sort_keys=False, indent=4,
                                   separators=(',', ': '))

        with open(json_parser.path, "w+") as json_file:
            json_file.write(json_str_main)
