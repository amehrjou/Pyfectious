import heapq
import sys
import types
from multiprocessing import Pool, Lock
from typing import List, Dict, Tuple

from tqdm.auto import tqdm

from distance import Distance
from distributions import Two_Variate_iid_Uniform_Distribution, Truncated_Normal_Distribution, \
    Normal_Distribution, Uniform_Distribution, Bernoulli_Distribution, \
    UniformSet_Distribution, Uniform_Whole_Week_Time_Cycle_Distribution, \
    Random, Distribution, Two_Variate_Distribution, Time_Cycle_Distribution
from logging_settings import logger
from time_handle import Time
# Initialize a multiprocessing lock
from utils import Infection_Status

lock = Lock()


class Person:
    """A class used to represent a single person.

    This class also contains general and statistical information about each individual,
    and these information are filled in the population generation process.

    Attributes
    ----------
    id_number (int): An identification number.
    age (int): Age of the person.

    health_condition (float): A float number between 0 and 1 used to represent medical
    history i.e. effective illnesses e.g. Diabetes and Asthma.

    gender (int): Gender of the person indicated by a number (0 --> Female, 1 --> Male).
    family (Family): Person's family object.
    communities (List[(Community, int)]): A list containing person's communities
    and the index of the sub_community for each community.

    to_connection_edges(List[Connection_Edge]): A list containing connection edges
    from this person to others.

    from_connection_edges (List[Connection_Edge]): A list containing connection edges
    from others to this person.

    infection_status (bool): Current situation of the person in terms of being infected. A
    person can be CLEAN, infected but still in INCUBATION period, and CONTAGIOUS.

    current_location (Place): Current location of the person, whether in some
    community or family.

    is_alive (bool): A boolean that indicates if the person is alive or dead.
    has_profession (bool): A boolean representing whether the person has a career
    or not.

    times_of_infection (int): An integer, saving the number of time this person has
    been infected by far.

    is_quarantined (bool): A boolean showing quarantine situation of this person.
    roles (List[Str]): The name of the roles of this person.

    transmission_ids (List[int]): The id number of people infected by this person.
    """

    def __init__(self, id_number: int, age: int, health_condition: float, gender: int, family):
        """Initialize the person object, and connection dictionaries.

        Args:
            id_number (int): An identification number.
            age (int): Person's age.
            health_condition (float): Health condition of the person.
            gender (int): Gender of the person. 0 refers to female, 1 refers to male.
            family (Family): Person's family object.
        """
        self.id_number = id_number
        self.age = age
        self.health_condition = health_condition
        self.gender = gender
        self.family = family

        self.communities = list()
        self.to_connection_edges: List[Connection_Edge] = list()
        self.from_connection_edges: List[Connection_Edge] = list()

        self.infection_status = Infection_Status.CLEAN
        self.current_location: Place or None = None

        self.is_alive = True
        self.has_profession = False
        self.times_of_infection = 0
        self.is_quarantined = False

        self.roles = list()
        self.transmission_ids = list()

    def get_current_location(self) -> Tuple[float, float]:
        """Returns current location of the person in terms of cartesian coordinates.

        Returns:
            Tuple[float, float]: The location tuple.
        """
        return self.current_location.get_location()

    def add_to_connection_edge(self, to_id):
        """Add a directional connection edge from this person to another
        person with to_id as id_number.

        Args:
            to_id (int): The id of a person connection edge goes to.

        Returns:
            Connection_Edge: The modified connection edge.
        """
        connection_edge = Connection_Edge(self.id_number, to_id)
        self.to_connection_edges.append(connection_edge)
        return connection_edge

    def add_from_connection_edge(self, from_id):
        """Add a directional connection edge to this person from another
        person with from_id as id_number.

        Args:
            from_id (int): The id of a person connection edge comes from.

        Returns:
            Connection_Edge: The modified connection edge.
        """
        connection_edge = Connection_Edge(from_id, self.id_number)
        self.from_connection_edges.append(connection_edge)
        return connection_edge

    def add_bidirectional_connection_edge(self, other_id):
        """Add a bidirectional connection edge between this person and
        another person with from as id_number.

        Args:
            other_id (int): The id of the other person.

        Returns:
            Connection_Edge: The modified connection edge.
        """
        connection_edges = list()
        connection_edges.append(self.add_from_connection_edge(other_id))
        connection_edges.append(self.add_to_connection_edge(other_id))
        return connection_edges

    def initialize(self):
        """Initialize connection edges and location of the person.
        """
        self.current_location = Place(self, None, None, is_family=True)
        self.is_quarantined = False
        for connection_edge in self.from_connection_edges:
            connection_edge.inactivate_from()
            connection_edge.unquarantine_from()
        for connection_edge in self.to_connection_edges:
            connection_edge.inactivate_to()
            connection_edge.unquarantine_to()

    def get_all_connection_edges(self):
        """Get all the connection edges coming to or leaving this person.

        Returns:
            List[Connection_Edge]: The list of all connection edges.
        """
        return self.to_connection_edges + self.from_connection_edges

    def get_to_connection_edges(self):
        """Get the connection edges to this person.

        Returns:
            List[Connection_Edge]: The list of the desired connection edges.
        """
        return self.to_connection_edges

    def get_from_connection_edges(self):
        """Get the connection edges from this person.

        Returns:
            List[Connection_Edge]: The list of the desired connection edges.
        """
        return self.from_connection_edges

    def quarantine(self):
        """Quarantine the current person.
        """
        self.is_quarantined = True
        for edge in self.get_to_connection_edges():
            edge.quarantine_from()
        for edge in self.get_from_connection_edges():
            edge.quarantine_to()

    def unquarantine(self):
        """Unquarantine the current person.
        """
        self.is_quarantined = False
        for edge in self.get_to_connection_edges():
            edge.unquarantine_from()
        for edge in self.get_from_connection_edges():
            edge.unquarantine_to()

    def has_role(self, role_name: str) -> bool:
        """Returns true if the person has the given role in his schedule.

        Args:
            role_name (str): The specified community type role name, e.g., Teacher.

        Returns:
            bool: True if person has this role.
        """
        if role_name in self.roles:
            return True
        return False

    def add_community(self, community, sub_community_index: int):
        """Add a community to the person's communities list.

        Args:
            community (Community): The community to be added.
            sub_community_index (int): The sub-community index that the person belongs to.
        """
        self.communities.append((community, sub_community_index))
        self.roles.append(community.community_type.sub_community_types[sub_community_index].name)

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(id_number=self.id_number,
                    age=self.age,
                    health_condition=self.health_condition,
                    gender=self.gender,
                    family=self.family)


