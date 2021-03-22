from typing import Tuple

import numpy as np
from scipy.stats import bernoulli
from scipy.stats import expon
from scipy.stats import norm
from scipy.stats import truncnorm
from scipy.stats import uniform

from time_handle import Time
from time_handle import Week_Days


class Distribution:
    """A class to model a basic statistical distribution.

    This class provides the basic functions required to integrate a statistical
    distribution. Distributions are used to correctly implement the probabilistic
    features of the simulation.
    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution
        parameters.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        self.parameters_dict = parameters_dict

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        pass

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        pass

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        pass

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        pass

    def accept_sample(self, sample: float):
        """Decide whether to accept a sample.

        Args:
            sample (float): The sample about which the accept decision is made.

        Returns:
            bool: True if the sample accepts, False if not.
        """
        return self.pdf(sample) >= np.random.uniform()

    def reject_sample(self, sample: float):
        """Decide whether to reject a sample.

        Args:
            sample (float): The sample about which the reject decision is made.

        Returns:
            bool: True if the sample rejects, False if not.
        """
        return self.pdf(sample) < np.random.uniform()

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    params=self.parameters_dict)


class Multivariate_Distribution(Distribution):
    """A class to model the statistical multivariate distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution
        parameters.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the multivariate distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        pass

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        pass

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        pass

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        pass


class Two_Variate_Distribution(Multivariate_Distribution):
    """A class to model the statistical two-variate distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution
        parameters.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the two variate distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        pass

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        pass

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        pass

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        pass


class Two_Variate_iid_Uniform_Distribution(Two_Variate_Distribution):
    """A class to model the statistical two-variate uniform iid distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        x_lower_bound (float): The x variable lower bound extracted from parameters_dict.
        x_upper_bound (float): The x variable upper bound extracted from parameters_dict.
        y_lower_bound (float): The y variable lower bound extracted from parameters_dict.
        y_upper_bound (float): The y variable upper bound extracted from parameters_dict.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the two variate uniform iid distribution and extract parameters.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """

        super().__init__(parameters_dict)
        self.x_lower_bound = parameters_dict["x_lower_bound"]
        self.x_upper_bound = parameters_dict["x_upper_bound"]
        self.y_lower_bound = parameters_dict["y_lower_bound"]
        self.y_upper_bound = parameters_dict["y_upper_bound"]

    def cdf(self, x: Tuple[float]):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.

        Returns:
            float: The CDF value at point x.
        """
        return uniform.cdf(x[0], loc=self.x_lower_bound, scale=self.x_upper_bound - self.x_lower_bound) \
               * uniform.cdf(x[1], loc=self.y_lower_bound, scale=self.y_upper_bound - self.y_lower_bound)

    def pdf(self, x: Tuple[float]):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        return uniform.pdf(x[0], loc=self.x_lower_bound, scale=self.x_upper_bound - self.x_lower_bound) \
               * uniform.pdf(x[1], loc=self.y_lower_bound, scale=self.y_upper_bound - self.y_lower_bound)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        return (uniform.rvs(loc=self.x_lower_bound, scale=self.x_upper_bound - self.x_lower_bound)
                , uniform.rvs(loc=self.y_lower_bound, scale=self.y_upper_bound - self.y_lower_bound))

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        return list(zip(uniform.rvs(loc=self.x_lower_bound, scale=self.x_upper_bound - self.x_lower_bound, size=size)
                        ,
                        uniform.rvs(loc=self.y_lower_bound, scale=self.y_upper_bound - self.y_lower_bound, size=size)))


