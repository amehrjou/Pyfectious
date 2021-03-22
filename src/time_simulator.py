import _pickle as pickle
import heapq
import os
import sys
from datetime import datetime, timedelta
from os.path import basename
from typing import List, Tuple

from tqdm.auto import tqdm

from database import Database
from disease_manipulator import Disease_Properties
from distributions import Random
from logging_settings import logger
from observer import Observer
from population_generator import Person, Population_Generator, Connection_Edge, Community
from population_generator import Place
from time_handle import Time
from utils import Statistics, Health_Condition, Simulation_Event, Infection_Status


class Simulator:
    """This class handles the operation and preparations of simulation.

    This object provides a set of methods to initialize and run a simulation.
    Some of its objectives are to generate/save/load the simulation model, initialize
    the simulation properties like database, and to run the main simulation based on
    the given population structure and disease properties.

    Attributes
    ----------
    population_generator (Population_Generator): The population generator object containing
    the data required to establish the population model.

    clock (Time): The main simulation clock.
    end_time (Time): The final time of the simulation.
    spread_period (Time): The period that disease transmission is being investigated.
    database (Database): The main database of the simulation to store the simulation data.
    people (list[Person]): The people created out of the population generator.
    graph (Dict[int, List]): The graph of all the people in the simulation.
    families (List[Family]): The families built out of the population generator.

    communities (List[Community]): The communities involved in the
    simulation population structure.

    events (List[Event]): The list of all the events in the simulation, e.g., Transition,
    Virus Spread.

    disease_properties (Disease_Properties): The properties of the disease are stored inside
    this property of the simulation.

    commands (List[Command]): A list of commands to be executed during the simulation time.
    This is also known as simulation policies.

    observers (List[Observer]): A list of all observers in the simulation.
    initialized_infected_ids (List[int]): A list of people that initially have the disease.
    """

    def __init__(self, population_generator: Population_Generator,
                 disease_properties: Disease_Properties):
        """Initialize a simulator object.

        Args:
            population_generator (Population_Generator): The population generator object
            required to create families, communities, and people.

            disease_properties (Disease_Properties): The disease properties object is
            necessary to obtain a correct estimation of disease characteristics in the
            simulation.
        """
        self.population_generator = population_generator
        self.disease_properties = disease_properties

        self.clock, self.end_time = None, None
        self.statistics = None
        self.people, self.graph, self.families, self.communities = list(), dict(), list(), dict()
        self.events = list()

    def initialize_people(self):
        """Initialize every person in the simulator.people object.
        """
        for person in self.people:
            person.initialize()

    def initialize_db(self):
        """Initialize the database associated with the simulation environment,
        along with creating the tables for people, families, and communities.
        """
        if self.database_name is None:
            self.database = Database('simulator')
        else:
            self.database = \
                Database('simulator_' + str(self.database_name[0]) + '_' + str(self.database_name[1]))


        # a table to simulation statistics
        self.database.create_table(name='simulation',
                                   columns=[
                                       ('simulator_id', 'integer'),
                                       ('people_confirmed_cases', 'integer'),
                                       ('people_death_cases', 'integer'),
                                       ('people_active_cases', 'integer')
                                   ])
        # a table to keep people information
        self.database.create_table(name='people',
                                   columns=[
                                       ('id_number', 'integer'),
                                       ('age', 'integer'),
                                       ('health_condition', 'real'),
                                       ('gender', 'integer'),
                                       ('infection_status', 'integer'),
                                       ('is_alive', 'integer'),
                                       ('has_profession', 'integer'),
                                       ('times_of_infection', 'integer'),
                                       ('is_quarantined', 'integer'),
                                       ('location', 'str'),
                                       ('observation_id', 'integer'),
                                       ('observer_id', 'integer'),
                                       ('date_time', 'integer')
                                   ])

        # TODO: remove and create a consistent database
        self.database.delete_data('people')

        # TODO: tables reserved for later in case of use, fill accordingly
        self.database.create_table(name='families',
                                   columns=[('family_id', 'integer')])

        self.database.create_table(name='communities',
                                   columns=[('community_id', 'integer')])

    def initialize_simulation(self):
        """Initialize the simulation. This initialization is required when the
        simulator.simulate function is being called. The initialization deals with
        the simulator clock, database initiation, various simulation events, etc.
        """
        self.events = list()
        self.initialize_db()
        self.initialize_people()
        self.statistics = Statistics(simulator=self)
        self.clock = Time(delta_time=timedelta(0), init_date_time=self.end_time.init_date_time)
        self.initialize_plan_day_events(self.end_time)
        self.initialize_virus_spread_events(self.end_time, self.spread_period)
        self.initialize_infections(self.initialized_infected_ids)

    def initialize_plan_day_events(self, end_time: Time):
        """Initialize plan day event is the place that the plan_day_event task is
        pushed into the simulation heap structure.

        Args:
            end_time (Time): The simulation end time.
        """
        total_simulation_days = end_time.get_total_days()
        for i in range(total_simulation_days + 1):
            plan_time = Time(timedelta(days=i))
            plan_day_event = Plan_Day_Event(plan_time.get_minutes(), Simulation_Event.PLAN_DAY)
            heapq.heappush(self.events, plan_day_event)

    def initialize_virus_spread_events(self, end_time: Time, spread_period: Time):
        """Create and push the virus spread events into the simulation heap.

        Args:
            end_time (Time): The simulator final time.
            spread_period (Time): The spread period of the simulation on which the virus
            spread events are processed.
        """
        for i in range(0, end_time.get_minutes() + 1, spread_period.get_minutes()):
            virus_spread_event = Virus_Spread_Event(i, Simulation_Event.VIRUS_SPREAD)
            heapq.heappush(self.events, virus_spread_event)

    def initialize_infections(self, initialized_infected_ids: List[int]):
        """Initialize the infections by building an infection class and
        adding the corresponding event to the heap.

        Args:
            initialized_infected_ids (List[int]): The list of id numbers related
            to the people first having the disease.
        """
        Infection.start_infections(new_infected_ids=initialized_infected_ids,
                                   simulator=self)

    def generate_model(self, is_parallel: bool = False, show_progress: bool = True):
        """Generates a the simulation model, including the people, graph, families,
        and communities.

        Args:
            is_parallel (bool): If true, the function uses multiprocessing to boost
            the computations. Otherwise, the method runs in normal single processing
            mode.

            show_progress (bool, optional): Whether to show the progress bar or not.
            Defaults to True.
        """
        self.people, self.graph, self.families, self.communities = \
            self.population_generator.generate_population(is_parallel, show_progress)

        logger.info('Simulation model generated')

    def save_model(self, model_name: str):
        """Save the simulation model generated in generate model method for later use.

        This function saves the model in a pickle file located in the data/pickle
        folder.

        Warning: Using save model will change the reference of the objects, and leads to
        creation of different communities, people, families, etc. Only use it once to
        maintain consistency of the references.

        Args:
            model_name (str): The name of the pickle file to be saved.
        """
        if basename(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) == 'covid19_simulator':
            path = os.path.join(os.getcwd(), os.pardir, 'data', 'pickle', model_name)
        elif basename(os.getcwd()) == 'covid19_simulator':
            path = os.path.join(os.getcwd(), 'data', 'pickle', model_name)
        else:
            logger.warning('Failed to save model, change directory to src, example, or \
                project main directory and try again!')
            return

        os.makedirs(path, exist_ok=True)

        graph_path = os.path.join(path, 'graph.pickle')
        people_path = os.path.join(path, 'people.pickle')
        families_path = os.path.join(path, 'families.pickle')
        communities_path = os.path.join(path, 'communities.pickle')

        with open(people_path, 'wb') as f:
            pickle.dump(self.people, f)

        with open(graph_path, 'wb') as f:
            pickle.dump(self.graph, f)

        with open(families_path, 'wb') as f:
            pickle.dump(self.families, f)

        with open(communities_path, 'wb') as f:
            pickle.dump(self.communities, f)

        logger.info(f'Simulator model {model_name} saved')

    def load_model(self, model_name: str):
        """Load a saved simulation model from the pickle folder.

        This function automatically sets the simulation main entities to
        the data loaded from the pickle file.

        Args:
            model_name (str): The name of the model to be loaded.
        """
        if basename(os.getcwd()) == 'covid19_simulator':
            sys.path.insert(1, 'src')
            path = os.path.join(os.getcwd(), 'data', 'pickle', model_name)
        elif basename(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) == 'covid19_simulator':
            sys.path.insert(1, os.path.join(os.pardir, 'src'))
            path = os.path.join(os.getcwd(), os.pardir, 'data', 'pickle', model_name)
        else:
            raise FileNotFoundError('Failed to save model, change directory to src, example, or \
                project main directory and try again!')

        graph_path = os.path.join(path, 'graph.pickle')
        people_path = os.path.join(path, 'people.pickle')
        families_path = os.path.join(path, 'families.pickle')
        communities_path = os.path.join(path, 'communities.pickle')

        with open(people_path, 'rb') as f:
            self.people = pickle.load(f)

        with open(graph_path, 'rb') as f:
            self.graph = pickle.load(f)

        with open(families_path, 'rb') as f:
            self.families = pickle.load(f)

        with open(communities_path, 'rb') as f:
            self.communities = pickle.load(f)

        logger.info(f'Simulator model {model_name} loaded')

    def execute_observers(self):
        """This function is used to parallelize the observation process.

        The user-defined observation classes run here and store what they want
        into the database, using their own observer id.
        """
        for observer in self.observers:
            if not observer.is_deleted:
                observer.observe(self, self.end_time)
            if observer.observation_is_done():
                observer.is_deleted = True

    def execute_commands(self):
        """Executes the commands defined by user as the simulator input.

        A command gets deleted from the list whenever successfully committed.
        """
        for command in self.commands:
            if not command.is_deleted:
                command.take_action(self, self.end_time)
            if command.action_is_done():
                command.is_deleted = True

    def simulate(self, end_time: Time, spread_period: Time, initialized_infected_ids: List[int],
                 commands: List, observers: List, report_statistics: int = 1, database_name: Tuple = None,
                 show_progress: bool = True):
        """The main simulator function that starts the simulation given a certain criteria.

        The simulation main loop is located inside this function, in addition to collecting
        the observers and commands (policy).

        Args:
            end_time (Time): The simulation end time. Determines the total period
            of the simulation.

            spread_period (Time): The spread period determines the period of running the
            virus spread function.

            initialized_infected_ids (List[int]): A list of infected people at the beginning
            of the simulation.

            commands (List[Command]): A list of actions given to the simulator to contract the
            spread of the virus. The acceptable commands are located in commands.py module.

            observers (List[Observer]): The observer object to record the data from simulation
            into the database.

            report_statistics (int, optional): This parameter determines the degree of statistics
            shown after the simulation concluded. Starting from 0, meaning no statistics at all,
            and goes all the way to 2, where all the available statistics are shown in the console.
            Defaults to 1.

            database_name (Tuple, optional): The name of the database in case a change is required.
            Default to None.

            show_progress (bool, optional): Whether to show the progress bar or not.
            Defaults to True.
        """

        # Initialize simulation
        logger.info('Initializing the simulation')
        self.initialized_infected_ids = initialized_infected_ids
        self.end_time, self.spread_period = end_time, spread_period
        self.commands, self.observers = commands, observers
        self.database_name = database_name
        self.initialize_simulation()

        # Print a log and the progress indicator
        logger.info('Starting the simulation')

        with tqdm(total=self.end_time.get_minutes(), file=sys.stdout, disable=not show_progress) \
                as progress_bar:

            # Simulation main loop
            while Time.check_less(self.clock, self.end_time):

                # Events
                event = heapq.heappop(self.events)
                event.activate(self)

                # Observations
                self.execute_observers()

                # Commands
                self.execute_commands()

                # Update clock
                self.clock.set_minutes(event.minute)

                # Show progress
                progress_bar.update(self.clock.get_minutes() - progress_bar.n)

        logger.info('Simulation completed')

        # Show statistics
        self.statistics.report(self, report_statistics)

        # Database termination
        self.database.commit()

    def clear(self):
        """Clear the main objects of the simulation.
        """
        self.people.clear()
        self.families.clear()
        self.communities.clear()
        self.observers.clear()
        self.commands.clear()

        self.database.close()

        self.disease_properties = None
        self.population_generator = None

    def to_json(self):
        """Convert object fields to a JSON dictionary.

            Returns:
                dict: The JSON dictionary.
        """

        return dict(name=self.__class__.__name__,
                    end_time=self.end_time,
                    spread_period=self.spread_period,
                    initialized_infected_ids=self.initialized_infected_ids,
                    commands=self.commands,
                    observers=self.observers)


