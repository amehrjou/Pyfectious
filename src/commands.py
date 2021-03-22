from typing import List

from conditions import Condition
from distributions import Random
from logging_settings import logger
from time_handle import Time
from utils import Infection_Status


class Command:
    """A command to change the course of the simulation.

    A command is defined as an action which enforces an alteration upon an
    ongoing simulation. These actions include a variety of quarantine and
    restriction options.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition):
        """Initialize a command object.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.
        """
        self.condition = condition
        self.is_deleted = False

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.

            end_time (Time): The final time of the simulation.
        """
        pass

    def action_is_done(self):
        """Check if the command has done its action.
        """
        return self.condition.is_able_to_be_removed()

    def to_json(self):
        """Raise exception if child classes do not implement to_json method.
        """
        raise NotImplementedError


class Nope(Command):
    """ An empty command to complete the search space.
    """

    def __init__(self):
        """Create a nope command.
        """
        pass

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__)


class Quarantine_Single_Community(Command):
    """A command to quarantine a single community in the simulation.

    Having the community type name and index of community in a set of
    community types, this command is capable of dismiss all the people
    from the indicated community.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.

    community_type_name (str): The name of the community type to be quarantined.

    community_index (int): The index of community, since there might be more than
    one community created from the specified community type.
    """

    def __init__(self, condition: Condition, community_type_name: str, community_index: int):
        """Initialize a quarantine single community command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            community_type_name (str): The name of the community type to be quarantined.

            community_index (int): The index of community, since there might be more than
            one community created from the specified community type.
        """
        super().__init__(condition)
        self.condition = condition
        self.community_index = community_index
        self.community_type_name = community_type_name

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.

            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}, target: {self.community_type_name}')

            for community_type_id in simulator.communities:
                if simulator.communities[community_type_id][0].community_type.name == self.community_type_name:
                    logger.debug(f'Community quarantined: {self.community_type_name}, {self.community_index}')
                    simulator.communities[community_type_id][self.community_index].quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    community_type_name=self.community_type_name,
                    community_index=self.community_index)


class Unquarantine_Single_Community(Command):
    """A command to unquarantine a single community in the simulation.

    Having the community type name and index of community in a set of
    community types, this command is capable of lift the quarantine from
    all the people inside the community.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.

    community_type_name (str): The name of the community type to be quarantined.

    community_index (int): The index of community, since there might be more than
    one community created from the specified community type.
    """

    def __init__(self, condition: Condition, community_type_name: str, community_index: int):
        """Initialize an unquarantine single community command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            community_type_name (str): The name of the community type to be unquarantined.

            community_index (int): The index of community, since there might be more than
            one community created from the specified community type.
        """
        super().__init__(condition)
        self.condition = condition
        self.community_index = community_index
        self.community_type_name = community_type_name

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.

            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}, target: {self.community_type_name}')

            for community_type_id in simulator.communities:
                if simulator.communities[community_type_id][0].community_type.name == self.community_type_name:
                    logger.debug(f'Community quarantined: {self.community_type_name}, {self.community_index}')
                    simulator.communities[community_type_id][self.community_index].unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    community_type_name=self.community_type_name,
                    community_index=self.community_index)


class Quarantine_Community_Type(Command):
    """A command to quarantine a community type in the simulation.

    Having the community type name, this command is capable of dismiss
    all the people from the indicated community type.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.

    community_type_name (str): The name of the community type to be quarantined.
    """

    def __init__(self, condition: Condition, community_type_name: str):
        """Initialize a quarantine community type command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            community_type_name (str): The name of the community type to be quarantined.
        """
        super().__init__(condition)
        self.community_type_name = community_type_name

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}, target: {self.community_type_name}')

            for community_type_id in simulator.communities:
                if simulator.communities[community_type_id][0].community_type.name == self.community_type_name:
                    logger.debug(f'Community type quarantined: {self.community_type_name}')
                    for community in simulator.communities[community_type_id]:
                        community.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    community_type_name=self.community_type_name)