class Two_Variate_iid_Truncated_Normal_Distribution(Two_Variate_Distribution):
    """A class to model the statistical truncated two-variate uniform iid distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        x_lower_bound (float): The x variable lower bound extracted from parameters_dict.
        x_upper_bound (float): The x variable upper bound extracted from parameters_dict.
        y_lower_bound (float): The y variable lower bound extracted from parameters_dict.
        y_upper_bound (float): The y variable upper bound extracted from parameters_dict.
        x_mean (float): The x mean extracted from parameters_dict["x_mean"]
        x_std  (float): The x std extracted from parameters_dict["x_std"]
        y_mean (float): The y mean extracted from parameters_dict["y_mean"]
        y_std  (float): The y std extracted from parameters_dict["y_std"]

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the truncated two variate uniform iid distribution and extract parameters.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.x_lower_bound = parameters_dict["x_lower_bound"]
        self.x_upper_bound = parameters_dict["x_upper_bound"]
        self.x_mean = parameters_dict["x_mean"]
        self.x_std = parameters_dict["x_std"]
        self.y_lower_bound = parameters_dict["y_lower_bound"]
        self.y_upper_bound = parameters_dict["y_upper_bound"]
        self.y_mean = parameters_dict["y_mean"]
        self.y_std = parameters_dict["y_std"]

    def cdf(self, x: Tuple[float]):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.

        Returns:
            float: The CDF value at point x.
        """
        x_a, x_b = (self.x_lower_bound - self.x_mean) / self.x_std, (self.x_upper_bound - self.x_mean) / self.x_std
        y_a, y_b = (self.y_lower_bound - self.y_mean) / self.y_std, (self.y_upper_bound - self.y_mean) / self.y_std
        return truncnorm.cdf(x[0], x_a, x_b, self.x_mean, self.x_std) * truncnorm.cdf(x[1], y_a, y_b, self.y_mean,
                                                                                      self.y_std)

    def pdf(self, x: Tuple[float]):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        x_a, x_b = (self.x_lower_bound - self.x_mean) / self.x_std, (self.x_upper_bound - self.x_mean) / self.x_std
        y_a, y_b = (self.y_lower_bound - self.y_mean) / self.y_std, (self.y_upper_bound - self.y_mean) / self.y_std
        return truncnorm.pdf(x[0], x_a, x_b, self.x_mean, self.x_std) * truncnorm.pdf(x[1], y_a, y_b, self.y_mean,
                                                                                      self.y_std)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        x_a, x_b = (self.x_lower_bound - self.x_mean) / self.x_std, (self.x_upper_bound - self.x_mean) / self.x_std
        y_a, y_b = (self.y_lower_bound - self.y_mean) / self.y_std, (self.y_upper_bound - self.y_mean) / self.y_std
        return ((truncnorm.rvs(x_a, x_b, size=1) * self.x_std + self.x_mean)[0],
                (truncnorm.rvs(y_a, y_b, size=1) * self.y_std + self.y_mean)[0])

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        x_a, x_b = (self.x_lower_bound - self.x_mean) / self.x_std, (self.x_upper_bound - self.x_mean) / self.x_std
        y_a, y_b = (self.y_lower_bound - self.y_mean) / self.y_std, (self.y_upper_bound - self.y_mean) / self.y_std
        return list(zip(truncnorm.rvs(x_a, x_b, size=size) * self.x_std + self.x_mean
                        , truncnorm.rvs(y_a, y_b, size=size) * self.y_std + self.y_mean))

    def accept_sample(self, sample: Tuple[float]):
        """Decide whether to accept a sample.

        Args:
            sample (float): The sample about which the accept decision is made.

        Returns:
            bool: True if the sample accepts, False if not.
        """
        return self.cdf(sample) >= np.random.uniform()

    def reject_sample(self, sample: Tuple[float]):
        """Decide whether to reject a sample.

        Args:
            sample (float): The sample about which the reject decision is made.

        Returns:
            bool: True if the sample rejects, False if not.
        """
        return self.cdf(sample) < np.random.uniform()