class Family_Pattern:
    """A class used to represent a pattern common among families.

    ...

    Attributes
    ----------
    number_of_members (int): Number of members in this family pattern.
    age_distributions (List[Distribution]): A list containing age distributions of
    the members of this pattern

    health_condition_distributions (List[Distribution]): A list containing health
    condition distributions of the members of this pattern

    genders (List[int]): A list containing genders of the members of this pattern.
    location_distribution (Two_Variate_Distribution): A two variate joint distribution
    indicating location distribution of this pattern

    """

    def __init__(self, number_of_members, age_distributions: List[Distribution],
                 health_condition_distributions: List[Distribution],
                 genders: List[int], location_distribution: Two_Variate_Distribution):
        """Initialize a Family Pattern object.

        Args:
            number_of_members (int): Number of members living in this family.
            age_distributions (List[Distribution]): The age distribution for each member.
            health_condition_distributions (List[Distribution]): Health condition distribution
            for each member of the family.

            genders (List[int]): A list indicating the gender of the people living in the family.
            location_distribution (Two_Variate_Distribution): Location distribution of the family.
        """
        self.number_of_members = number_of_members
        self.age_distributions = age_distributions
        self.health_condition_distributions = health_condition_distributions
        self.genders = genders
        self.location_distribution: Two_Variate_Distribution = location_distribution

    def is_pattern_satisfied(self, ages: List[int], health_conditions: List[float],
                             genders: List[int]) -> bool:
        """Returns whether the pattern is satisfied with given parameter
        distributions or not.

        Args:
            ages (List[int]): A list of ages in the family.
            health_conditions (List[float]): A list containing the health condition of
            people in the family.

            genders (int): A list containing the genders of this family.

        Returns:
            bool: True, if the given data satisfies the current pattern.
        """
        for age_distribution, age in zip(self.age_distributions, ages):
            if age_distribution.reject_sample(age):
                return False

        for health_condition_distribution, health_condition in zip(self.health_condition_distributions,
                                                                   health_conditions):
            if health_condition_distribution.reject_sample(health_condition):
                return False

        for pattern_gender, gender in zip(self.genders, genders):
            if pattern_gender != gender:
                return False

        return True

    def generate_location(self):
        """Generate the location of this family.

        Returns:
            Tuple: The sampled location.
        """
        return self.location_distribution.sample_single_random_variable()

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        # use int() since int32 cannot be JSON serialized
        return dict(name=self.__class__.__name__,
                    number_of_members=int(self.number_of_members),
                    age_distributions=self.age_distributions,
                    health_condition_distributions=self.health_condition_distributions,
                    genders=self.genders,
                    location_distribution=self.location_distribution)

    @staticmethod
    def sample_person(id_number, family, age_distribution, health_condition_distribution, gender):
        """Sample a person from a family.

        Args:
            id_number (int): Person's id number.
            family (Family): Person's family object.
            age_distribution (Distribution): The age distribution of the person.
            health_condition_distribution (Distribution): The health condition distribution
            of the person.

            gender (int): The gender of the person.

        Returns:
            Person: The sampled person.
        """
        person = Person(id_number, age_distribution.sample_single_random_variable()
                        , health_condition_distribution.sample_single_random_variable(), gender, family)
        return person

    def generate_family_members(self, family, people_ids):
        """Returns the people associated with this family pattern.

        Args:
            family (Family): The target family.
            people_ids (List[int]): The list of people's ids.

        Returns:
            List[Person]: The family members.
        """
        people = list()
        for person_id, age_distribution, health_condition_distribution, gender in \
                zip(people_ids, self.age_distributions, self.health_condition_distributions, self.genders):
            people.append(Family_Pattern.sample_person(person_id
                                                       , family
                                                       , age_distribution
                                                       , health_condition_distribution
                                                       , gender))
        return people


