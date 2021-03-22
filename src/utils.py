from enum import Enum
from typing import List, Dict

from texttable import Texttable

from logging_settings import logger


class Infection_Status(Enum):
    """Enum for the infectious state .

    Notes:
        CLEAN: the individual has not contracted the virus.
        INCUBATION: the individual has contracted the virus but is not contagious.
        INFECTION: the person is infected, and can transmit the disease.
    """
    CLEAN = 0
    INCUBATION = 1
    CONTAGIOUS = 2

    # TODO: implement other infection status if applicable.


class Simulation_Event(Enum):
    """Enum for simulation events located in time simulator file.

    Important Note:
        The value of each definition is the priority entangled with the event. Lower
        numbers indicate higher priorities. Obviously, the priority is an integer.

        INCUBATION: This event is added to the heap when person is just infected.
        INFECTION: This event is added when the disease is developed and the person is contagious.
        SCHEDULE: A plan day event is activated by this event type for a person.
        TRANSITION: A transition event simulates the transition between different plans in a day.
        TRANSMISSION: The virus spread event is responsible for investigating the virus transmission among people.
    """
    NONE = 0
    INCUBATION = 1
    INFECTION = 2
    PLAN_DAY = 3
    TRANSITION = 4
    VIRUS_SPREAD = 5


class Health_Condition(Enum):
    """Enum for various health conditions status.

    The class Health Condition, inherits the Enum class and presents the most important
    health status constants. These are later used to develop methods related to people's
    health condition.
    """

    IS_INFECTED = 1
    IS_NOT_INFECTED = 2
    HAS_BEEN_INFECTED = 3
    HAS_NOT_BEEN_INFECTED = 4
    ALIVE = 5
    DEAD = 6
    ALL = 7

    def to_json(self):
        return dict(name=self.name,
                    value=self.value)


class Operator(Enum):
    """Enum for comparison operators.

    The class Operator, inherits the Enum class and presents comparison operations
    as the attributes of the class.
    """
    # Operations
    EQ = 1  # Equal
    NE = 2  # Not Equal
    LT = 3  # Less Than
    LE = 4  # Less Than Equal
    GE = 5  # Greater Than Equal
    GT = 6  # Greater Than

    def to_json(self):
        return dict(name=self.name,
                    value=self.value)


class Comparison:
    """A class to perform comparison related tasks.

    This class represents methods to compare between two numbers in a compact
    way. The class is directly using the Operator enum, to find the suitable
    operator of comparison.

    """

    @staticmethod
    def compare(first_argument: float, second_argument: float, operation_type: Operator) -> bool:
        if operation_type is Operator.EQ:
            return first_argument == second_argument
        elif operation_type is Operator.NE:
            return first_argument != second_argument
        elif operation_type is Operator.LT:
            return first_argument < second_argument
        elif operation_type is Operator.LE:
            return first_argument <= second_argument
        elif operation_type is Operator.GE:
            return first_argument >= second_argument
        elif operation_type is Operator.GT:
            return first_argument > second_argument
        return False