class Truncated_Normal_Distribution(Distribution):
    """A class to model the statistical truncated normal distributions.

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        lower_bound (float): The lower bound extracted from parameters_dict.
        upper_bound (float): The upper bound extracted from parameters_dict.
        mean (float): The mean extracted from parameters_dict["y_mean"]
        std  (float): The std extracted from parameters_dict["y_std"]

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the truncated normal distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.lower_bound = parameters_dict["lower_bound"]
        self.upper_bound = parameters_dict["upper_bound"]
        self.mean = parameters_dict["mean"]
        self.std = parameters_dict["std"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        a, b = (self.lower_bound - self.mean) / self.std, (self.upper_bound - self.mean) / self.std
        return truncnorm.cdf(x, a, b, self.mean, self.std)

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        a, b = (self.lower_bound - self.mean) / self.std, (self.upper_bound - self.mean) / self.std
        return truncnorm.pdf(x, a, b, self.mean, self.std)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        a, b = (self.lower_bound - self.mean) / self.std, (self.upper_bound - self.mean) / self.std
        return (truncnorm.rvs(a, b, size=1) * self.std + self.mean)[0]

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        a, b = (self.lower_bound - self.mean) / self.std, (self.upper_bound - self.mean) / self.std
        return truncnorm.rvs(a, b, size=size) * self.std + self.mean


class Normal_Distribution(Distribution):
    """A class to model the statistical normal distributions.

    The class acts as wrapper for scipy norm distribution.

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
    """

    def __init__(self, parameters_dict: dict):
        """Initialize the normal distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.mu = parameters_dict["mu"]
        self.sigma = parameters_dict["sigma"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        return norm.cdf(x, loc=self.mu, scale=self.sigma)

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        return norm.pdf(x, loc=self.mu, scale=self.sigma)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        return (np.random.normal(self.mu, self.sigma, 1))[0]

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        return np.random.normal(self.mu, self.sigma, size)


class Uniform_Distribution(Distribution):
    """A class to model the statistical uniform distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        lower_bound (float): The lower bound extracted from parameters_dict.
        upper_bound (float): The upper bound extracted from parameters_dict.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.lower_bound = parameters_dict["lower_bound"]
        self.upper_bound = parameters_dict["upper_bound"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        return uniform.cdf(x, loc=self.lower_bound, scale=self.upper_bound - self.lower_bound)

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        return uniform.pdf(x, loc=self.lower_bound, scale=self.upper_bound - self.lower_bound)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        return uniform.rvs(loc=self.lower_bound, scale=self.upper_bound - self.lower_bound)

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        return uniform.rvs(loc=self.lower_bound, scale=self.upper_bound - self.lower_bound, size=size)


class Bernoulli_Distribution(Distribution):
    """A class to model the statistical bernoulli distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        p (float): The lower bound extracted from parameters_dict.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the bernoulli distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.p = parameters_dict["p"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        return bernoulli.cdf(x, self.p)

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        return bernoulli.pmf(x, self.p)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        return bernoulli.rvs(self.p)

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        return bernoulli.rvs(self.p, size=size)


class UniformSet_Distribution(Distribution):
    """A class to model the statistical uniform set distributions.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform set distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.probability_dict = parameters_dict["probability_dict"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        values, probabilities = list(self.probability_dict.keys()), list(self.probability_dict.values())
        values, probabilities = zip(*sorted(list(zip(values, probabilities))))
        prob = 0
        for value, probability in zip(values, probabilities):
            if x >= value:
                prob += probability
        return prob

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        if x in self.probability_dict.keys():
            return self.probability_dict[x]
        else:
            return 0

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        values, probabilities = list(self.probability_dict.keys()), list(self.probability_dict.values())
        return np.random.choice(values, size=1, replace=True, p=probabilities)[0]

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        values, probabilities = list(self.probability_dict.keys()), list(self.probability_dict.values())
        return np.random.choice(values, size=size, replace=True, p=probabilities)


class Exponential_Distribution(Distribution):
    """This class represents the statistical exponential distribution.

    This is mainly used to model parameters like immunity conditioned with age,
    but may also be used in other relevant circumstances.
    """

    def __init__(self, parameters_dict: dict):
        """Initialize the bernoulli distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.scale = parameters_dict["scale"]

    def cdf(self, x: float):
        """Find the CDF for a certain x value.

        Args:
            x (float): The value for which the CDF is needed.
        """
        return expon.cdf(x, scale=self.scale)

    def pdf(self, x: float):
        """Find the PDF for a certain x value.

        Args:
            x (float): The value for which the PDF is needed.
        """
        return expon.pdf(x, scale=self.scale)

    def sample_single_random_variable(self):
        """Samples a single random variable from the distribution.
        """
        return expon.rvs(scale=self.scale)

    def sample_multiple_random_variables(self, size: int):
        """Sample a number of random variables from the distribution.

        Args:
            size (int): Number of random variables to be sampled.
        """
        return expon.rvs(scale=self.scale, size=size)


class Time_Cycle_Distribution:
    """A class to model the statistical time cycle distributions.

    This distribution is mainly used to plan an event during the day, such as working in
    an office or going to the schools.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the time cycle distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        self.parameters_dict = parameters_dict

    def sample_single_random_variable(self, time: Time) -> (int, int):
        """Samples a single random variable from the distribution.
        """
        pass

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    params=self.parameters_dict)


class Uniform_Whole_Week_Time_Cycle_Distribution(Time_Cycle_Distribution):
    """A class to model the statistical uniform distribution for an entire week.

    The class uses a start point and length. This results in a sample time period characterized
    by [start, start + length]. This class inherits from the Time-Cycle distribution and resembles
    the distribution of daily activities like work.


    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        length_distribution (float): The length of the time distribution extracted from
        parameters_dict.

        start_distribution (float): The starting point of the time distribution extracted
        from parameters_dict.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform whole week time cycle distribution class using a
        parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.start_distribution = Uniform_Distribution(parameters_dict["start"])
        self.length_distribution = Uniform_Distribution(parameters_dict["length"])

    def sample_single_random_variable(self, time: Time) -> (int, int):
        """Samples a single random variable from the distribution.

        Args:
            time (Time): The time in case used in distribution.

        Returns:
            int, int: The start and the length of the time period.
        """
        start = self.start_distribution.sample_single_random_variable()
        length = self.length_distribution.sample_single_random_variable()
        return start, length


class Uniform_Weekend_Time_Cycle_Distribution(Time_Cycle_Distribution):
    """A class to model the uniform weekend time cycle.

    The class uses a start point and length. This results in a sample time period characterized
    by [start, start + length]. The length is set to zero if we are not in the weekends.

    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        length_distribution (float): The length of the time distribution extracted from
        parameters_dict.

        start_distribution (float): The starting point of the time distribution extracted
        from parameters_dict.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform whole week time cycle distribution class using a
        parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.start_distribution = Uniform_Distribution(parameters_dict["start"])
        self.length_distribution = Uniform_Distribution(parameters_dict["length"])

    def sample_single_random_variable(self, time: Time) -> (int, int):
        """Samples a single random variable from the distribution.

        Args:
            time (Time): The time in case used in distribution.

        Returns:
            int, int: The start and the length of the time period.
        """
        start = self.start_distribution.sample_single_random_variable()

        length = 0
        if time.get_day_of_week() is Week_Days.SATURDAY or \
                time.get_day_of_week() is Week_Days.SUNDAY:
            # These events only have a length if they are on holidays
            length = self.length_distribution.sample_single_random_variable()

        return start, length


class Disease_Property_Distribution:
    """A class to model the statistical disease properties distributions.

    This distribution is mainly used to generate disease attributes, such as mortality
    rate, immunity, and infectious rate. The class may be expanded to cover other disease
    distributions and match more complex statistical models as well.
    ...

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
    """

    def __init__(self, parameters_dict: dict):
        """Initialize the disease property distribution class using a parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        self.parameters_dict = parameters_dict

    def sample_single_random_variable(self, time: Time, person) -> float:
        """Samples a single random variable from the distribution.

        Args:
            time (Time): The time in case used in distribution.
            person (Person): The person given to this distribution.

        Returns:
            float: The sampled value.
        """
        pass

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    params=self.parameters_dict)


class Uniform_Disease_Property_Distribution(Disease_Property_Distribution):
    """A class to model the statistical uniform disease properties distributions.

    This distribution is mainly used to generate disease attributes, such as mortality
    rate, immunity, and infectious rate. The class inherits from the disease property
    distribution.

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        distribution (Distribution): The distribution of the disease property.

    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform disease property distribution class using a
        parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.distribution = Uniform_Distribution(parameters_dict)

    def sample_single_random_variable(self, time: Time, person) -> float:
        """Samples a single random variable from the distribution.

        Args:
            time (Time): The time in case used in distribution.

        Returns:
            float: The sampled value.
        """
        return self.distribution.sample_single_random_variable()


class Truncated_Normal_Disease_Property_Distribution(Disease_Property_Distribution):
    """A class to model the statistical truncated normal disease properties distributions.

    This distribution is mainly used to generate disease attributes, such as disease period
    and incubation period. The class inherits from the disease property distribution, and
    is employed whenever a disease property follows a truncated normal distribution.

    Attributes:
        parameters_dict (dict): The dictionary object containing the distribution parameters.
        distribution (Distribution): The distribution of the disease property.
    """

    def __init__(self, parameters_dict: dict):
        """Initialize the uniform disease property distribution class using a
        parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.distribution = Truncated_Normal_Distribution(parameters_dict)

    def sample_single_random_variable(self, time: Time, person) -> float:
        """Samples a single random variable from the distribution.

        Args:
            time (Time): The time in case used in distribution.

        Returns:
            float: The sampled value.
        """
        return self.distribution.sample_single_random_variable()


class Immunity_Distribution(Disease_Property_Distribution):
    """A class to model the immunity distributions.

    This distribution is mainly used to generate the immunity distribution given
    the person and a set of upper and lower bounds in parameters dict.

    Note: It is assumed that immunity increases after each time of infection,
    nearly impossible for a person to be infected for a third or fourth time.
    Also, immunity is related to the person's age, where younger people are
    less likely to catch the disease.

    Note: This distribution is subject to change if new related information
    is revealed.

    TODO: Update the distribution and involve time and age.
    TODO: Update parameters dictionary for a vast support of distributions.
    Attributes:
        reinfection_probability (float): A number between 0 and 1, very close to 0,
        determining the chance of getting the virus for the second time.

        distribution (Distribution): The distribution employed to determine the probability
        for the people infected for the first time.
    """

    def __init__(self, parameters_dict: dict):
        """Initialize the immunity disease property distribution class using a
        parameters dictionary.

        Args:
            parameters_dict (dict): The dictionary object containing the parameters.
        """
        super().__init__(parameters_dict)
        self.distribution = Uniform_Distribution(parameters_dict)
        self.reinfection_probability = 0.02

    def sample_single_random_variable(self, time: Time, person) -> float:
        """Samples a single random variable from the distribution.

        Args:
            person (Person): The person given to the distribution.
            time (Time): The time in case used in distribution.

        Returns:
            float: The sampled value.
        """
        if person.times_of_infection == 0:
            return self.distribution.sample_single_random_variable()
        else:
            return 1 - self.reinfection_probability


class Random:
    """A class to construct functions with a random nature.

    This class provides a set of methods to call whenever a random choice is needed to be
    made.

    """

    @staticmethod
    def random_choose(probability_dict, choice_size=1, replace=True):
        """Generates a random sample from a given dictionary.

        Args:
            probability_dict (dict): The input probability dictionary.
            choice_size (int, optional): The size of choosing. Defaults to 1.
            replace (bool, optional): Replace the choosing or not. Defaults to True.

        Returns:
            list: The selected sample(s).
        """
        values, probabilities = list(probability_dict.keys()), list(probability_dict.values())
        return np.random.choice(values, size=choice_size, replace=replace, p=probabilities)

    @staticmethod
    def random_choose_uniform(values, choice_size=1, replace=True):
        """Generates a random sample from a given 1-D array.

        Args:
            values (dict): The input array.
            choice_size (int, optional): The size of choosing. Defaults to 1.
            replace (bool, optional): Replace the choosing or not. Defaults to True.

        Returns:
            list: The selected sample(s).
        """
        return np.random.choice(values, size=choice_size, replace=replace)

    @staticmethod
    def flip_coin(probability):
        """Flip a coin with the given probability.

        Args:
            probability (float): Should be between 0 and 1.

        Returns:
            bool: The result of the flipping.
        """
        return np.random.uniform() < probability


if __name__ == '__main__':
    # Build local tests here
    parameters_dict = {"lower_bound": 0, "upper_bound": 1}
    uniform_dist = Uniform_Distribution(parameters_dict)

    print(uniform_dist.sample_single_random_variable())
