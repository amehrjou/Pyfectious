import json
import os
from os.path import basename
from typing import List, Dict

from commands import Quarantine_Single_Community, Unquarantine_Single_Community, \
    Quarantine_Single_Person, Unquarantine_Single_Person, \
    Quarantine_Multiple_People, Unquarantine_Multiple_People, \
    Quarantine_Diseased_People, Restrict_Certain_Roles, Nope, Quarantine_All_People, Unquarantine_All_People, \
    Unquarantine_Diseased_People, Quarantine_Diseased_People_Noisy, Quarantine_Community_Type, \
    Unquarantine_Community_Type

from conditions import Time_Point_Condition, Time_Period_Condition, \
    Statistical_Family_Condition, Statistical_Ratio_Condition, \
    Statistical_Ratio_Role_Condition

from disease_manipulator import Disease_Properties
from distance import Distance
from distributions import Distribution

from observer import Observer
from population_generator import Community_Type, Community_Type_Role, Community, Person, Family
from population_generator import Population_Generator, Family_Pattern, Sub_Community_Type
from time_handle import Time
from time_simulator import Simulator
from utils import Operator, Health_Condition


class Parser:
    """A class to encode/decode complex objects to JSON.

    This class can be used in order to convert a complex object that has implemented a to_json method,
    into a json file. Conversely, the stored json files can also be parsed from the data/json folder,
    located in the project main directory.

    Attributes
    ----------
    json_string (str): The json string built by build_json function is stored in this container.
    path (str): Path to target json file.
    json_name (str): Name of the target json file.
    folder_name (str, optional): Name of the folder to store json files. Defaults to 'example'.

    """

    def __init__(self, folder_name: str = 'test'):
        """Initialize Parser object using folder name.

        Args:
            folder_name (str, optional): Folder name indicates the folder name to categorize
            the JSON files. Defaults to 'example'.
        """
        self.folder_name: str = folder_name
        self.json_name: str = ""
        self.json_string: str = ""
        self.json_dict: str = ""
        self.path: str = ""

    def build_json(self, obj):
        """Build a json string for an object.

        Args:
            obj (object): The object to be converted into JSON format.
        """
        self.json_string = json.dumps(obj, cls=ComplexEncoder,
                                      sort_keys=False, indent=4,
                                      separators=(',', ': '))
        self.json_name = obj.__class__.__name__

    def save_json(self):
        """This saves the json_string variable into a file named after the class name

        The class name is obtained using the object name attribute.
        """
        self.build_path()

        with open(self.path, "w+") as json_file:
            json_file.write(self.json_string)

    def parse_simulator_data(self):
        """This reads the simulator data the folder in which it is located.

        Returns:
            Time, Time, List[int], List[Command], List[Observer]: This is almost everything we need to
            run the simulate function. The function simulate, inside the simulator class uses this data
            to operate.
        """
        self.json_name = 'Simulator'
        self.build_path()

        # load json file
        with open(self.path, 'r') as f:
            self.json_dict = json.load(f)

        # retrieve main attributes dictionaries
        end_time = self.parse_time(self.json_dict['end_time'])
        spread_period = self.parse_time(self.json_dict['spread_period'])
        initialized_infected_ids = self.json_dict['initialized_infected_ids']
        commands = self.parse_commands(self.json_dict['commands'])
        observers = self.parse_observers(self.json_dict['observers'])

        return end_time, spread_period, initialized_infected_ids, commands, observers

    def parse_simulator(self) -> Simulator:
        """Parse the simulator object by parsing both population generator and disease properties.

        Returns:
            Simulator: The simulator object. Note that the simulator.generate function is
            not called here.
        """
        return Simulator(self.parse_population_generator(), self.parse_disease_properties())

    def parse_observers(self, observers_list: List) -> List:
        """Parse the observers from the observers list, extracted from a JSON dictionary.

        Args:
            observers_list (List): List of the observers, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Observer]: A list containing the observer objects.
        """
        observers = list()

        for observer_dict in observers_list:
            observer = self.parse_observer(observer_dict)
            observers.append(observer)

        return observers

    def parse_observer(self, observer_dict: Dict) -> Observer:
        """Parse a single observer object from JSON dictionary.

        Args:
            observer_dict (Dict): JSON dictionary containing the observer info.

        Returns:
            Observer: The actual observer class.
        """
        # parse observer fields
        condition = self.parse_condition(observer_dict['condition'])
        observe_people = observer_dict['observe_people']
        observe_families = observer_dict['observe_families']
        observe_communities = observer_dict['observe_communities']

        return Observer(condition, observe_people, observe_families, observe_communities)

    def parse_commands(self, commands_list: List) -> List:
        """Parse the commands from the commands list, extracted from a JSON dictionary.

        Args:
            commands_list (List): List of the commands, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Command]: A list containing the command objects.
        """
        commands = list()

        for command_dict in commands_list:
            command = self.parse_command(command_dict)
            commands.append(command)

        return commands

    def parse_command(self, command_dict: Dict):
        """Parse a single command object from JSON dictionary.

        Important: whenever a new command is added to the src, this function needs
        to change accordingly. Otherwise, the command cannot be parsed properly and
        will be treated as a Nope command.

        Args:
            command_dict (Dict): JSON dictionary containing the command info.

        Returns:
            Command: The actual command class.
        """
        name = command_dict['name']

        if name == Quarantine_Single_Community.__name__:
            condition = self.parse_condition(command_dict['condition'])
            community_type_name = command_dict['community_type_name']
            community_index = command_dict['community_index']

            return Quarantine_Single_Community(condition, community_type_name, community_index)

        if name == Unquarantine_Single_Community.__name__:
            condition = self.parse_condition(command_dict['condition'])
            community_type_name = command_dict['community_type_name']
            community_index = command_dict['community_index']

            return Unquarantine_Single_Community(condition, community_type_name, community_index)

        if name == Quarantine_Community_Type.__name__:
            condition = self.parse_condition(command_dict['condition'])
            community_type_name = command_dict['community_type_name']

            return Quarantine_Community_Type(condition, community_type_name)

        if name == Unquarantine_Community_Type.__name__:
            condition = self.parse_condition(command_dict['condition'])
            community_type_name = command_dict['community_type_name']

            return Unquarantine_Community_Type(condition, community_type_name)

        if name == Quarantine_Single_Person.__name__:
            condition = self.parse_condition(command_dict['condition'])
            id = command_dict['id']

            return Quarantine_Single_Person(condition, id)

        if name == Unquarantine_Single_Person.__name__:
            condition = self.parse_condition(command_dict['condition'])
            id = command_dict['id']

            return Unquarantine_Single_Person(condition, id)

        if name == Quarantine_Multiple_People.__name__:
            condition = self.parse_condition(command_dict['condition'])
            ids = command_dict['ids']

            return Unquarantine_Single_Person(condition, ids)

        if name == Unquarantine_Multiple_People.__name__:
            condition = self.parse_condition(command_dict['condition'])
            ids = command_dict['ids']

            return Unquarantine_Single_Person(condition, ids)

        if name == Quarantine_Diseased_People_Noisy.__name__:
            condition = self.parse_condition(command_dict['condition'])
            probability = float(command_dict['probability'])
            return Quarantine_Diseased_People_Noisy(condition, probability)

        if name == Quarantine_Diseased_People.__name__:
            condition = self.parse_condition(command_dict['condition'])

            return Quarantine_Diseased_People(condition)

        if name == Unquarantine_Diseased_People.__name__:
            condition = self.parse_condition(command_dict['condition'])

            return Unquarantine_Diseased_People(condition)

        if name == Quarantine_All_People.__name__:
            condition = self.parse_condition(command_dict['condition'])

            return Quarantine_All_People(condition)

        if name == Unquarantine_All_People.__name__:
            condition = self.parse_condition(command_dict['condition'])

            return Unquarantine_All_People(condition)

        if name == Restrict_Certain_Roles.__name__:
            condition = self.parse_condition(command_dict['condition'])
            role_name = command_dict['role_name']
            restriction_ratio = command_dict['restriction_ratio']

            return Restrict_Certain_Roles(condition, role_name, restriction_ratio)

        # If none of the above, then it is a Nope command
        return Nope()

    def parse_condition(self, condition_dict: Dict):
        """Parse a single condition object from JSON dictionary.

        Important: whenever a new command is added to the src, this function needs
        to change accordingly. Otherwise, the condition cannot be parsed properly.

        Args:
            condition_dict (Dict): JSON dictionary containing the condition info.

        Returns:
            Condition: The actual condition class.
        """
        name = condition_dict['name']

        if name == Time_Point_Condition.__name__:
            deadline = self.parse_time(condition_dict['deadline'])

            return Time_Point_Condition(deadline)

        if name == Time_Period_Condition.__name__:
            period = self.parse_time(condition_dict['period'])

            return Time_Period_Condition(period)

        if name == Statistical_Ratio_Condition.__name__:
            dividend = Health_Condition(condition_dict['dividend']['value'])
            divisor = Health_Condition(condition_dict['divisor']['value'])
            comparison_type = Operator(condition_dict['comparison_type']['value'])
            target_ratio = condition_dict['target_ratio']
            max_satisfaction = condition_dict['max_satisfaction']

            return Statistical_Ratio_Condition(dividend, divisor, target_ratio, comparison_type, max_satisfaction)

        if name == Statistical_Ratio_Role_Condition.__name__:
            dividend = Health_Condition(condition_dict['dividend']['value'])
            divisor = Health_Condition(condition_dict['divisor']['value'])
            comparison_type = Operator(condition_dict['comparison_type']['value'])
            role_name = condition_dict['role_name']
            target_ratio = condition_dict['target_ratio']
            max_satisfaction = condition_dict['max_satisfaction']

            return Statistical_Ratio_Role_Condition(dividend, divisor, target_ratio, comparison_type, role_name,
                                                    max_satisfaction)

        if name == Statistical_Family_Condition.__name__:
            stat_type = Health_Condition(condition_dict['stat_type']['value'])
            target_ratio = condition_dict['target_ratio']
            comparison_type = Operator(condition_dict['comparison_type']['value'])
            max_satisfaction = condition_dict['max_satisfaction']

            return Statistical_Family_Condition(stat_type, target_ratio, comparison_type, max_satisfaction)

    def parse_people(self, people_list):
        """Parse the people from the people list, extracted from a JSON dictionary.

        Args:
            people_list (List): List of the persons, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Person]: A people list containing the person objects.
        """
        # retrieve people
        people = list()

        for person_dict in people_list:
            person = self.parse_person(person_dict)
            people.append(person)

        return people

    def parse_person(self, person_dict: Dict) -> Person:
        """Parse a single person object from JSON dictionary.

        Args:
            person_dict (Dict): JSON dictionary containing the person info.

        Returns:
            Person: The actual person class.
        """
        # parse main attributes of the object
        id_number = person_dict['id_number']
        age = person_dict['age']
        health_condition = person_dict['health_condition']
        gender = person_dict['gender']
        family = self.parse_family(person_dict['family'])

        return Person(id_number, age, health_condition, gender, family)

    def parse_family(self, family_dict: Dict) -> Family:
        """Parse a single family object from JSON dictionary.

        Args:
            family_dict (Dict): JSON dictionary containing the family info.

        Returns:
            Family: The actual family class.
        """
        id_number = family_dict['id_number']
        people_ids = family_dict['people_ids']
        family_pattern = self.parse_family_pattern(family_dict['family_pattern'])

        return Family(id_number, people_ids, family_pattern)

    def parse_communities(self, communities_list) -> List:
        """Parse the communities from the communities list, extracted from a JSON dictionary.

        Args:
            communities_list (List): List of the communities, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Community]: A list containing the community objects.
        """
        # retrieve community types
        communities = list()

        for community_dict in communities_list:
            community = self.parse_community(community_dict)
            communities.append(community)

        return communities

    def parse_community(self, community_dict: Dict) -> Community:
        """Parse a single community object from JSON dictionary.

        Args:
            community_dict (Dict): JSON dictionary containing the community info.

        Returns:
            Community: The actual community class.
        """
        # retrieve main object fields
        id_number = community_dict['id_number']
        community_type = self.parse_community_type(community_dict['community_type'])
        people_ids_dict = community_dict['people_ids_dict']
        intracommunity_setting_dict = community_dict['intracommunity_setting_dict']
        intercommunity_connectivity_dict = community_dict['intercommunity_connectivity_dict']
        location = tuple(community_dict['location'])

        return Community(id_number, community_type, people_ids_dict, intracommunity_setting_dict,
                         intercommunity_connectivity_dict, location)

    def parse_time(self, time_dict) -> Time:
        """Parse a Time object from time_dict JSON dictionary.

        Args:
            time_dict (Dict): The JSON dictionary containing the time object info.

        Returns:
            Time: The parsed Time object.
        """
        unix_time = time_dict['unix_time']
        minutes = time_dict['minutes']

        initial_date_time = Time.convert_unix_to_datetime(unix_time - minutes * 60)
        delta_time = Time.convert_unix_to_datetime(unix_time) - initial_date_time

        return Time(delta_time, initial_date_time)

    def parse_disease_properties(self) -> Disease_Properties:
        """Parse the disease properties object from the Disease_Properties.json file.

        Returns:
            Disease_Properties: The disease properties object containing the disease information.
        """
        self.json_name = 'Disease_Properties'
        self.build_path()

        # load json file
        with open(self.path, 'r') as f:
            self.json_dict = json.load(f)

        # retrieve main attributes dictionaries
        infectious_rate_distribution = self.parse_distribution(self.json_dict['infectious_rate_distribution'])
        immunity_distribution = self.parse_distribution(self.json_dict['immunity_distribution'])
        disease_period_distribution = self.parse_distribution(self.json_dict['disease_period_distribution'])
        death_probability_distribution = self.parse_distribution(self.json_dict['death_probability_distribution'])
        incubation_period_distribution = self.parse_distribution(self.json_dict['incubation_period_distribution'])

        # hospitalization
        hospitalization_probability_distribution = None
        if 'hospitalization_probability_distribution' in self.json_dict.keys():
            hospitalization_probability_distribution = self.parse_distribution(self.json_dict['hospitalization_probability_distribution'])

        # build the object
        disease_properties = Disease_Properties(infectious_rate_distribution,
                                                immunity_distribution,
                                                disease_period_distribution,
                                                death_probability_distribution,
                                                incubation_period_distribution,
                                                hospitalization_probability_distribution)
        return disease_properties

    def parse_population_generator(self) -> Population_Generator:
        """Parse the population generator object from the Population_Generator.json file.

        Returns:
            Population_Generator: The population generator object containing the population information.
        """
        self.json_name = 'Population_Generator'
        self.build_path()

        # load json file
        with open(self.path, 'r') as f:
            self.json_dict = json.load(f)

        # retrieve main attributes dictionaries
        population_size = self.json_dict['population_size']
        family_patterns = self.parse_family_patterns(self.json_dict['family_patterns'])
        community_types = self.parse_community_types(self.json_dict['community_types'])
        distance_function = Distance.map_str_to_function(self.json_dict['distance_function'])

        # build the object
        population_generator = Population_Generator(population_size, family_patterns, community_types,
                                                    distance_function)
        return population_generator

    def parse_family_patterns(self, family_patterns_dict) -> Dict:
        """Parse the family pattern probability JSON dictionary.

        Args:
            family_patterns_dict (Dict): The family pattern probability dictionary in JSON dictionary
            format.

        Returns:
            Dict: The family pattern probability dictionary object, containing all the information
            required to realize the families.
        """
        # retrieve family patterns
        family_patterns = dict()
        for p in family_patterns_dict:
            family_pattern_dict = family_patterns_dict[p]
            family_pattern = self.parse_family_pattern(family_pattern_dict)

            # add family pattern to family patterns dictionary
            family_patterns[family_pattern] = p

        return family_patterns

    def parse_family_pattern(self, family_pattern_dict: Dict) -> Family_Pattern:
        """Parse the family pattern object from the respective JSON dictionary.

        Args:
            family_pattern_dict (Dict): The JSON dictionary containing the information about
            a family pattern.

        Returns:
            Family_Pattern: The actual family pattern object.
        """
        # parse attributes of family pattern
        number_of_members = family_pattern_dict['number_of_members']
        age_distributions = self.parse_distributions(family_pattern_dict['age_distributions'])
        health_condition_distributions = self.parse_distributions(family_pattern_dict['health_condition_distributions'])
        genders = family_pattern_dict['genders']
        location_distribution = self.parse_distribution(family_pattern_dict['location_distribution'])

        return Family_Pattern(number_of_members, age_distributions, health_condition_distributions,
                              genders, location_distribution)

    def parse_community_types(self, community_types_list) -> List[Community_Type]:
        """Parse the community types from the community types list, extracted from a JSON dictionary.

        Args:
            community_types_list (List): List of the community types, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Community_Type]: A list containing the community type objects.
        """
        # retrieve community types
        community_types = list()

        for community_type_dict in community_types_list:
            community_type = self.parse_community_type(community_type_dict)
            community_types.append(community_type)

        return community_types

    def parse_community_type(self, community_type_dict):
        """Parse a single community type object a JSON dictionary.

        Args:
            community_type_dict (Dict): The JSON dictionary containing the community type
            information.

        Returns:
            Community_Type: The actual community type object.
        """
        # parse the object fields
        sub_community_types = self.parse_sub_community_types(community_type_dict['sub_community_types'])
        name = community_type_dict['community_name']
        number_of_communities = community_type_dict['number_of_communities']
        sub_community_connectivity_dict = \
            self.parse_sub_community_connectivity_dict(community_type_dict['sub_community_connectivity_dict'])
        location_distribution = self.parse_distribution(community_type_dict['location_distribution'])
        transmission_potential_dict = \
            self.parse_transmission_potential_dict(community_type_dict['transmission_potential_dict'])

        return Community_Type(sub_community_types, name, number_of_communities,
                              sub_community_connectivity_dict, location_distribution,
                              transmission_potential_dict)

    def parse_transmission_potential_dict(self, transmission_potential_dict_dict):
        """Parse the transmission potential connectivity dict from a JSON dictionary.

        Args:
            transmission_potential_dict_dict (Dict): The JSON dictionary of the transmission
            potential dictionary. Do not get confused by _dict_dict, the first dict refers to
            the object being a dictionary, and the second refers to the parsed JSON dictionary.

        Returns:
            Dict: The actual transmission potential dictionary object.
        """
        transmission_potential_dict: Dict[int, Dict[int, Distribution]] = dict()

        # parse the json dict object of transmission_potential_dict
        for key in transmission_potential_dict_dict:
            inner_dict: Dict[int, Distribution] = dict()

            for inner_key in transmission_potential_dict_dict[key]:
                inner_dict[int(inner_key)] = self.parse_distribution(transmission_potential_dict_dict[key][inner_key])

            transmission_potential_dict[int(key)] = inner_dict

        return transmission_potential_dict

    def parse_sub_community_connectivity_dict(self, sub_community_connectivity_dict_dict):
        """Parse the sub community connectivity dict from a JSON dictionary.

        Args:
            sub_community_connectivity_dict_dict (Dict): The JSON dictionary of the sub community
            connectivity dictionary. Do not get confused by _dict_dict, the first dict refers to
            the object being a dictionary, and the second refers to the parsed JSON dictionary.

        Returns:
            Dict: The actual sub community connectivity dictionary object.
        """
        sub_community_connectivity_dict: Dict[int, Dict[int, Distribution]] = dict()

        # parse the json dict object of sub_community_connectivity_dict
        for key in sub_community_connectivity_dict_dict:
            inner_dict: Dict[int, Distribution] = dict()

            for inner_key in sub_community_connectivity_dict_dict[key]:
                inner_dict[int(inner_key)] = self.parse_distribution(
                    sub_community_connectivity_dict_dict[key][inner_key])

            sub_community_connectivity_dict[int(key)] = inner_dict

        return sub_community_connectivity_dict

    def parse_sub_community_types(self, sub_community_types_list: List) -> List:
        """Parse a sub community types based on a list of objects in the form of JSON dictionary.

        Args:
            sub_community_types_list (List): A list containing the sub community types JSON
            dictionary.

        Returns:
            List[Sub_Community_Type]: The list of parsed sub community type objects.
        """
        sub_community_types = list()

        for sub_community_type_dict in sub_community_types_list:
            # parse the object fields
            community_type_role = \
                self.parse_community_type_role(sub_community_type_dict['community_type_role'])

            number_of_members_distribution = \
                self.parse_distribution(sub_community_type_dict['number_of_members_distribution'])

            connectivity_distribution = \
                self.parse_distribution(sub_community_type_dict['connectivity_distribution'])

            transmission_potential_distribution = \
                self.parse_distribution(sub_community_type_dict['transmission_potential_distribution'])

            sub_community_types.append(Sub_Community_Type(community_type_role,
                                                          sub_community_type_dict['sub_community_name'],
                                                          number_of_members_distribution,
                                                          connectivity_distribution,
                                                          transmission_potential_distribution))
        return sub_community_types

    def parse_community_type_role(self, community_type_role_dict: Dict) -> Community_Type_Role:
        """Parse a community type role object from the respective JSON dictionary.

        Args:
            community_type_role_dict (Dict): The JSON dictionary containing all the information of
            a community type role.

        Returns:
            Community_Type_Role: The actual community type role object.
        """
        age_distribution = self.parse_distribution(community_type_role_dict['age_distribution'])
        gender_distribution = self.parse_distribution(community_type_role_dict['gender_distribution'])
        time_cycle_distribution = self.parse_distribution(community_type_role_dict['time_cycle_distribution'])
        is_profession = community_type_role_dict['is_profession']
        priority = community_type_role_dict['priority']

        return Community_Type_Role(age_distribution, gender_distribution, time_cycle_distribution,
                                   is_profession, priority)

    def parse_distributions(self, distributions_list: List) -> List:
        """Parse the distributions from the distributions list, extracted from a JSON dictionary.

        Args:
            distributions_list (List): List of the distributions, each of them is JSON encoded using
            the to_json method of the class.

        Returns:
            List[Distribution]: A list containing the distribution objects.
        """
        distributions = list()

        for distribution_dict in distributions_list:
            distributions.append(self.parse_distribution(distribution_dict))

        return distributions

    def parse_distribution(self, distribution_dict: Dict):
        """Parse the distribution object based on distribution JSON dictionary.

        Args:
            distribution_dict (Dict): A JSON dictionary containing all the required information to
            build a distribution.

        Returns:
            Distribution: The parsed distribution object.
        """

        module = __import__('distributions')
        distribution = getattr(module, distribution_dict['name'])

        return distribution(distribution_dict['params'])

    def build_path(self):
        """Build the required path to access a JSON file.

        Raises:
            FileNotFoundError: If the src is not running in the project folder this exception
            will be thrown.
        """
        # build the file address
        if basename(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) == 'Pyfectious':
            folder_path = os.path.join(os.getcwd(), os.pardir, 'data', 'json', self.folder_name)
        elif basename(os.getcwd()) == 'Pyfectious':
            folder_path = os.path.join(os.getcwd(), 'data', 'json', self.folder_name)
        else:
            raise FileNotFoundError('Run the source in "project", "src", or "example" folder!')

        # make the folder, pass if exists
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass

        self.path = os.path.join(folder_path, self.json_name)
        self.path += '.json'


class ComplexEncoder(json.JSONEncoder):
    """A class to encode hierarchical complex objects to JSON format.

    """

    def default(self, obj):
        """The converter method.

        If object is still complex, the method runs toJSON method.

        Args:
            obj (object): The object which should be converted.

        Returns:
            str: The JSON string result of the conversion.
        """
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        else:
            return json.JSONEncoder.default(self, obj)


if __name__ == '__main__':
    # implement local tests here
    p = Parser()

    # create a population generator from json file
    pg = p.parse_population_generator()

    # check the output data
    print(type(pg))
    p.build_json(pg)
    p.save_json()