class Family:
    """A class used to represent a family.

    ...

    Attributes
    ----------
    id_number (int): An identification number.
    people_ids (List[int]): A list consists of id number of the
    members of this family.

    size (int): Number of the members of this family.
    to_connection_edges (Dict[Connection_Edge]): A dictionary containing
    connection edges from members of this family to others(key: person id).

    from_connection_edges (Dict[Connection_Edge]): A dictionary containing
    connection edges from others to members of this family(key: person id).

    family_pattern (Family_Pattern): Pattern of this family.
    location (Tuple[float, float]): Cartesian location of this family.
    is_quarantined (bool): A boolean showing quarantine situation of this person.

    """

    def __init__(self, id_number: int, people_ids: List[int], family_pattern: Family_Pattern):
        """Initialize a Family object.

        Args:
            id_number (int): ID number of the family.
            people_ids (List[int]): The ids of members of this family.
            family_pattern (Family_Pattern): The pattern of this family.
        """
        self.id_number = id_number
        self.people_ids = people_ids
        self.size = len(people_ids)
        self.to_connection_edges = {i: [] for i in people_ids}
        self.from_connection_edges = {i: [] for i in people_ids}
        self.family_pattern = family_pattern
        self.location = family_pattern.generate_location()
        self.is_quarantined = False

    def construct_graph(self, graph, people):
        """Construct the graph of this family.

        Args:
            graph (Dict): The input graph.
            people (List[Person]): The people of the family.

        Returns:
            Dict: The family graph.
        """
        people.extend(self.family_pattern.generate_family_members(self, self.people_ids))
        for i in self.people_ids:
            for j in self.people_ids:
                if i != j:
                    graph[i].append(j)
                    people[j].add_from_connection_edge(i)
                    connection_edge = people[i].add_to_connection_edge(j)
                    self.to_connection_edges[i].append(connection_edge)
                    self.from_connection_edges[j].append(connection_edge)
            graph[i] = list(set(graph[i]))
        return graph

    def get_all_connection_edges(self):
        """Get all the connection edges coming to or leaving this family.

        Returns:
            List[Connection_Edge]: The list of all connection edges.
        """
        connection_edges = list()
        for edge_list in self.to_connection_edges.values():
            connection_edges.extend(edge_list)
        return list(set(connection_edges))

    def get_all_to_edges(self, person_id):
        """Get the connection edges to this family.

        Returns:
            List[Connection_Edge]: The list of the desired connection edges.
        """
        return list(set(self.to_connection_edges[person_id]))

    def get_all_from_edges(self, person_id):
        """Get the connection edges from this family.

        Returns:
            List[Connection_Edge]: The list of the desired connection edges.
        """
        return list(set(self.from_connection_edges[person_id]))

    def quarantine(self, people: List[Person]):
        """Quarantine the current family.
        """
        self.is_quarantined = True

        for person in people:
            if person.id_number in self.people_ids:
                person.quarantine()

    def unquarantine(self, people: List[Person]):
        """Unquarantine the current family.
        """
        self.is_quarantined = False

        for person in people:
            if person.id_number in self.people_ids:
                person.unquarantine()

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(id_number=self.id_number,
                    people_ids=self.people_ids,
                    family_pattern=self.family_pattern)


class Connection_Edge:
    """A class used to represent a connection edge.

    This class describes a connection edge between two people being
    used to spread the disease from from_id to to_id i the graph.

    Attributes
    ----------
    from_id (int): Id_number of the from side of this edge.
    to_id (int): Id_number of the to side of this edge.
    from_is_available (bool): A boolean represent whether the from
    side is in the place of this edge.

    to_is_available (bool): A boolean represent whether the to side
    is in the place of this edge.

    from_is_quarantined (bool): A boolean represent whether the from
    side is quarantined.

    to_is_quarantined (bool): A boolean represent whether the to
    side is quarantined.

    transmission_potential (float, optional): An argument indicating the
    potential of transmission that this connection edge is capable of.

    """

    def __init__(self, from_id: int, to_id: int, transmission_potential: float = 1):
        """Initialize a connection edge object.

        Args:
            from_id (int): The id of the beginning of the edge.
            to_id (int): The id of the end of the edge.
        """
        self.from_id = from_id
        self.to_id = to_id
        self.from_is_available = False
        self.to_is_available = False
        self.from_is_quarantined = False
        self.to_is_quarantined = False
        self.transmission_potential = transmission_potential

    def initialize(self):
        """Initialize the connection edge availability to default values.
        """
        self.from_is_available = False
        self.to_is_available = False

    def activate_from(self):
        """Activate the from side of the edge.
        """
        self.from_is_available = True

    def inactivate_from(self):
        """Inactivate the from side of the edge.
        """
        self.from_is_available = False

    def activate_to(self):
        self.to_is_available = True

    def inactivate_to(self):
        """Inactivate the to side of the connection edge.
        """
        self.to_is_available = False

    def quarantine_from(self):
        """Quarantine the from side of the edge.
        """
        self.from_is_quarantined = True

    def unquarantine_from(self):
        """Unquarantine the from side of the edge.
        """
        self.from_is_quarantined = False

    def quarantine_to(self):
        """Quarantine the to side of the edge.
        """
        self.to_is_quarantined = True

    def unquarantine_to(self):
        """Unquarantine the to side of the edge.
        """
        self.to_is_quarantined = False

    def is_active(self):
        """Check whether the edge is active.

        Returns:
            bool: True, if the edge is active.
        """
        return self.from_is_available and self.to_is_available \
               and not self.from_is_quarantined and not self.to_is_quarantined

    def set_transmission_potential(self, transmission_potential):
        """Set the transmission potential of this connection edge.
        """
        self.transmission_potential = transmission_potential


class Community_Type_Role:
    """A class used to represent the people's role.

    This class constructs the role that each person in the corresponding sub_community has.
    It also contains the distributions needed for sampling people for the corresponding
    sub_community.

    Attributes
    ----------
    age_distribution (Distribution): Age distribution of the people having this role.
    gender_distribution (Distribution): Gender distribution of the people having this role.

    time_cycle_distribution (Time_Cycle_Distribution): Time cycle distribution of the people
    having this role. each plan day event use this distribution to sample a time cycle related
     to this role for each person separately.

    is_profession (bool): Indicates if this role is a career.
    priority (int): Priority of the intervals generated by this role to be used to resolve
    conflict between intervals; note that the less this value is, the more priority this role has.

    presence_prob (float): Probability of being present in this community, initiating with one,
    it changes whenever the work space is subject to governmental restrictions or other
    environmental conditions.

    """

    def __init__(self, age_distribution: Distribution, gender_distribution: Distribution
                 , time_cycle_distribution: Time_Cycle_Distribution, is_profession: bool, priority: int):
        self.age_distribution = age_distribution
        self.gender_distribution = gender_distribution
        self.time_cycle_distribution = time_cycle_distribution
        self.is_profession = is_profession
        self.priority = priority  # priority is decreasing
        self.presence_prob = 1.0

    def generate_time_cycle(self, current_time: Time):
        """Generate a time cycle for this role to be used for a person.

        Args:
            current_time (Time): The current time.

        Returns:
            int, int: The start and the end of the time cycle.
        """
        start, length = self.time_cycle_distribution.sample_single_random_variable(current_time)
        end = start + length
        return start, end

    def accept_sample(self, person: Person) -> bool:
        """Indicates if this person fits to this role based on reject sampling
        of this role distributions.

        Args:
            person (Person): Whether this role accepts this person or not.

        Returns:
            bool: True, if the person can have the role.
        """
        lock.acquire()
        result = self.age_distribution.accept_sample(person.age) and \
                 self.gender_distribution.accept_sample(person.gender) and \
                 not (person.has_profession and self.is_profession)
        lock.release()

        return result

    def get_likelihood_person_given_role(self, person: Person) -> float:
        """Returns likelihood probability of the person given this role.

        Args:
            person (Person): The person that is checked for the likelihood.

        Returns:
            float: The likelihood of the person having the role.
        """
        lock.acquire()
        profession = person.has_profession and self.is_profession
        lock.release()

        if not profession:
            return self.age_distribution.pdf(person.age) * self.gender_distribution.pdf(person.gender)
        else:
            return 0

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    age_distribution=self.age_distribution,
                    gender_distribution=self.gender_distribution,
                    time_cycle_distribution=self.time_cycle_distribution,
                    is_profession=self.is_profession,
                    priority=self.priority)


