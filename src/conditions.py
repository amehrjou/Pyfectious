from datetime import timedelta
from typing import List

from time_handle import Time
from utils import Statistics, Operator, Comparison, Health_Condition


class Condition:
    """This class acts as an interface to build new conditions.

    Conditions are widely used in the simulation to signal specific points
    in time or statistics, e.g., when the simulation reaches an specific moment
    or when the statistics of dead people changes in a certain way.
    """

    def __init__(self):
        """Initialize the condition object.
        """
        pass

    def is_satisfied(self, simulator, end_time: Time) -> List[Time]:
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List[Time]: A list of the satisfaction times.
        """
        pass

    def is_able_to_be_removed(self):
        """Determines whether the condition has served its purpose or not.
        """
        pass

    def to_json(self):
        """Return the json dictionary of the object.

        Raises exception if the child classes do not implement
        this method individually.
        """
        raise NotImplementedError


class Time_Point_Condition(Condition):
    """Set a condition to alert a specific point in simulation time.

    Attributes:
        deadline (Time): The time delta object in Time represents the
        point of time which the condition should be triggered.

        satisfied (bool): True if the condition is satisfied.
    """

    def __init__(self, deadline: Time):
        """Initialize a time point condition.

        Args:
            deadline (Time): The time delta object in Time represents the
            condition deadline.
        """
        super().__init__()
        self.deadline = deadline
        self.satisfied = False

    def is_satisfied(self, simulator, end_time: Time):
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List: The deadline of the condition if satisfied, otherwise none.
        """
        if Time.check_less(self.deadline, simulator.clock) and not self.satisfied:
            self.satisfied = True
            return [self.deadline]
        return []

    def is_able_to_be_removed(self):
        """Checks whether the condition may be removed or not.

        Returns:
            bool: If the condition is satisfied, it may be removed.
        """
        return self.satisfied

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    deadline=self.deadline)