class Infection:
    """A perfect container to hold the data related to each individual's infection.

    This object provides a set of tools to investigate the infection situation of
    people in the simulation. The object may later determine whether the person
    will survive or die from the infection.

    Attributes
    ----------
    person (Person): The person related to this infection object.
    starting_time_incubation (int): The start time of the incubation period in minutes.
    ending_time_transmission (int): The end time of transmission state, and the disease.
    ending_incubation_time (int): The ending time of the incubation period.
    death_probability (float): The probability of person being dead as a result
    of the infection.
    """

    def __init__(self, person: Person, clock: Time, disease_properties: Disease_Properties):
        """Initialize the infection object using a person and the properties of the disease.

        TODO: Calculate death probability in the __init__ and assign a
              recovery or death period individually.

        Args:
            person (Person): The person object associated with the infection class.
            clock (Time): The clock to determine the infection start and end dates.

            disease_properties (Disease_Properties): The disease properties object
            of the simulation.
        """
        self.person = person
        self.starting_time_incubation = int(clock.get_minutes())

        self.ending_time_incubation = int(self.starting_time_incubation +
                                          disease_properties.generate_incubation_period(clock, person))

        self.ending_time_transmission = int(self.ending_time_incubation +
                                            disease_properties.generate_disease_period(clock, person))

        self.death_probability = disease_properties.generate_death_probability(clock, person)

    def will_die(self) -> bool:
        """Determines whether a person will die of the infection of not.

        Important Note:
            In addition to death probability (aka mortality rate of the virus),
            the person's health condition is highly effective to the probability
            of death.

        Returns:
            bool: True, if the person will die.

        """
        probability = self.death_probability * (1 - self.person.health_condition)
        return Random.flip_coin(probability)

    @staticmethod
    def start_infections(new_infected_ids, simulator: Simulator):
        """ Starts the infection routine, builds an Infection object for each and every
        newly infected person.

        The firs event pushed is the INCUBATION, since the disease starts with an incubation period.

        Args:
            new_infected_ids (List[int]): The new infected people.
            simulator (Simulator): The simulator object.
        """
        for person_id in new_infected_ids:
            simulator.people[person_id].infection_status = Infection_Status.INCUBATION
            simulator.statistics.update_people_statistic(Health_Condition.IS_INFECTED,
                                                         simulator.people[person_id])

            if not simulator.people[person_id].times_of_infection:
                simulator.statistics.update_people_statistic(Health_Condition.HAS_BEEN_INFECTED,
                                                             simulator.people[person_id])
            simulator.people[person_id].times_of_infection += 1

            infection = Infection(simulator.people[person_id], simulator.clock, simulator.disease_properties)

            incubation_event = Incubation_Event(infection.ending_time_incubation,
                                                Simulation_Event.INCUBATION,
                                                infection)

            heapq.heappush(simulator.events, incubation_event)