class Sub_Community_Type:
    """A class used to represent a sub_community_type.

    This class is used to generate a subcommunity; note that each community
    consists of a set of sub_communities, e.g., a school comprises the sub
    community of teachers and students.

    Attributes
    ----------
    community_type_role (Community_Type_Role): Role of the people in this sub_community_type.

    number_of_members_distribution (Distribution): A distribution used to generate a number as
    number of the members each time this kind of sub_community_type is generated.

    connectivity_distribution (Distribution): A distribution used to generate a number between
    0 and 1 as connectivity probability each time this kind of sub_community_type is generated,
    note that connectivity is the probability of existence of any edge within this sub_community.

    transmission_potential_distribution (Distribution): A distribution indicating the potential of
    disease being transmitted among the individuals in this sub-community.

    name (str): The name of the sub-community.
    """

    def __init__(self, community_type_role: Community_Type_Role, name: str,
                 number_of_members_distribution: Distribution,
                 connectivity_distribution: Distribution,
                 transmission_potential_distribution: Distribution):
        """Initialize a sub community type object.

        Args:
            community_type_role (Community_Type_Role): The type of role associated
            with this community.

            number_of_members_distribution (Distribution): Distribution of the sub
            community size.

            connectivity_distribution (Distribution): Distribution of the sub community
            connectivity.
        """
        self.community_type_role = community_type_role
        self.name = name
        self.number_of_members_distribution = number_of_members_distribution
        self.connectivity_distribution = connectivity_distribution
        self.transmission_potential_distribution = transmission_potential_distribution

    def generate_number_of_members(self):
        """Generate the number of members based on the distribution.

        Returns:
            int: The number of members.
        """
        return int(self.number_of_members_distribution.sample_single_random_variable())

    def generate_transmission_potential(self):
        """Generate the transmission potential based on the distribution.

        Returns:
            int: A single transmission potential sample.
        """
        return self.transmission_potential_distribution.sample_single_random_variable()

    def generate_connectivity(self):
        """Generate the connectivity based on the distribution.

        Generate connectivity probability, note that connectivity is the probability of
        existence of any edge within the sub_community going to be generated.

        Returns:
            int: A single connectivity sample.
        """
        return self.connectivity_distribution.sample_single_random_variable()

    def calculate_likelihood_people_given_sub_community_type(self, people: List[Person], community_location
                                                             , distance_function):
        """Calculate the likelihood probability for all the people multiplied by
        the distance of each person calculated by distance_function.

        Args:
            people (List[Person]): The people for whom the likelihood is calculated.
            community_location (Tuple): The location tuple of the community.
            distance_function (Function): The distance function to calculate the distance.

        Returns:
            List: A list of likelihoods.
        """
        likelihood = list()
        for person in people:
            distance = distance_function(person.family.location, community_location)
            temp = (self.community_type_role.get_likelihood_person_given_role(person)
                    * distance, person.id_number)
            likelihood.append(temp)
        return likelihood

    def sample_sub_community(self, people, number_of_members, community_location, distance_function) -> List[int]:
        """Returns list of indices of designated people for a sample of this
        sub_community type, using maximum of posterior probability to sample its members.

        Args:
            people (List[Person]): The people to sample from.
            number_of_members (int): Number of members in the community.
            community_location (Tuple): The community location tuple.
            distance_function (Function): The distance function to calculate the likelihood.

        Returns:
            List[int]: The list of sampled people.
        """
        designated_people_ids = heapq.nlargest(number_of_members,
                                               self.calculate_likelihood_people_given_sub_community_type(people,
                                                                                                         community_location,
                                                                                                         distance_function))

        # check whether the role is a profession
        if self.community_type_role.is_profession:
            for id in designated_people_ids:
                lock.acquire()
                people[id[1]].has_profession = True
                lock.release()

        return list(list(zip(*designated_people_ids))[1])

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    community_type_role=self.community_type_role,
                    number_of_members_distribution=self.number_of_members_distribution,
                    connectivity_distribution=self.connectivity_distribution,
                    sub_community_name=self.name,
                    transmission_potential_distribution=self.transmission_potential_distribution)