class Statistical_Ratio_Condition(Condition):
    """This class enables the simulation to be notified about certain statistical points.

    The class represents a condition that is triggered when the ratio of two statistics
    reaches a certain target, e.g., when the mortality rate, defined as the number of dead
    people divided by population size reaches 1 percent.

    Attributes:
        people_stat (Dict[Health_Condition: int]): Statistics of the simulation population
        is stored in this dictionary.

        dividend (Health_Condition): The statistics placed in the dividend of ratio.
        divisor (Health_Condition): The statistics placed in the divisor of ratio.

        target_ratio (float): The trigger ratio that dividend/divisor
        is supposed to reach.

        comparison_type (Operator): The operator of the comparison,
        like greater than or less than.

        max_satisfaction (int): Maximum number of times for the
        condition to be satisfied.
    """

    def __init__(self, dividend: Health_Condition, divisor: Health_Condition, target_ratio: float,
                 comparison_type: Operator, max_satisfaction: int):
        """Initialize a statistical ratio condition.

        Args:
            dividend (Health_Condition): The statistics placed in the dividend of ratio.
            divisor (Health_Condition): The statistics placed in the divisor of ratio.

            target_ratio (float): The trigger ratio that dividend/divisor
            is supposed to reach.

            comparison_type (Operator): The operator of the comparison,
            like greater than or less than.

            max_satisfaction (int): Maximum number of times for the
            condition to be satisfied.

        """
        super().__init__()
        self.people_stat = dict()
        self.dividend = dividend
        self.divisor = divisor
        self.comparison_type = comparison_type
        self.target_ratio = target_ratio
        self.max_satisfaction = max_satisfaction
        self.can_be_satisfied = True

    def is_satisfied(self, simulator, end_time: Time):
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List [Time]: The clock of the simulation when the condition is
            satisfied, otherwise none.
        """
        self.people_stat = simulator.statistics.get_people_statistics()
        current_ratio = self.people_stat[self.dividend] / self.people_stat[self.divisor]

        # stop the condition from repeatedly being triggered
        if not Comparison.compare(current_ratio, self.target_ratio, self.comparison_type):
            self.can_be_satisfied = True

        if Comparison.compare(current_ratio, self.target_ratio, self.comparison_type) and \
                self.max_satisfaction and self.can_be_satisfied:

            self.max_satisfaction -= 1
            self.can_be_satisfied = False
            return [simulator.clock]
        else:
            return []

    def is_able_to_be_removed(self):
        """Checks whether the condition may be removed or not.

        Returns:
            bool: If the condition is satisfied, it may be removed.
        """
        return self.max_satisfaction == 0

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    dividend=self.dividend,
                    divisor=self.divisor,
                    comparison_type=self.comparison_type,
                    target_ratio=self.target_ratio,
                    max_satisfaction=self.max_satisfaction)


class Statistical_Ratio_Role_Condition(Condition):
    """This class enables the simulation to be notified about certain statistical points.

    The class represents a condition that is triggered when the ratio of two statistics
    reaches a certain target for a specific role, e.g., when the mortality rate, defined
    as the number of dead people divided by population size reaches 1 percent for teachers
    or students, etc.

    Attributes:
        role_stat (Dict[Health_Condition: int]): Statistics of the simulation population
        for a specific role is stored in this dictionary.

        dividend (Health_Condition): The statistics placed in the dividend of ratio.
        divisor (Health_Condition): The statistics placed in the divisor of ratio.

        target_ratio (float): The trigger ratio that dividend/divisor
        is supposed to reach.

        comparison_type (Operator): The operator of the comparison,
        like greater than or less than.

        role_name (str): The name of the target role.
        max_satisfaction (int): Maximum number of times for the condition to be satisfied.
    """

    def __init__(self, dividend: Health_Condition, divisor: Health_Condition, target_ratio: float,
                 comparison_type: Operator, role_name: str, max_satisfaction: int):
        """Initialize a statistical role ratio condition.

        Args:
            dividend (Health_Condition): The statistics placed in the dividend of ratio.
            divisor (Health_Condition): The statistics placed in the divisor of ratio.

            target_ratio (float): The trigger ratio that dividend/divisor
            is supposed to reach.

            comparison_type (Operator): The operator of the comparison,
            like greater than or less than.

            role_name (str): The name of the target role.
            max_satisfaction (int): Maximum number of times for the
            condition to be satisfied.
        """
        super().__init__()
        self.role_stat = dict()
        self.dividend = dividend
        self.divisor = divisor
        self.comparison_type = comparison_type
        self.target_ratio = target_ratio
        self.role_name = role_name
        self.max_satisfaction = max_satisfaction

    def is_satisfied(self, simulator, end_time: Time):
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List: The clock of the simulation when the condition is
            satisfied, otherwise none.
        """
        self.role_stat = Statistics.get_role_statistics(simulator.people, self.role_name)
        current_ratio = self.role_stat[self.dividend] / self.role_stat[self.divisor]

        if Comparison.compare(current_ratio, self.target_ratio, self.comparison_type) and self.max_satisfaction:
            self.max_satisfaction -= 1
            return [simulator.clock]

        return []

    def is_able_to_be_removed(self):
        """Checks whether the condition may be removed or not.

        Returns:
            bool: If the condition is satisfied, it may be removed.
        """
        return self.max_satisfaction == 0

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    dividend=self.dividend,
                    divisor=self.divisor,
                    comparison_type=self.comparison_type,
                    target_ratio=self.target_ratio,
                    role_name=self.role_name,
                    max_satisfaction=self.max_satisfaction)