class Event:
    """This class enables the ability to create a variety of events.

    This object provides an interface for more specific event types to inherit. The
    class also determines the priority of a given event based on its type.

    TODO: Develop enum for event types.

    Attributes
    ----------
    minute (int): The elapsed minutes from the start of the simulation
    in which this event happens.

    event_type (Simulation_Event): The event type. This parameter can take the
    values determined in Simulation_Event enum.

    priority (int): The priority of the event, e.g. transition events are
    less important than plan day events.
    """

    def __init__(self, minute: int, event_type: Simulation_Event):
        """Initialize an event object, given the event minute and type.

        This class is employed whenever an event is needed to be happen
        inside the simulation.

        Args:
            minute (int): The time that event is going to happen in terms of minutes.

            event_type (Simulation_Event): The event type. This parameter can take the
            values determined in Simulation_Event enum.
        """
        self.minute = minute
        self.type = event_type
        self.priority = int(event_type.value)

    def check_time(self, clock: Time):
        """Check whether a given time is equal to event time or not.

        Args:
            clock (Time): The given time to compare with event time.

        Returns:
            bool : True, if the given time is the same as event time.

        """
        return clock.get_minutes() == self.minute

    def activate(self, simulator: Simulator):
        """Activate the current event.

        Args:
            simulator (Simulator): The simulator object.
        """
        raise NotImplementedError

    def __lt__(self, other):
        """Check whether an event is less important than another event.

        Args:
            other (Event): The other event used in comparison.

        Returns:
            bool : True if the priority is less than the given event.

        """
        return (self.minute, self.priority) < (other.minute, other.priority)