class Community_Type:
    """A class used to represent a community type to be used to generate communities.


    Attributes
    ----------

    sub_community_types (List[Sub_Community_Type]): A list containing the sub_community_types
    in this community type.

    name (str): A string as the name of this community type.

    number_of_communities (int): An integer indicating the number of this community_type
    to be generated.

    sub_community_connectivity_dict (Dict[int, Dict[int, Distribution]]): A dictionary containing
    the connectivity distribution of inter-sub_community edges, first and second indices are from
    and to sides of these edges

    location_distribution (Two_Variate_Distribution): A two variate joint distribution indicating
    location distribution of this type.

    transmission_potential_dict (Dict[int, Dict[int, Distribution]]): The potential of disease
    being transmitted between the sub communities in this type of community.
    """

    def __init__(self, sub_community_types: List[Sub_Community_Type], name: str, number_of_communities: int
                 , sub_community_connectivity_dict: Dict[int, Dict[int, Distribution]]
                 , location_distribution: Two_Variate_Distribution
                 , transmission_potential_dict: Dict[int, Dict[int, Distribution]]):
        """Initialize a community type object.

        Args:
            sub_community_types (List[Sub_Community_Type]): A list of sub community types.
            name (str): The name of the community type.
            number_of_communities (int): Number of this community.

            sub_community_connectivity_dict (Dict[int, Dict[int, Distribution]]): A dictionary
            representing the connectivity of sub-communities within this community.

            location_distribution (Two_Variate_Distribution): The location distribution of the community.

            transmission_potential_dict (Dict[int, Dict[int, Distribution]]): The potential of disease
            being transmitted among sub-communities in this type of community.
        """
        self.sub_community_types = sub_community_types
        self.sub_community_connectivity_dict = sub_community_connectivity_dict
        self.number_of_communities = number_of_communities
        self.name = name
        self.location_distribution = location_distribution
        self.transmission_potential_dict = transmission_potential_dict

    def generate_transmission_potential(self, first_community_id: int,
                                        second_community_id: int) -> float:
        """Generate a transmission potential sample based on the transmission potential
        dictionary.

        Args:
            first_community_id (int): The first sub-community id.
            second_community_id (int): The second sub-community id.

        Returns:
            float:
        """
        return self.transmission_potential_dict[first_community_id][second_community_id] \
            .sample_single_random_variable()

    def generate_community_setting(self):
        """Generates inter and intra sub_community connectivity settings. Showing the connection
        settings within and between the sub-communities.

        Returns:
            Dict, Dict: Inter and intra community connectivity dictionaries.
        """
        intracommunity_setting_dict = {}
        for i, sub_community_type in enumerate(self.sub_community_types):
            connectivity = sub_community_type.generate_connectivity()
            number_of_members = sub_community_type.generate_number_of_members()
            intracommunity_setting_dict[i] = (connectivity, number_of_members)

        intercommunity_connectivity_dict = {}
        for i1, sub_community_type1 in enumerate(self.sub_community_types):
            intercommunity_connectivity_dict[i1] = {}
            for i2, sub_community_type2 in enumerate(self.sub_community_types):
                if sub_community_type1 != sub_community_type2:
                    connectivity = self.sub_community_connectivity_dict[i1][i2].sample_single_random_variable()
                    intercommunity_connectivity_dict[i1][i2] = connectivity

        return intracommunity_setting_dict, intercommunity_connectivity_dict

    def create_community(self, id_number, graph, people, distance_function):
        """Generates a sample community of this community_type using maximum of
        posterior probability.

        Args:
            id_number (int): The id_number of this community.
            graph (Dict): The graph of communities.
            people (List[Person]): The people that communities are created from.
            distance_function (Function): The distance function.

        Returns:
            Community: The constructed community.
        """
        # generate community settings
        intracommunity_setting_dict, intercommunity_connectivity_dict = self.generate_community_setting()
        people_ids_dict = {}

        # sample a location based on self location distribution
        location = self.location_distribution.sample_single_random_variable()
        for i, sub_community_type in enumerate(self.sub_community_types):
            people_ids_dict[i] = sub_community_type.sample_sub_community(people,
                                                                         intracommunity_setting_dict[i][1],
                                                                         location, distance_function)

        # build the community object
        community = Community(id_number, self, people_ids_dict,
                              intracommunity_setting_dict,
                              intercommunity_connectivity_dict,
                              location)

        # construct the community graph
        community.construct_graph(graph, people)
        return community

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    sub_community_types=self.sub_community_types,
                    sub_community_connectivity_dict=self.sub_community_connectivity_dict,
                    number_of_communities=self.number_of_communities,
                    community_name=self.name,
                    location_distribution=self.location_distribution,
                    transmission_potential_dict=self.transmission_potential_dict)