class Unquarantine_Community_Type(Command):
    """A command to unquarantine a community type in the simulation.

    Having the community type name, this command is capable of lift the
    quarantine from the indicated community type.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.

    community_type_name (str): The name of the community type to be quarantined.
    """

    def __init__(self, condition: Condition, community_type_name: str):
        """Initialize an unquarantine community type command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            community_type_name (str): The name of the community type to be unquarantined.
        """
        super().__init__(condition)
        self.community_type_name = community_type_name

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}, target: {self.community_type_name}')

            for community_type_id in simulator.communities:
                if simulator.communities[community_type_id][0].community_type.name == self.community_type_name:
                    logger.debug(f'Community type quarantined: {self.community_type_name}')
                    for community in simulator.communities[community_type_id]:
                        community.unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    community_type_name=self.community_type_name)


class Quarantine_Single_Family(Command):
    """A command to quarantine a single family in the simulation.

    Having the family id number, this command is capable of enforcing a
    quarantine upon the entire family.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the family to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, id: int):
        """Initialize a quarantine single family command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            id (int): The id number of the family to be quarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.id = id

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for family in simulator.families:
                if family.id_number == self.id:
                    logger.debug(f'Family quarantined: {family.id_number}')
                    family.quarantine(simulator.people)

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.id)


class Unquarantine_Single_Family(Command):
    """A command to unquarantine a single family in the simulation.

    Having the family id number, this command is capable of releasing the
    quarantine of the entire family.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the family to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, id: int):
        """Initialize an unquarantine single family command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            id (int): The id number of the family to be unquarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.id = id

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for family in simulator.families:
                if family.id_number == self.id:
                    logger.debug(f'Family unquarantined: {family.id_number}')
                    family.unquarantine(simulator.people)

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.id)


class Quarantine_Multiple_Families(Command):
    """A command to quarantine multiple families in the simulation.

    Having the family id number, this command is capable of enforcing a
    quarantine upon multiple families.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    ids (List[int]): The id number of the families to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, ids: List[int]):
        """Initialize a quarantine multiple family command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            ids (List[int]): The id number of the families to be quarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.ids = ids

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for family in simulator.families:
                if family.id_number in self.ids:
                    logger.debug(f'Family quarantined: {family.id_number}')
                    family.quarantine(simulator.people)

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.ids)


class Unquarantine_Multiple_Families(Command):
    """A command to unquarantine multiple families in the simulation.

    Having the family id number, this command is capable of releasing
    the quarantine of multiple families.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    ids (List[int]): The id number of the families to be unquarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, ids: List[int]):
        """Initialize an unquarantine multiple family command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            ids (List[int]): The id number of the families to be unquarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.ids = ids

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for family in simulator.families:
                if family.id_number in self.ids:
                    logger.debug(f'Family unquarantined: {family.id_number}')
                    family.unquarantine(simulator.people)

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.ids)


class Quarantine_Single_Person(Command):
    """A command to quarantine a single person in the simulation.

    Having the person's id number, this command is capable of quarantining
    the person by clearing the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, id: int):
        """Initialize a quarantine single person command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            id (int): The id number of the person to be quarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.id = id

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.id_number == self.id:
                    logger.debug(f'Person quarantined: {person.id_number}')
                    person.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.id)


class Unquarantine_Single_Person(Command):
    """A command to unquarantine a single person in the simulation.

    Having the person's id number, this command is capable of unquarantining
    the person by rescheduling the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, id: int):
        """Initialize an unquarantine single person command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            id (int): The id number of the person to be unquarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.id = id

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.id_number == self.id:
                    logger.debug(f'Person unquarantined: {person.id_number}')
                    person.unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    id=self.id)


class Quarantine_Multiple_People(Command):
    """A command to quarantine a group of people in the simulation.

    Having the people's id number, this command is capable of quarantining
    each person by clearing the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, ids: List[int]):
        """Initialize a quarantine multiple people command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            ids (List[int]): The id number of people to be quarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.ids = ids

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.id_number in self.ids:
                    logger.debug(f'Person quarantined: {person.id_number}')
                    person.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    ids=self.ids)


class Quarantine_All_People(Command):
    """A command to quarantine all the people in the simulation.

    This command is capable of quarantining each person in the simulation
    by clearing the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition):
        """Initialize a quarantine all people command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.
        """
        super().__init__(condition)
        self.condition = condition

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                person.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition)


class Unquarantine_All_People(Command):
    """A command to unquarantine all the people in the simulation.

    This command is capable of unquarantining each person in the simulation
    by rescheduling the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition):
        """Initialize an unquarantine all people command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.
        """
        super().__init__(condition)
        self.condition = condition

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                person.unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition)