class Incubation_Event(Event):
    """This event concludes the end of incubation period for a person.

    After the incubation period, the person is now capable of transmitting the disease
    to other individuals. During the incubation period person cannot be infected or spread
    the disease.

    Attributes
    ----------
    infection (Infection): The infection class related to this infection end event.
    minute (int): The elapsed minutes from the start of the simulation
    in which this event happens.

    event_type (Simulation_Event): The event type. This parameter can take the
    values determined in Simulation_Event enum.
    """

    def __init__(self, minute: int, event_type: Simulation_Event, infection: Infection):
        """Initialize an incubation event.

        Args:
            minute (int): The minutes remaining util the end of infection period.
            event_type (Simulation_Event): Type of the event is Incubation.
            infection (Infection): The infection class entangled to this event.
        """
        super().__init__(minute, event_type)
        self.infection = infection

    def activate(self, simulator: Simulator):
        """Activate the incubation event to conclude the incubation period.

        Upon activation, the person will be considered contagious and can potentially
        spread the disease. The infection status changes to INFECTION.

        Args:
            simulator: The simulator object required to activate this event.
        """
        self.infection.person.infection_status = Infection_Status.CONTAGIOUS

        infection_event = Infection_Event(self.infection.ending_time_transmission,
                                          Simulation_Event.INFECTION,
                                          self.infection)

        heapq.heappush(simulator.events, infection_event)