class Community:
    """A class used to represent a community.

    ...

    Attributes
    ----------

    id_number (int): An identification number.
    community_type (Community_Type): Community_type of this community.

    people_ids_dict (Dict[int, List[int]]): A dictionary containing people id number of this
    community, representing by sub_community_type indices as keys of the dictionary.

    intracommunity_setting_dict (Dict[int, Tuple[int, float]]): A dictionary containing
    tuples(first number of sub_community members, second the connectivity of intra-sub_community
    edges), keys of the dictionary are sub_community_type indices.

    intercommunity_connectivity_dict (Dict[int, Dict[int, float]]): A dictionary containing the
    connectivity of inter-sub_community edges, first and second indices are from
    and to sides of these edges.

    location (Tuple[float, float]): Cartesian location of this community.

    """

    def __init__(self, id_number, community_type, people_ids_dict: Dict[int, List[int]],
                 intracommunity_setting_dict: Dict[int, Tuple[int, float]],
                 intercommunity_connectivity_dict: Dict[int, Dict[int, float]],
                 location: Tuple):
        """Initialize a community object.

        Args:
            id_number (int): The community id.
            community_type (Community_Type): The type of the community.

            people_ids_dict (Dict[int, List[int]]): A dictionary containing people id number
            of this community.

            intracommunity_setting_dict (Dict[int, Tuple[int, float]]): A dictionary containing tuples(
            first number of sub-community members, second the connectivity of intra-sub_community
            edges), keys of the dictionary are sub_community_type indices.

            intercommunity_connectivity_dict (Dict[int, Dict[int, float]]): A dictionary containing the
            connectivity of inter-sub-community edges, first and second indices are from
            and to sides of these edges.

            location (Tuple): The location tuple.
        """
        self.id_number = id_number
        self.community_type = community_type
        self.people_ids_dict = people_ids_dict
        self.people_ids = []
        for ids in people_ids_dict.values():
            self.people_ids.extend(ids)
        self.size = len(self.people_ids)
        self.to_connection_edges = {(i, j): [] for i in self.people_ids for j in
                                    range(len(self.community_type.sub_community_types))}
        self.from_connection_edges = {(i, j): [] for i in self.people_ids for j in
                                      range(len(self.community_type.sub_community_types))}
        self.intracommunity_setting_dict = intracommunity_setting_dict
        self.intercommunity_connectivity_dict = intercommunity_connectivity_dict
        self.intracommunity_edges_dict = {i: [] for i, sub_community_type in
                                          enumerate(self.community_type.sub_community_types)}
        self.intercommunity_edges_dict = {
            i1: {i2: [] for i2, sub_community_type2 in enumerate(self.community_type.sub_community_types)}
            for i1, sub_community_type1 in enumerate(self.community_type.sub_community_types)}
        self.location = location
        self.status = [True for _ in range(len(self.community_type.sub_community_types))]  # Results in Plan Day Event

    def construct_graph(self, graph, people):
        """Constructs graph of this community by adding related connection edges.

        The function also appends the community to the related person's communities
        list.

        Args:
            graph (Dict): The community graph.
            people (List[Person]): The people of the simulation.

        Returns:
            Dict: The constructed graph.
        """
        for index, sub_community_type in enumerate(self.community_type.sub_community_types):
            people_ids = self.people_ids_dict[index]
            connectivity = self.intracommunity_setting_dict[index][1]

            for i in people_ids:
                for j in people_ids:
                    if i != j and Random.flip_coin(connectivity):
                        graph[i].append(j)
                        people[j].add_from_connection_edge(i)
                        connection_edge = people[i].add_to_connection_edge(j)

                        potential = sub_community_type.generate_transmission_potential()
                        connection_edge.set_transmission_potential(potential)

                        self.to_connection_edges[(i, index)].append(connection_edge)
                        self.from_connection_edges[(j, index)].append(connection_edge)
                        self.intracommunity_edges_dict[index].append(connection_edge)

                # add the created community to the corresponding person
                people[i].add_community(self, index)

                # update the graph
                graph[i] = list(set(graph[i]))

        for index1, _ in enumerate(self.community_type.sub_community_types):
            for index2, _ in enumerate(self.community_type.sub_community_types):
                if index1 != index2:
                    people_ids1 = self.people_ids_dict[index1]
                    people_ids2 = self.people_ids_dict[index2]
                    connectivity = self.intercommunity_connectivity_dict[index1][index2]

                    for i in people_ids1:
                        for j in people_ids2:
                            if i != j and Random.flip_coin(connectivity):
                                graph[i].append(j)
                                people[j].add_from_connection_edge(i)
                                connection_edge = people[i].add_to_connection_edge(j)

                                potential = \
                                    self.community_type.generate_transmission_potential(first_community_id=index1,
                                                                                        second_community_id=index2)
                                connection_edge.set_transmission_potential(potential)

                                self.to_connection_edges[(i, index1)].append(connection_edge)
                                self.from_connection_edges[(j, index2)].append(connection_edge)
                                self.intercommunity_edges_dict[index1][index2].append(connection_edge)

                        graph[i] = list(set(graph[i]))

        return graph

    def get_all_to_edges(self, person_id: int, subcommunity_type_index: int):
        """Returns all connection edges in the given subcommunity from person_id to others
        in this community.

        Args:
            person_id (int): The person id.
            subcommunity_type_index (int): The target sub community.

        Returns:
            List[Connection_Edge]: A list of all to connection edges.
        """
        return self.to_connection_edges[(person_id, subcommunity_type_index)]

    def get_all_from_edges(self, person_id: int, subcommunity_type_index: int):
        """Returns all connection edges in the given subcommunity to person_id from others
        in this community.

        Args:
            person_id (int): The person id.
            subcommunity_type_index (int): The target sub community.

        Returns:
            List[Connection_Edge]: A list of all from connection edges.
        """
        return self.from_connection_edges[(person_id, subcommunity_type_index)]

    def get_all_connection_edges(self) -> List[Connection_Edge]:
        """Returns all connection edges in this community.

        Returns:
            List[Connection_Edge]: A list of all connection edges
        """
        connection_edges = list()
        for edge_list in self.to_connection_edges.values():
            connection_edges.extend(edge_list)
        return connection_edges

    def quarantine(self):
        """Quarantine the whole community.
        """
        self.status = [False for _ in range(len(self.community_type.sub_community_types))]

    def unquarantine(self):
        """Unquarantine the whole community.
        """
        self.status = [True for _ in range(len(self.community_type.sub_community_types))]

    def quarantine_subcommunity(self, subcommunity_type_index):
        """Quarantine the given sub_community.

        Args:
            subcommunity_type_index ([type]): Index of the sub community to be quarantined.
        """
        self.status[subcommunity_type_index] = False

    def unquarantine_subcommunity(self, subcommunity_type_index):
        """Unquarantine the given sub_community.

        Args:
            subcommunity_type_index ([type]): Index of the sub community to be unquarantined.
        """
        self.status[subcommunity_type_index] = True

    def is_closed(self):
        """Indicates whether the whole community is closed or not.

        Returns:
            bool: True, if the community is entirely closed.
        """
        for status in self.status:
            if status:
                return False
        return True

    def is_open(self, subcommunity_type_index: int = None):
        """Indicates if the given sub_community is open.

        Args:
            subcommunity_type_index (int): The index of subcommunity type.

        Returns:
            bool: True, if it is open.
        """
        return self.status[subcommunity_type_index]

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    id_number=self.id_number,
                    community_type=self.community_type,
                    people_ids_dict=self.people_ids_dict,
                    intracommunity_setting_dict={x: (y[0], float(y[1])) for x, y in
                                                 self.intracommunity_setting_dict.items()},
                    intercommunity_connectivity_dict=self.intercommunity_connectivity_dict,
                    location=self.location)


