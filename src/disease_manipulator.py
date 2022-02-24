from typing import Dict

from distributions import Disease_Property_Distribution
from logging_settings import logger
from population_generator import Person
from time_handle import Time


class Disease_Properties:
    """A class containing the main attributes of a disease.

    This class contains the data required to simulate the disease
    spread. This data is in the form of distributions.

    Attributes:
        infectious_rate_distribution (Disease_Property_Distribution): The
        distribution explaining infectious rate.

        immunity_distribution (Disease_Property_Distribution): The distribution
        of people's immunity.

        disease_period_distribution (Disease_Property_Distribution): This holds
        the distribution of infectious period.

        incubation_period_distribution (Disease_Property_Distribution): The distribution
            of incubation period.

        death_probability_distribution (Disease_Property_Distribution): This
        determines the probability that the virus kills someone.

        infectious_rate_dict (dict): A dictionary for infectious rates.
        immunity_dict (dict): A dictionary for immunities.

    """

    def __init__(self, infectious_rate_distribution: Disease_Property_Distribution,
                 immunity_distribution: Disease_Property_Distribution,
                 disease_period_distribution: Disease_Property_Distribution,
                 death_probability_distribution: Disease_Property_Distribution,
                 incubation_period_distribution: Disease_Property_Distribution,
                 hospitalization_probability_distribution: Disease_Property_Distribution or None = None):
        """Initialize a disease properties object and create infectious and immunity
        dictionaries.

        Args:
            infectious_rate_distribution (Disease_Property_Distribution): The
            distribution explaining infectious rate.

            immunity_distribution (Disease_Property_Distribution): The distribution
            of people's immunity.

            disease_period_distribution (Disease_Property_Distribution): This holds
            the distribution of infectious period.

            incubation_period_distribution (Disease_Property_Distribution): The distribution
            of incubation period.

            death_probability_distribution (Disease_Property_Distribution): This
            determines the probability that the virus kills someone.

            hospitalization_probability_distribution (Disease_Property_Distribution): Sampling from
            this distribution results in getting a probability of hospitalization between 0 and 1.
            Defaults to None.
        """
        self.immunity_distribution = immunity_distribution
        self.infectious_rate_distribution = infectious_rate_distribution
        self.disease_period_distribution = disease_period_distribution
        self.death_probability_distribution = death_probability_distribution
        self.incubation_period_distribution = incubation_period_distribution
        self.hospitalization_probability_distribution = hospitalization_probability_distribution

        self.infectious_rate_dict: Dict[int, float] = {}
        self.immunity_dict: Dict[int, float] = {}

        logger.info('Disease Properties generated')

    def clear_cache(self, person: Person):
        """Clear the values of infectious rate and immunity dictionaries.

        Args:
            person (Person): The keys in dictionaries which their values will be cleaned.
        """
        if person.id_number in self.infectious_rate_dict.keys():
            del self.infectious_rate_dict[person.id_number]
        if person.id_number in self.immunity_dict.keys():
            del self.immunity_dict[person.id_number]

    def generate_infectious_rate(self, time: Time, person: Person, simulator):
        """Generate a normalized infectious rate.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the rate is generated.
            simulator (Simulator): The simulator object.

        Returns:
            float: The infectious rate.
        """
        period = simulator.spread_period.get_minutes()
        if person.id_number not in self.infectious_rate_dict.keys():
            self.infectious_rate_dict[person.id_number] = \
                self.infectious_rate_distribution.sample_single_random_variable(time, person)

        return Disease_Properties.standard_prob(self.infectious_rate_dict[person.id_number], period)

    def generate_immunity(self, time: Time, person: Person, simulator):
        """Generate a normalized immunity probability.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the probability is generated.
            simulator (Simulator): The simulator object.

        Returns:
            float: The immunity probability.
        """
        period = simulator.spread_period.get_minutes()
        if person.id_number not in self.immunity_dict.keys():
            self.immunity_dict[person.id_number] = \
                self.immunity_distribution.sample_single_random_variable(time, person)

        return Disease_Properties.standard_prob(self.immunity_dict[person.id_number], period)

    def generate_incubation_period(self, time: Time, person: Person):
        """Generate an incubation period based on the given distribution.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the period is generated.

        Returns:
            float: Period of incubation.
        """
        return self.incubation_period_distribution.sample_single_random_variable(time, person)

    def generate_hospitalization_prob(self, time: Time, person: Person):
        """Sample the distribution representing the possibility of hospitalization.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the period is generated.

        Returns:
            float: Probability of hospitalization.
        """
        sample = 0.00
        if self.hospitalization_probability_distribution is not None:
            sample = self.hospitalization_probability_distribution.sample_single_random_variable(time, person)

        return sample

    def generate_disease_period(self, time: Time, person: Person):
        """Generate a disease period based on the disease period distribution.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the period is generated.

        Returns:
            float: Period of the disease.
        """
        return self.disease_period_distribution.sample_single_random_variable(time, person)

    def generate_death_probability(self, time: Time, person: Person):
        """Generate a death probability based non the death probability distribution.

        Args:
            time (Time): Current time in case it affects the distribution.
            person (Person): The person for whom the probability is generated.

        Returns:
            float: Probability of death.
        """
        return self.death_probability_distribution.sample_single_random_variable(time, person)

    @staticmethod
    def standard_prob(probability, period):
        """Standardize the given probability with respect to period.

        Args:
            probability (float): The given probability.
            period (float): The spread period for standardization.

        Returns:
            float: The standard probability.
        """
        probability_windows = 720
        return 1 - (1 - probability) ** (period / probability_windows)

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        return dict(name=self.__class__.__name__,
                    infectious_rate_distribution=self.infectious_rate_distribution,
                    immunity_distribution=self.immunity_distribution,
                    disease_period_distribution=self.disease_period_distribution,
                    death_probability_distribution=self.death_probability_distribution,
                    incubation_period_distribution=self.incubation_period_distribution)