class Infection_Event(Event):
    """This event signals the conclusion of an infection for a person.

    After the infection is over, the person is decided to be either dead or alive,
    and the infection_status attribute of the person changes accordingly.

    Attributes
    ----------
    infection (Infection): The infection class related to this infection end event.
    minute (int): The elapsed minutes from the start of the simulation
    in which this event happens.

    event_type (Simulation_Event): The event type. This parameter can take the
    values determined in Simulation_Event enum.
    """

    def __init__(self, minute: int, event_type: Simulation_Event, infection: Infection):
        """Initialize an infection end event to signal the end of an infection period.

        Args:
            minute (int): The minutes remaining util the end of infection period.
            event_type (Simulation_Event): Type of the event is Incubation.
            infection (Infection): The infection class entangled to this event.
        """
        super().__init__(minute, event_type)
        self.infection = infection

    def activate(self, simulator: Simulator):
        """Activate the Infection End event.

        Upon activation, the person will be considered either dead or recovered
        from the infection.

        Args:
            simulator: The simulator object required to activate this event.
        """
        self.infection.person.infection_status = Infection_Status.CLEAN
        simulator.statistics.update_people_statistic(Health_Condition.IS_NOT_INFECTED, self.infection.person)

        if self.infection.will_die():
            self.infection.person.is_alive = False
            simulator.statistics.update_people_statistic(Health_Condition.DEAD, self.infection.person)

        simulator.disease_properties.clear_cache(self.infection.person)