class Place:
    """A class used to represent place that can be near his/her family or some community.

    Attributes
    ----------
    person (Person): The person this place represent its location.
    community (Community): Community if the mentioned person is in the community.

    subcommunity_type_index (int): Index of the sub_community this person is in if
    the mentioned person is in the community.

    is_family (bool): Whether the mention person is near his/her family.
    """

    def __init__(self, person: Person, community: Community or None, subcommunity_type_index: int or None,
                 is_family: bool):
        """Initialize a place object.

        Args:
            person (Person): Person associated with this place.
            community (Community or None): Community if the mentioned person is in the community.
            subcommunity_type_index (int or None): Index of the sub_community this person is in.
            is_family (bool): Whether the mention person is near his/her family.
        """
        self.person = person
        self.community = community
        self.subcommunity_type_index = subcommunity_type_index
        self.is_family = is_family

    def get_location(self) -> Tuple[float, float]:
        """Returns current location of the person in terms of cartesian coordinates.

        Note that this function translate the place person is in to cartesian coordinates.

        Returns:
            Tuple[float, float]: The location of this place.
        """
        noise_x, noise_y = Place.generate_random_location_noise()
        if self.is_family:
            return self.person.family.location[0] + noise_x, self.person.family.location[1] + noise_y
        else:
            return self.community.location[0] + noise_x, self.community.location[1] + noise_y

    @staticmethod
    def generate_random_location_noise():
        """Generate a random noise for location.

        Returns:
            float, float: Noise for x and y.
        """
        params = {
            "mu": 1,
            "sigma": 1
        }
        noise_x = Normal_Distribution(params).sample_single_random_variable()
        noise_y = Normal_Distribution(params).sample_single_random_variable()
        return noise_x, noise_y


class Population_Generator:
    """A class used to generate a population with given setting.

    Given the family patterns and community types, the population generator class creates
    a society and assigns the number of people indicated in population size to the families,
    and then to the communities.

    Note: People get their specifications by being assigned to a family pattern, based on
    the probability indicated in the family pattern probability dictionary. Moreover, the
    features like gender, age, etc, are determined at the time of assignment to the family.

    Attributes
    ----------
    population_size (int): Number of people being generated.

    family_pattern_probability_dict (Dict[Family_Pattern, float]): A dictionary containing
    probability of each family pattern that will be used to generate the population.

    community_types (List[Community_Type]): Index of the sub_community this person is in if
    the mentioned person is in the community.

    community_role_names (Set[str]): A list containing all the roles within different community
    types along with the number of people associated with the role.

    distance_function (Function): A function used to evaluate distance.
    """

    def __init__(self, population_size, family_pattern_probability_dict: Dict[Family_Pattern, float],
                 community_types: List[Community_Type],
                 distance_function: types.FunctionType = Distance.euclidean_distance):
        """Initialize a population generator object.

        Args:
            population_size (int): Size of the population.
            family_pattern_probability_dict (Dict[Family_Pattern, float]): A dictionary containing
            probability of each family pattern.

            community_types (List[Community_Type]): A list of all the existing community types.
            distance_function (FunctionType, optional): Defaults to Distance.euclidean_distance.
        """

        self.population_size = population_size
        self.family_pattern_probability_dict = family_pattern_probability_dict
        self.community_types = community_types
        self.community_role_names = set()
        self.distance_function = distance_function

        self.extract_community_roles()
        logger.info('Population Generator created')

    def create_communities_parallel(self, data: (Community_Type, Dict, List[Person])):
        communities_list = list()

        for i in range(data[0].number_of_communities):
            community = data[0].create_community(i, data[1], data[2],
                                                 distance_function=self.distance_function)
            communities_list.append(community)

        return communities_list

    def generate_population(self, is_parallel, show_progress: bool = True):
        """Generates the population based on the given data.

        Args:
            is_parallel (bool): Whether the generation process runs in
            multiprocess setting or not.

            show_progress (bool, optional): Whether to show the progress bar or not.
            Defaults to True.

        Returns:
            List[Person], Dict, List[Family], Dict: People, the general graph,
            families and the formed communities.
        """
        people = list()
        graph = {i: [] for i in range(self.population_size)}

        # split families based on people and graph
        families = self.split_population_to_families(graph, people, self.population_size,
                                                     self.family_pattern_probability_dict)

        logger.info(f'Jobs required to generate the model: {len(self.community_types)}')
        communities = {i: [] for i in range(len(self.community_types))}

        if is_parallel:
            # build the pool object
            pool = Pool()

            # run the pool
            results = pool.map(self.create_communities_parallel,
                               [(community_type, graph, people) for community_type in self.community_types])

            for i in range(len(self.community_types)):
                communities[i].append(results[i])

            # close the pool
            pool.close()
        else:
            number_of_all_communities = sum([community_type.number_of_communities
                                             for community_type in self.community_types])

            with tqdm(total=number_of_all_communities, file=sys.stdout, disable=not show_progress) \
                    as progress_bar:
                for j, community_type in enumerate(self.community_types):
                    for i in range(community_type.number_of_communities):
                        progress_bar.update(1)
                        community = community_type.create_community(i, graph, people,
                                                                    distance_function=self.distance_function)
                        communities[j].append(community)

        return people, graph, families, communities

    def extract_community_roles(self):
        """Fill the community roles list with the string name of community type roles.
        """
        role_names = list()
        for community_type in self.community_types:
            for sub_community_type in community_type.sub_community_types:
                role_names.append(sub_community_type.name)

        self.community_role_names = set(role_names)

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    population_size=self.population_size,
                    family_patterns={y: x for x, y in self.family_pattern_probability_dict.items()},
                    community_types=self.community_types,
                    distance_function=self.distance_function.__name__)

    @staticmethod
    def split_population_to_families(graph, people, population_size, family_pattern_probability_dict):
        """Split the population into families.

        Args:
            graph (Dict): The general graph of the people.
            people (List[Person]): People to be split into families.
            population_size (int): Size of the population.
            family_pattern_probability_dict (Dict): The dictionary containing family patterns
            and the probability of their occurrence.

        Returns:
            List[Family]: A list of constructed families.
        """
        remained_population = population_size
        families = list()
        while remained_population > 0:
            family_pattern = Random.random_choose(family_pattern_probability_dict, 1, True)[0]

            # fix graph
            for i in range(population_size - remained_population,
                           population_size - remained_population + family_pattern.number_of_members):
                graph[i] = []

            family = Family(len(families), list(range(population_size - remained_population,
                                                      population_size - remained_population +
                                                      family_pattern.number_of_members)),
                            family_pattern)

            family.construct_graph(graph, people)
            families.append(family)
            remained_population -= family_pattern.number_of_members
        return families