class Unquarantine_Multiple_People(Command):
    """A command to unquarantine a group of people in the simulation.

    Having the people's id number, this command is capable of unquarantining
    each person by rescheduling the daily plans of the subject.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, ids: List[int]):
        """Initialize an unquarantine multiple person command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            ids (List[int]): The id number of people to be unquarantined.
        """
        super().__init__(condition)
        self.condition = condition
        self.ids = ids

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.id_number in self.ids:
                    logger.debug(f'Person unquarantined: {person.id_number}')
                    person.unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    ids=self.ids)


class Quarantine_Diseased_People_Noisy(Command):
    """A command to quarantine every infected person with an error in detection.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    probability (float): The correct detection probability.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition, probability: float):
        """Initialize a quarantine infected people with noise command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            probability (float): The correct detection probability.
        """
        super().__init__(condition)
        self.condition = condition
        self.probability = probability

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.infection_status is Infection_Status.CONTAGIOUS or \
                        person.infection_status is Infection_Status.INCUBATION:
                    if Random.flip_coin(self.probability):
                        logger.debug(f'Person quarantined: {person.id_number}')
                        person.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    probability=self.probability)


class Quarantine_Diseased_People(Command):
    """A command to quarantine every infected person in the simulation.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition):
        """Initialize a quarantine infected people command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.
        """
        super().__init__(condition)
        self.condition = condition

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.infection_status is Infection_Status.CONTAGIOUS or \
                        person.infection_status is Infection_Status.INCUBATION:
                    logger.debug(f'Person quarantined: {person.id_number}')
                    person.quarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition)


class Unquarantine_Diseased_People(Command):
    """A command to unquarantine every infected person in the simulation.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.

    condition (Condition): A condition that determines when the command should
    be triggered.
    """

    def __init__(self, condition: Condition):
        """Initialize an unquarantine infected people command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.
        """
        super().__init__(condition)
        self.condition = condition

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.



            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}')

            for person in simulator.people:
                if person.infection_status is Infection_Status.CONTAGIOUS or \
                        person.infection_status is Infection_Status.INCUBATION:
                    logger.debug(f'Person unquarantined: {person.id_number}')
                    person.unquarantine()

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition)


class Restrict_Certain_Roles(Command):
    """A command to reduce the number of people attending their role.

    This command is employed whenever there is an intention of reducing the
    presence of people in a certain role during the simulation, e.g., cutting
    the number of students in half.

    Attributes
    ----------
    is_deleted (bool): Determines whether the command has served its purpose.
    id (int): The id number of the person to be quarantined.

    condition (Condition): A condition that determines when the command should
    be triggered.

    role_name (String): The name of the role to be restricted.

    restriction_ratio (float): The ratio of restriction. The higher the ratio
    the less people attending the role.
    """

    def __init__(self, condition: Condition, role_name: str, restriction_ratio: float):
        """Initialize a restriction on certain community roles command.

        Args:
            condition (Condition): A condition that determines when the command
            should be triggered.

            role_name (String): The name of the role to be restricted.

            restriction_ratio (float): The ratio of restriction. The higher the ratio
            the less people attending the role.
        """
        super().__init__(condition)
        self.condition = condition
        self.role_name = role_name
        self.restriction_ratio = restriction_ratio

    def take_action(self, simulator, end_time: Time):
        """Start the action that the commands is designed for.

        Args:
            simulator (Simulator): The main simulator object which is passed to
            this command.

            end_time (Time): The final time of the simulation.
        """
        if self.condition.is_satisfied(simulator, end_time):
            logger.info(f'Command executed: {self.__class__.__name__}, {self.role_name}')

            for person in simulator.people:
                for community, subcommunity_type_index in person.communities:
                    if self.role_name == community.community_type.sub_community_types[subcommunity_type_index].name:
                        community.community_type.sub_community_types[subcommunity_type_index] \
                            .community_type_role.presence_prob = 1 - self.restriction_ratio

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    role_name=self.role_name,
                    restriction_ratio=self.restriction_ratio)