class Virus_Spread_Event(Event):
    """This event handles the spread of the virus among people.

    The class provides a set of instructions to start the infection sequence,
    spread the disease among people, and to decide whether the disease can be
    transmitted between two people or not.

    """

    def activate(self, simulator: Simulator):
        """Activate the virus spread event.

        This function is used to initialize the virus spread event and
        start the infection sequence.

        Args:
            simulator (Simulator): The simulator object.
        """
        Virus_Spread_Event.activate_edges(simulator.people)

        new_infected_ids = Virus_Spread_Event.spread_disease(simulator)
        Infection.start_infections(new_infected_ids, simulator)

    @staticmethod
    def spread_disease(simulator: Simulator):
        """Check the disease transmission procedure for every edge in the graph.

        This method also determines who is getting infected in this session, and
        returns the id number of newly infected people.

        Args:
            simulator (Simulator): The simulator object.

        Returns:
            List[int]: The list of the newly infected people.

        """
        new_infected_ids = list()
        for person in simulator.people:
            if person.infection_status is Infection_Status.CONTAGIOUS:
                for edge in person.to_connection_edges:
                    if simulator.people[edge.to_id].infection_status is Infection_Status.CLEAN and \
                            Virus_Spread_Event.is_disease_transmitted(edge, simulator):

                        person.transmission_ids.append(edge.to_id)
                        new_infected_ids.append(edge.to_id)

        return list(set(new_infected_ids))

    @staticmethod
    def is_disease_transmitted(connection_edge: Connection_Edge, simulator: Simulator):
        """Check whether the disease is transmitted or not.

        Args:
            connection_edge (Connection_Edge): The connection edge between two people.
            simulator (Simulator): The simulator object.

        Returns:
            bool: True, if the disease is transmitted.
        """
        # return false if the edge between two people is not activated
        if not connection_edge.is_active():
            return False

        infected: Person = simulator.people[connection_edge.from_id]
        infecting: Person = simulator.people[connection_edge.to_id]

        infectious_rate_effect = simulator.disease_properties.generate_infectious_rate(simulator.clock,
                                                                                       infected,
                                                                                       simulator) \
                                 * simulator.disease_properties.generate_infectious_rate(simulator.clock,
                                                                                         infecting,
                                                                                         simulator)

        immunity_effect = (1 - simulator.disease_properties.generate_immunity(simulator.clock, infecting,
                                                                              simulator))

        infection_transmission_prob = infectious_rate_effect * \
                                      immunity_effect * \
                                      connection_edge.transmission_potential

        return Random.flip_coin(infection_transmission_prob)

    @staticmethod
    def activate_edges(people: List[Person]):
        """Activate all the connection edges for simulation people.

        Initialize every edge for all the people in the simulation. This enables
        people to interact with each other through the connection edges in the graph.

        Args:
            people (List[Person]): The simulator object.
        """
        for person in people:
            for edge in person.to_connection_edges:
                edge.initialize()
            for edge in person.from_connection_edges:
                edge.initialize()

        for person in people:
            if person.is_alive and person.current_location.is_family:
                for connection_edge in person.family.get_all_to_edges(person.id_number):
                    connection_edge.activate_from()
                for connection_edge in person.family.get_all_from_edges(person.id_number):
                    connection_edge.activate_to()
            elif person.is_alive:
                for connection_edge in \
                        person.current_location.community.get_all_to_edges(person.id_number,
                                                                           person.current_location.subcommunity_type_index):
                    connection_edge.activate_from()
                for connection_edge in \
                        person.current_location.community.get_all_from_edges(person.id_number,
                                                                             person.current_location.subcommunity_type_index):
                    connection_edge.activate_to()