class Test:
    @staticmethod
    def get_age_distribution_adult():
        params = {
            "lower_bound": 25,
            "upper_bound": 45,
            "mean": 35,
            "std": 5
        }
        return Truncated_Normal_Distribution(params)

    @staticmethod
    def get_age_distribution_youth():
        params = {
            "lower_bound": 18,
            "upper_bound": 24,
            "mean": 21,
            "std": 2
        }
        return Truncated_Normal_Distribution(params)

    @staticmethod
    def get_age_distribution_child():
        params = {
            "lower_bound": 1,
            "upper_bound": 17,
            "mean": 9,
            "std": 8
        }
        return Truncated_Normal_Distribution(params)

    @staticmethod
    def get_age_distribution_old():
        params = {
            "lower_bound": 46,
            "upper_bound": 80,
            "mean": 50,
            "std": 5
        }
        return Truncated_Normal_Distribution(params)

    @staticmethod
    def get_age_distribution():
        age_type = Random.random_choose_uniform([1, 2, 3, 4])
        if age_type == 1:
            return Test.get_age_distribution_child()
        elif age_type == 2:
            return Test.get_age_distribution_youth()
        elif age_type == 3:
            return Test.get_age_distribution_adult()
        elif age_type == 4:
            return Test.get_age_distribution_old()

    @staticmethod
    def get_health_condition_distribution():
        params = {
            "lower_bound": 0,
            "upper_bound": 1,
        }
        return Uniform_Distribution(params)

    @staticmethod
    def get_location_distribution():
        params = {
            "x_lower_bound": 0,
            "x_upper_bound": 100,
            "y_lower_bound": 0,
            "y_upper_bound": 100,
        }
        return Two_Variate_iid_Uniform_Distribution(params)

    @staticmethod
    def get_gender_distribution():
        params = {
            "p": 0.5
        }
        return Bernoulli_Distribution(params)

    @staticmethod
    def generate_random_family_pattern():
        location_distribution = Test.get_location_distribution()
        age_distributions = list()
        health_condition_distributions = list()
        genders = list()
        family_size = Random.random_choose_uniform([1, 2, 3, 4])[0]
        for _ in range(family_size):
            age_distributions.append(Test.get_age_distribution())
            health_condition_distributions.append(Test.get_health_condition_distribution())
            if Random.flip_coin(0.5):
                genders.append(1)
            else:
                genders.append(0)
        return Family_Pattern(family_size, age_distributions, health_condition_distributions, genders,
                              location_distribution)

    @staticmethod
    def get_number_of_members_distribution():
        params = {
            "probability_dict": {
                10: 0.4,
                20: 0.6
            }
        }
        return UniformSet_Distribution(params)

    @staticmethod
    def get_connectivity_distribution():
        params = {
            "lower_bound": 0.8,
            "upper_bound": 1,
        }
        return Uniform_Distribution(params)

    @staticmethod
    def get_transmission_potential_distribution():
        params = {
            "lower_bound": 0.9,
            "upper_bound": 1,
        }
        return Uniform_Distribution(params)

    @staticmethod
    def get_time_cycle_distribution():
        params = {
            "start": {
                "lower_bound": 300,
                "upper_bound": 301
            },
            "length": {
                "lower_bound": 60,
                "upper_bound": 120
            }
        }
        return Uniform_Whole_Week_Time_Cycle_Distribution(params)

    @staticmethod
    def generate_community_type():
        scr1 = Community_Type_Role(Test.get_age_distribution(), Test.get_gender_distribution(),
                                   Test.get_time_cycle_distribution(), True, 1)
        sct1 = Sub_Community_Type(scr1, "Worker", Test.get_number_of_members_distribution(),
                                  Test.get_connectivity_distribution(),
                                  Test.get_transmission_potential_distribution())

        scr2 = Community_Type_Role(Test.get_age_distribution(), Test.get_gender_distribution(),
                                   Test.get_time_cycle_distribution(), False, 1)
        sct2 = Sub_Community_Type(scr2, "Worker", Test.get_number_of_members_distribution(),
                                  Test.get_connectivity_distribution(),
                                  Test.get_transmission_potential_distribution())

        return Community_Type([sct1, sct2], "Office", 3,
                              {0: {1: Test.get_connectivity_distribution()},
                               1: {0: Test.get_connectivity_distribution()}},
                              Test.get_location_distribution(),
                              {0: {1: Test.get_transmission_potential_distribution()},
                               1: {0: Test.get_transmission_potential_distribution()}})


if __name__ == '__main__':
    fp1 = Test.generate_random_family_pattern()
    fp2 = Test.generate_random_family_pattern()
    fp3 = Test.generate_random_family_pattern()

    ct1 = Test.generate_community_type()
    ct2 = Test.generate_community_type()