class Statistical_Family_Condition(Condition):
    """This class enables the simulation to be notified about certain statistical points.

    The class represents a condition that is triggered when the ratio of a certain
    statistics like deaths or infected reaches a certain target for the families.

    Note: This class only considers one statistic against the total number of families.

    Attributes:
        family_stat (Dict[Health_Condition: int]): Statistics of the simulation population
        for the families is stored in this dictionary.

        target_ratio (float): The trigger ratio that dividend/divisor
        is supposed to reach.

        stat_type (Health_Condition): Choose which stat type to consider against
        the number of families.

        comparison_type (Operator): The operator of the comparison,
        like greater than or less than.

        max_satisfaction (int): Maximum number of times for the condition to be satisfied.
        """

    def __init__(self, stat_type: Health_Condition, target_ratio: float,
                 comparison_type: Operator, max_satisfaction: int):
        super().__init__()
        self.target_ratio = target_ratio
        self.stat_type = stat_type
        self.family_stat = dict()
        self.comparison_type = comparison_type
        self.max_satisfaction = max_satisfaction

    def is_satisfied(self, simulator, end_time: Time):
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List: The clock of the simulation when the condition is
            satisfied, otherwise none.
        """
        self.family_stat = Statistics.get_family_statistics(simulator.people, simulator.families)
        current_ratio = self.family_stat[self.stat_type] / len(simulator.families)

        if Comparison.compare(current_ratio, self.target_ratio, self.comparison_type) and self.max_satisfaction:
            self.max_satisfaction -= 1
            return [simulator.clock]

        return []

    def is_able_to_be_removed(self):
        """Checks whether the condition may be removed or not.

        Returns:
            bool: If the condition is satisfied, it may be removed.
        """
        return self.max_satisfaction == 0

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    stat_type=self.stat_type,
                    target_ratio=self.target_ratio,
                    comparison_type=self.comparison_type,
                    max_satisfaction=self.max_satisfaction)


class Time_Period_Condition(Condition):
    """Set a condition to alert specific periodic points in simulation time.

    Note: This condition contains several time point conditions that are set
    to be triggered according to the period until the end of the simulation.

    Attributes:
        period (Time): The time delta object in Time represents the
        point of time which the condition should be triggered.

        conditions (List[Time_Point_Condition]): A set of time point
        conditions to be triggered by the value of period.

        conditions_are_initialized (bool): True if the time point conditions
        are initialized.
    """

    def __init__(self, period: Time):
        """Initialize the time period object.

        Args:
            period (Time): The time delta object in Time represents the
            point of time which the condition should be triggered.

        """
        super().__init__()
        self.period = period
        self.conditions: List[Time_Point_Condition] = list()
        self.conditions_are_initialized = False

    def initialize_time_point_conditions(self, end_time: Time):
        """ Initialize a set of time point conditions according to the period.

        Args:
            end_time: The end time of the simulation
        """
        for i in range(0, end_time.get_minutes() + 1, self.period.get_minutes()):
            time_point_condition = Time_Point_Condition(Time(timedelta(minutes=i)))
            self.conditions.append(time_point_condition)
        self.conditions.sort(key=lambda x: x.deadline.get_minutes())

    def is_satisfied(self, simulator, end_time: Time):
        """Check whether the condition is satisfied or not.

        Args:
            simulator (Simulator): The simulator object.
            end_time (Time): The final time of the simulation.

        Returns:
            List: The clock of the simulation when the condition is
            satisfied, otherwise none.
        """
        if not self.conditions_are_initialized:
            self.initialize_time_point_conditions(end_time)
            self.conditions_are_initialized = True

        satisfaction_times = list()
        while len(self.conditions) > 0 and self.conditions[0].is_satisfied(simulator, end_time):
            satisfaction_times.append(self.conditions[0].deadline)
            self.conditions.pop(0)

        return satisfaction_times

    def is_able_to_be_removed(self):
        """Checks whether the condition may be removed or not.

        Returns:
            bool: If the condition is satisfied, it may be removed.
        """
        return len(self.conditions) == 0

    def to_json(self):
        """Return the json dictionary of the object.
        """
        return dict(name=self.__class__.__name__,
                    period=self.period)