class Transition_Event(Event):
    """This event handles the transition of a person to another place.

    The class determines the place that this person has to be moved in order
    to correctly fulfill his daily plan.

    Attributes
    ----------
    person (Person): The person that is going to transit using this event.
    community (Community): The community in which the transition takes place.
    subcommunity_type_index (int): Index of the destination sub-community.
    is_start (int): Whether this is a start transition or not.
    """

    def __init__(self, minute: int, event_type: Simulation_Event, person: Person, community: Community,
                 subcommunity_type_index: int, is_start: bool):
        """Initialize a transition event object.

        Args:
            minute (int): The total elapsed minutes that this event is going to happen.
            event_type (Simulation_Event): The type of this event is TRANSITION.
            person (Person): The person associated with this transition event.
            community (Community): The community of the person associated with this event.
            subcommunity_type_index (int): The sub-community type index of the person.
            is_start (bool): True, if this is the start transition.
        """
        super().__init__(minute, event_type)
        self.person = person
        self.community = community
        self.subcommunity_type_index = subcommunity_type_index
        self.is_start = is_start

    def activate(self, simulator: Simulator):
        """Activates the transition event, moving a person from one place to another.

        Args:
            simulator (Simulator): The main simulator object. Not required here.

        """
        if self.is_start:
            self.person.current_location = Place(self.person, self.community, self.subcommunity_type_index,
                                                 is_family=False)
        else:
            self.person.current_location = Place(self.person, community=None, subcommunity_type_index=None,
                                                 is_family=True)


class Plan_Day_Event(Event):
    """This event handles the daily planning of all the people involved in the simulation.

    The class is responsible for quarantining people as well as planning a daily event for
    people who are not quarantined. Moreover, this class provides tools to apply more complex
    quarantine conditions over communities and sub-communities.
    """

    def activate(self, simulator: Simulator):
        """Activate the plan day event object and determine the daily plan for
        every person in the simulation.

        The presence probability here is used to determine the current status of
        the person's community type role.

        The is_quarantine determines whether a person is quarantined or not. A
        quarantined person is not permitted to leave his home, so no daily plan
        is necessary in that case.

        Args:
            simulator (Simulator): The main simulator object. People and communities
            are extracted out of this object.
        """
        intervals = list()

        for person in simulator.people:
            if person.is_alive and not person.is_quarantined:
                person_intervals = list()

                for person_community, subcommunity_type_index in person.communities:
                    # calculate the presence probability
                    presence_probability = person_community.community_type. \
                        sub_community_types[subcommunity_type_index] \
                        .community_type_role.presence_prob

                    # check if the sub-community type is open
                    if not person_community.is_open(subcommunity_type_index):
                        presence_probability = 0

                    # check if the community is open
                    if not person_community.is_closed():
                        # flip a coin based on presence probability
                        if Random.flip_coin(presence_probability):
                            # set the start and end based on community type role
                            start, end \
                                = person_community.community_type.sub_community_types[subcommunity_type_index] \
                                .community_type_role.generate_time_cycle(simulator.clock)

                            # add the pre-interval minutes to the start and end
                            start += simulator.clock.get_minutes()
                            end += simulator.clock.get_minutes()

                            interval = Interval(person, start, end, person_community, subcommunity_type_index)
                            person_intervals.append(interval)

                person_intervals = Plan_Day_Event.resolve_intervals(person_intervals)
                intervals.extend(person_intervals)

        for interval in intervals:
            start_transition_event = Transition_Event(interval.start, Simulation_Event.TRANSITION,
                                                      interval.person, interval.community,
                                                      interval.subcommunity_type_index, True)
            heapq.heappush(simulator.events, start_transition_event)

            end_transition_event = Transition_Event(interval.end, Simulation_Event.TRANSITION,
                                                    interval.person, interval.community,
                                                    interval.subcommunity_type_index, False)
            heapq.heappush(simulator.events, end_transition_event)

    @staticmethod
    def resolve_intervals(intervals):
        temp = sorted(intervals, key=lambda x: (x.priority, x.end, x.end - x.start))
        designated_intervals = list()
        while len(temp) > 0:
            designated_intervals.append(temp[0])
            del temp[0]
            temp = [interval for interval in temp if not Interval.check_overlap(designated_intervals[-1], interval)]
        return designated_intervals