class Statistics:
    """"Statistics class is employed to display real time disease statistics.

    This class consists of a few methods related to finding and displaying the
    statistics of entities in the simulation environment, and in real-time. For
    instance, imagine that you have a list of people and you want to know how
    many of them are dead or alive. The same holds for the families.

    Attributes:
        people_statistics_dict (Dict[Health_Condition, int]): A dictionary to store
        the real-time statistics of the simulation's population.
    """

    def __init__(self, simulator, keep_role_statistics: bool = False):
        """Initialize the statistic object.

        Args:
            simulator (Simulator): The main simulation object.
        """
        self.keep_role_statistics = keep_role_statistics

        population_size = simulator.population_generator.population_size
        self.people_statistics_dict: Dict[Health_Condition, int] = {
            Health_Condition.IS_INFECTED: 0,
            Health_Condition.IS_NOT_INFECTED: population_size,
            Health_Condition.HAS_BEEN_INFECTED: 0,
            Health_Condition.HAS_NOT_BEEN_INFECTED: population_size,
            Health_Condition.ALIVE: population_size,
            Health_Condition.DEAD: 0,
            Health_Condition.ALL: population_size
        }

        if self.keep_role_statistics:
            self.role_statistics_dict: Dict[str, Dict[Health_Condition, int]] = dict()
            for role_name in simulator.population_generator.community_role_names:
                self.role_statistics_dict[role_name] = {
                    Health_Condition.IS_INFECTED: 0,
                    Health_Condition.IS_NOT_INFECTED: 0,
                    Health_Condition.HAS_BEEN_INFECTED: 0,
                    Health_Condition.HAS_NOT_BEEN_INFECTED: 0,
                    Health_Condition.ALIVE: 0,
                    Health_Condition.DEAD: 0,
                    Health_Condition.ALL: 0
                }

            for person in simulator.people:
                for role_name in simulator.population_generator.community_role_names:
                    if person.has_role(role_name):
                        self.role_statistics_dict[role_name][Health_Condition.ALL] += 1
                        self.role_statistics_dict[role_name][Health_Condition.ALIVE] += 1
                        self.role_statistics_dict[role_name][Health_Condition.IS_NOT_INFECTED] += 1
                        self.role_statistics_dict[role_name][Health_Condition.HAS_NOT_BEEN_INFECTED] += 1

    def update_people_statistic(self, health_condition: Health_Condition, person, value: int = 1):
        """Update the people's statistic dictionary given the item.

        Args:
            person (Person): The person causing the change in statistics.
            value (int): The value to be added to the given item.
            health_condition (Health_Condition): The item in the dictionary
            that needs to be updated.
        """
        if health_condition is Health_Condition.IS_INFECTED:
            self.people_statistics_dict[Health_Condition.IS_INFECTED] += value
            self.people_statistics_dict[Health_Condition.IS_NOT_INFECTED] -= value

            if self.keep_role_statistics:
                for role in person.roles:
                    self.role_statistics_dict[role][Health_Condition.IS_INFECTED] += value
                    self.role_statistics_dict[role][Health_Condition.IS_NOT_INFECTED] -= value

        if health_condition is Health_Condition.IS_NOT_INFECTED:
            self.people_statistics_dict[Health_Condition.IS_INFECTED] -= value
            self.people_statistics_dict[Health_Condition.IS_NOT_INFECTED] += value

            if self.keep_role_statistics:
                for role in person.roles:
                    self.role_statistics_dict[role][Health_Condition.IS_INFECTED] -= value
                    self.role_statistics_dict[role][Health_Condition.IS_NOT_INFECTED] += value

        if health_condition is Health_Condition.DEAD:
            self.people_statistics_dict[Health_Condition.DEAD] += value
            self.people_statistics_dict[Health_Condition.ALIVE] -= value

            if self.keep_role_statistics:
                for role in person.roles:
                    self.role_statistics_dict[role][Health_Condition.DEAD] += value
                    self.role_statistics_dict[role][Health_Condition.ALIVE] -= value

        if health_condition is Health_Condition.HAS_BEEN_INFECTED:
            self.people_statistics_dict[Health_Condition.HAS_BEEN_INFECTED] += value
            self.people_statistics_dict[Health_Condition.HAS_NOT_BEEN_INFECTED] -= value

            if self.keep_role_statistics:
                for role in person.roles:
                    self.role_statistics_dict[role][Health_Condition.HAS_BEEN_INFECTED] += value
                    self.role_statistics_dict[role][Health_Condition.HAS_NOT_BEEN_INFECTED] -= value

    def get_people_statistics(self) -> Dict[Health_Condition, int]:
        """Find the disease statistics of the people in real-time.

        Returns:
            Dict[Health_Condition, int]: The statistics dictionary such that keys are
            of Health Condition type and the values are statistics.
        """

        return self.people_statistics_dict

    def get_role_statistics(self, role_name: str) -> Dict[Health_Condition, int]:
        """Find the statistics related to a specific role in the community, e.g., teachers.

        Args:
            role_name (str): The target role to find its statistics.

        Returns:
            Dict[str, int]: The statistics dictionary such that keys are of Health Condition type and
                            the values are statistics.
        """
        if self.keep_role_statistics:
            return self.role_statistics_dict[role_name]
        return None

    @staticmethod
    def report(simulator, report_statistics: int):
        """Report the statistics at the end of the simulation.

        Args:
            simulator (Simulator): The main simulator object.

            report_statistics (int): If 2, all the stats are shown, if 1,
            only the most important ones like the population stats, and if 0,
            no statistics is printed on the console log.
        """
        if report_statistics == 1 or report_statistics == 2:
            Statistics.display_people_statistics(simulator)
            Statistics.display_simulator_statistics(simulator)

        if report_statistics == 2:
            Statistics.display_family_statistics(simulator.people, simulator.families)
            Statistics.display_disease_characteristics(simulator.disease_properties)
            Statistics.display_population_statistics(simulator.population_generator)

    @staticmethod
    def get_family_statistics(people: List, families: List) -> Dict[Health_Condition, int]:
        """This function extracts the real time statistics of all the families passed in the arguments.

        TODO: Refactor to dynamic programming.

        Args:
            people (List[Person]): The people that joint to build the families.
            families (List[Family]): The families list passed to obtain their statistics.

        Returns:
            Dict[str, int]: The statistics dictionary such that keys are of Health Condition type and
                            the values are statistics.
        """
        statistics_dict = {Health_Condition.IS_INFECTED: 0, Health_Condition.IS_NOT_INFECTED: 0,
                           Health_Condition.HAS_BEEN_INFECTED: 0, Health_Condition.HAS_NOT_BEEN_INFECTED: 0,
                           Health_Condition.ALIVE: 0, Health_Condition.DEAD: 0, Health_Condition.ALL: len(families)}

        dead, is_infected, has_been_infected = 0, 0, 0

        for family in families:
            for id in family.people_ids:
                person = people[id]

                if person.infection_status is not Infection_Status.CLEAN:
                    is_infected = 1
                if person.times_of_infection > 0:
                    has_been_infected = 1
                if not person.is_alive:
                    dead = 1

            if dead == 0:
                statistics_dict[Health_Condition.ALIVE] += 1
            if is_infected == 0:
                statistics_dict[Health_Condition.IS_NOT_INFECTED] += 1
            if has_been_infected == 0:
                statistics_dict[Health_Condition.HAS_NOT_BEEN_INFECTED] += 1

            statistics_dict[Health_Condition.DEAD] += dead
            statistics_dict[Health_Condition.IS_INFECTED] += is_infected
            statistics_dict[Health_Condition.HAS_BEEN_INFECTED] += has_been_infected

            is_infected, has_been_infected, dead = 0, 0, 0

        return statistics_dict

    @staticmethod
    def get_r0_value(simulator) -> float:
        """Get the R0 value of a completed simulation.

        Args:
            simulator (Simulator): The main simulator object.

        Returns:
            float: The value of R0.
        """
        r0: float = 0
        number_of_infecteds: int = simulator.statistics.get_people_statistics()[Health_Condition.HAS_BEEN_INFECTED]

        for person in simulator.people:
            r0 += len(person.transmission_ids)

        r0 /= number_of_infecteds
        return r0

    @staticmethod
    def display_spread_statistics(simulator):
        """Print the parameters related to the spread like R0 of a completed simulation.

        R0: At the beginning of an epidemics the R0 value describes how many other people
        an infected person will infect on average.

        Args:
            simulator (Simulator): The simulator objectd.
        """
        t = Texttable()
        t.add_rows([['Parameter', 'Value'],
                    ['R0', simulator.end_time.init_date_time],
                    ['R effective', simulator.end_time.get_utc_time()],
                    ['Spread Period', simulator.spread_period.get_minutes()],
                    ['Database', simulator.database_name]])

        logger.info(f'\n{t.draw()}')

    @staticmethod
    def display_simulator_statistics(simulator):
        """Print the simulator data on the terminal.

        Args:
            simulator (Simulator): The simulator object which its data is printed.
        """
        t = Texttable()
        t.add_rows([['Simulator', 'Data'],
                    ['Start Time', simulator.end_time.init_date_time],
                    ['End Time', simulator.end_time.get_utc_time()],
                    ['Spread Period', simulator.spread_period.get_minutes()],
                    ['Database', simulator.database_name]])

        logger.info(f'\n{t.draw()}')

    @staticmethod
    def display_people_statistics(simulator):
        """Print the people's statistics table on the terminal

        Args:
            simulator (Simulator): The simulation environment.
        """
        stat_dict = simulator.statistics.get_people_statistics()

        total_people = stat_dict[Health_Condition.ALL]
        dead = stat_dict[Health_Condition.DEAD]
        is_infected = stat_dict[Health_Condition.IS_INFECTED]
        has_been_infected = stat_dict[Health_Condition.HAS_BEEN_INFECTED]

        t = Texttable()
        t.add_rows([['People', 'Count'],
                    ['Population Size', total_people],
                    ['Confirmed (Active + Close)', has_been_infected],
                    ['Total Death Cases', dead],
                    ['Total Recovered', has_been_infected - dead],
                    ['Currently Active Cases', is_infected]])
        logger.info(f'\n{t.draw()}')

    @staticmethod
    def display_family_statistics(people: List, families: List):
        """Print the family statistics on the terminal.

        Args:
            people (List[Person]): The people of the simulator that are merged into families.
            families (List[Family]): The families of the simulation environment.
        """
        stat_dict = Statistics.get_family_statistics(people, families)

        total_families = len(families)
        dead = stat_dict[Health_Condition.DEAD]
        is_infected = stat_dict[Health_Condition.IS_INFECTED]
        has_been_infected = stat_dict[Health_Condition.HAS_BEEN_INFECTED]

        t = Texttable()
        t.add_rows([['Families', 'Count'],
                    ['Number of Families', total_families],
                    ['Confirmed (Active + Close)', has_been_infected],
                    ['Total Death Cases', dead],
                    ['Currently Active Cases', is_infected]])
        logger.info(f'\n{t.draw()}')

    @staticmethod
    def display_population_statistics(population_generator):
        """Print population statistics on the terminal.

        Args:
            population_generator (Population_Generator): The population generator class consisting of population data.
        """
        # family patterns
        patterns_table = Texttable()
        patterns = population_generator.family_pattern_probability_dict
        for pattern in patterns:
            members_count = pattern.number_of_members
            genders = ['Male' if gender else 'Female' for gender in pattern.genders]
            patterns_table.add_rows([['Family Pattern Probability', 'Number of Members', 'Genders'],
                                     [patterns[pattern], members_count, genders]])

        logger.info(f'\n{patterns_table.draw()}')

        # community types
        types_table = Texttable()
        types = population_generator.community_types
        for community_type in types:
            name = community_type.name
            communities_count = community_type.number_of_communities
            sub_community_types = [sct.name for sct in community_type.sub_community_types]
            types_table.add_rows([['Community Type', 'Number of Communities', 'Sub-community Types'],
                                  [name, communities_count, sub_community_types]])

        logger.info(f'\n{types_table.draw()}')

    @staticmethod
    def display_disease_characteristics(disease_properties):
        """Print the statistics related to disease in terminal.

        Args:
            disease_properties (Disease_Properties): The disease properties object containing disease information.
        """

        infectious_rate_distribution = disease_properties.infectious_rate_distribution
        immunity_distribution = disease_properties.immunity_distribution
        disease_period_distribution = disease_properties.disease_period_distribution
        death_probability_distribution = disease_properties.death_probability_distribution

        t = Texttable()
        t.add_rows([['Disease Property', 'Distribution Type', 'Parameters'],
                    ['Infectious Rate', infectious_rate_distribution.__class__.__name__,
                     infectious_rate_distribution.parameters_dict],
                    ['Immunity Rate', immunity_distribution.__class__.__name__,
                     immunity_distribution.parameters_dict],
                    ['Disease Period', disease_period_distribution.__class__.__name__,
                     disease_period_distribution.parameters_dict],
                    ['Death Probability', death_probability_distribution.__class__.__name__,
                     death_probability_distribution.parameters_dict]])

        logger.info(f'\n{t.draw()}')