class Interval:
    """This class is employed whenever an interval is required.

    The interval is used to create an exact time bracket for the events, and to
    handle the priority of the items in the daily plan of each person.

    Attributes
    ----------
    person (Person): The person that is going to transit using this event.
    community (Community): The community in which the transition takes place.
    subcommunity_type_index (int): Index of the destination sub-community.
    self.start (int): The start of this interval in minutes.
    self.end (int): The end of this interval in minutes.
    self.priority (int): The priority of this interval.
    """

    def __init__(self, person: Person, start: int, end: int, community: Community,
                 subcommunity_type_index: int):
        """Initialize an interval object to hold the intervals in planning the daily events.

        Args:
            person (Person): The person that the interval is defined for.
            start (int): The start of this interval.
            end (int): The end time of the interval.
            community (Community): The community of the person.
            subcommunity_type_index (int): The index of sub-community type associated with this person.
        """
        self.person = person
        self.start = start
        self.end = end
        self.community = community
        self.subcommunity_type_index = subcommunity_type_index
        self.priority = community.community_type.sub_community_types[
            subcommunity_type_index].community_type_role.priority

    @staticmethod
    def check_overlap(interval1, interval2):
        """Check whether the two intervals overlap.

        Args:
            interval1: The first interval.
            interval2: The second interval.

        Returns:
            bool: True, if the intervals overlap.
        """
        if interval1.start <= interval2.start <= interval1.end or \
                interval2.start <= interval1.start <= interval2.end:
            return True
        return False

    @staticmethod
    def choose_superior(interval1, interval2):
        """Determine the superior interval.

        Args:
            interval1: The first interval.
            interval2: The second interval.

        Returns:
            Interval: The superior interval is returned.
        """
        if interval1.priority > interval2.priority:
            return interval1
        elif interval1.priority < interval2.priority:
            return interval2
        else:
            if interval1.start <= interval2.start:
                return interval1
            else:
                return interval2

    @staticmethod
    def choose_inferior(interval1, interval2):
        """Determine the inferior interval.

        Args:
            interval1: The first interval.
            interval2: The second interval.

        Returns:
            Interval: The inferior interval is returned.
        """
        if interval1.priority < interval2.priority:
            return interval1
        elif interval1.priority > interval2.priority:
            return interval2
        else:
            if interval1.start > interval2.start:
                return interval1
            else:
                return interval2


if __name__ == '__main__':
    from json_handle import Parser

    simulator = Parser('test').parse_simulator()
    end_time, spread_period, initialized_infected_ids, commands, observers = \
        Parser('test').parse_simulator_data()

    simulator.generate_model()
    simulator.save_model('test')

    simulator.simulate(Time(delta_time=timedelta(days=60),
                            init_date_time=datetime.now()),
                       spread_period,
                       initialized_infected_ids,
                       commands,
                       observers,
                       report_statistics=2)

    observers[0].plot_disease_statistics_during_time(Health_Condition.IS_INFECTED)

