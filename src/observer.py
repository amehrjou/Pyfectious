from typing import List

from conditions import Condition
from plot_utils import Plot
from time_handle import Time
from utils import Health_Condition, Infection_Status
from utils import Statistics


class Observer:

    def __init__(self, condition: Condition, observe_people: bool = False, observe_families: bool = False
                 , observe_communities: bool = False, observe_simulation: bool = False):
        self.condition = condition
        self.observed_simulators: List = list()
        self.observe_people = observe_people
        self.observe_families = observe_families
        self.observe_communities = observe_communities
        self.observe_simulation = observe_simulation
        self.observation_id = 0
        self.simulator = None
        self.is_deleted = False

    def observe(self, simulator, end_time: Time):
        # get satisfaction times
        self.simulator = simulator
        satisfaction_times = self.condition.is_satisfied(self.simulator, end_time)

        # save data for each satisfaction time
        for _ in satisfaction_times:

            if self.observe_people:
                self.save_people_data()

            if self.observe_families:
                # TODO: self.save_families_data()
                pass

            if self.observe_communities:
                # TODO: self.save_communities_data()
                pass

            if self.observe_simulation:
                # TODO: self.save_simulation_data()
                self.save_simulation_data()

            self.observation_id += 1

    def observation_is_done(self):
        return self.condition.is_able_to_be_removed()

    def save_simulation_data(self):
        # manipulate time to store in db
        date_time = self.simulator.clock.unix_time

        # save simulation and observer id
        observer_id = id(self)
        observation_id = self.observation_id

        stats = Statistics.get_people_statistics(self.simulator.people)

        # extract the statistics
        active_cases = stats[Health_Condition.IS_INFECTED]
        confirmed_cases = stats[Health_Condition.HAS_BEEN_INFECTED]
        death_cases = stats[Health_Condition.DEAD]

        # insert people's data into database
        self.simulator.database.insert(table_name='simulator', data=[confirmed_cases,
                                                                     death_cases,
                                                                     active_cases])
        self.simulator.database.commit()

    def save_people_data(self):
        # manipulate time to store in db
        date_time = self.simulator.clock.unix_time

        # save simulation and observer id
        observer_id = id(self)
        observation_id = self.observation_id

        columns = list()
        for person in self.simulator.people:
            # build sql column
            location = person.get_current_location()
            column = tuple([str(person.id_number),
                            str(person.age),
                            str(person.health_condition),
                            str(person.gender),
                            str(int(person.infection_status.value)),
                            str(int(person.is_alive)),
                            str(int(person.has_profession)),
                            str(person.times_of_infection),
                            str(int(person.is_quarantined)),
                            str(location[0]) + "," + str(location[1]),
                            str(observation_id),
                            str(observer_id),
                            str(date_time)])

            # append column to columns
            columns.append(column)

        # insert people's data into database
        self.simulator.database.insert_many('people', columns)

    def get_initial_ages(self):
        condition = "observer_id=? AND observation_id=?"
        condition_data = (id(self), 0)
        data = self.simulator.database.get_data(table_name='people', data="age", condition=condition,
                                                condition_data=condition_data)

        ages = [x[0] for x in data]
        return ages

    def plot_initial_hist_age(self, x_label: str = "Age", density: bool = False, fit_curve: bool = False):
        ages = self.get_initial_ages()
        Plot.plot_hist(ages, x_label, density, fit_curve)

    def get_initial_health_conditions(self):
        condition = "observer_id=? AND observation_id=?"
        condition_data = (id(self), 0)
        data = self.simulator.database.get_data(table_name='people', data="health_condition", condition=condition,
                                                condition_data=condition_data)

        health_conditions = [x[0] for x in data]
        return health_conditions

    def plot_initial_hist_health_condition(self, x_label: str = "Health Condition", density: bool = False,
                                           fit_curve: bool = False):
        health_conditions = self.get_initial_health_conditions()
        Plot.plot_hist(health_conditions, x_label, density, fit_curve)

    def plot_initial_bar_gender(self, x_label: str = "Gender"):
        condition = "observer_id=? AND observation_id=?"
        condition_data = (id(self), 0)
        data = self.simulator.database.get_data(table_name='people', data="gender", condition=condition,
                                                condition_data=condition_data)

        genders = [x[0] for x in data]
        Plot.plot_barplot(genders, x_label, ["Female", "Male"])

    def plot_specific_condition_hist_age(self, condition_id: int, person_disease_condition: Health_Condition,
                                         x_label: str = "Age", density: bool = False, fit_curve: bool = False):

        condition, condition_data = self.build_plot_condition(person_disease_condition, condition_id)
        data = self.simulator.database.get_data(table_name='people', data="age", condition=condition,
                                                condition_data=condition_data)

        ages = [x[0] for x in data]
        Plot.plot_hist(ages, x_label, density, fit_curve)

    def plot_specific_condition_hist_health_condition(self, condition_id: int,
                                                      person_disease_condition: Health_Condition,
                                                      x_label: str = "Health Condition",
                                                      density: bool = False, fit_curve: bool = False):

        condition, condition_data = self.build_plot_condition(person_disease_condition, condition_id)
        data = self.simulator.database.get_data(table_name='people', data="health_condition", condition=condition,
                                                condition_data=condition_data)

        health_conditions = [x[0] for x in data]
        Plot.plot_hist(health_conditions, x_label, density, fit_curve)

    def plot_specific_condition_barplot_gender(self, condition_id: int, person_disease_condition: Health_Condition,
                                               x_label: str = "Gender"):

        condition, condition_data = self.build_plot_condition(person_disease_condition, condition_id)
        data = self.simulator.database.get_data(table_name='people', data="gender", condition=condition,
                                                condition_data=condition_data)

        genders = [x[0] for x in data]
        Plot.plot_barplot(genders, x_label, ["Female", "Male"])

    def get_final_ages(self, person_disease_condition: Health_Condition):
        data = self.simulator.database.get_data(table_name='people', data="MAX(observation_id)",
                                                condition="observer_id=?", condition_data=(id(self),))
        last_observation_time = int(data[0][0])

        condition, condition_data = self.build_plot_condition(person_disease_condition, last_observation_time)
        data = self.simulator.database.get_data(table_name='people', data="age", condition=condition,
                                                condition_data=condition_data)

        ages = [x[0] for x in data]
        return ages

    def plot_final_hist_age(self, person_disease_condition: Health_Condition, x_label: str = "Age"
                            , density: bool = False, fit_curve: bool = False):

        ages = self.get_final_ages(person_disease_condition)
        Plot.plot_hist(ages, x_label, density, fit_curve)

    def plot_final_hist_health_condition(self, person_disease_condition: Health_Condition,
                                         x_label: str = "Health Condition",
                                         density: bool = False, fit_curve: bool = False):

        data = self.simulator.database.get_data(table_name='people', data="MAX(observation_id)",
                                                condition="observer_id=?", condition_data=(id(self),))
        last_observation_time = int(data[0][0])

        condition, condition_data = self.build_plot_condition(person_disease_condition, last_observation_time)
        data = self.simulator.database.get_data(table_name='people', data="health_condition", condition=condition,
                                                condition_data=condition_data)

        health_conditions = [x[0] for x in data]
        Plot.plot_hist(health_conditions, x_label, density, fit_curve)

    def plot_final_barplot_gender(self, person_disease_condition: Health_Condition, x_label: str = "Gender"):

        data = self.simulator.database.get_data(table_name='people', data="MAX(observation_id)",
                                                condition="observer_id=?", condition_data=(id(self),))
        last_observation_time = int(data[0][0])

        condition, condition_data = self.build_plot_condition(person_disease_condition, last_observation_time)
        data = self.simulator.database.get_data(table_name='people', data='gender', condition=condition,
                                                condition_data=condition_data)

        genders = [x[0] for x in data]
        Plot.plot_hist(genders, x_label, ["Female", "Male"])

    def build_plot_condition(self, person_disease_condition: Health_Condition, observation_id: int):
        condition, condition_data = None, None

        if person_disease_condition is Health_Condition.IS_INFECTED:
            condition = "observer_id=? AND observation_id=? AND infection_status!=?"
            condition_data = (id(self), observation_id, 0)
        elif person_disease_condition is Health_Condition.IS_NOT_INFECTED:
            condition = "observer_id=? AND observation_id=? AND infection_status=?"
            condition_data = (id(self), observation_id, 0)
        elif person_disease_condition is Health_Condition.HAS_BEEN_INFECTED:
            condition = "observer_id=? AND observation_id=? AND times_of_infection<>?"
            condition_data = (id(self), observation_id, 0)
        elif person_disease_condition is Health_Condition.HAS_NOT_BEEN_INFECTED:
            condition = "observer_id=? AND observation_id=? AND times_of_infection=?"
            condition_data = (id(self), observation_id, 0)
        elif person_disease_condition is Health_Condition.ALIVE:
            condition = "observer_id=? AND observation_id=? AND is_alive=?"
            condition_data = (id(self), observation_id, 1)
        elif person_disease_condition is Health_Condition.DEAD:
            condition = "observer_id=? AND observation_id=? AND is_alive=?"
            condition_data = (id(self), observation_id, 0)
        elif person_disease_condition is Health_Condition.ALL:
            condition = "observer_id=? AND observation_id=?"
            condition_data = (id(self), observation_id)
        else:
            raise ValueError('person disease condition not recognized!')

        return condition, condition_data

    def to_json(self):
        return dict(name=self.__class__.__name__,
                    condition=self.condition,
                    observe_people=self.observe_people,
                    observe_families=self.observe_families,
                    observe_communities=self.observe_communities)

    def get_health_statistics(self, person_disease_condition: Health_Condition, observation_id: int):
        condition, condition_data = self.build_plot_condition(person_disease_condition, observation_id)
        data = self.simulator.database.count_data(table_name='people', data='date_time', count_data='*',
                                                  condition=condition, condition_data=condition_data)
        stat_count, time = data[0][1], data[0][0]

        if stat_count == 0:
            # get the time matched with observation_id
            condition, condition_data = self.build_plot_condition(Health_Condition.ALL, observation_id)
            data = self.simulator.database.get_data(table_name='people', data='date_time', condition=condition,
                                                    condition_data=condition_data)

            # extract time from database rows
            time = data[0][0]

        return stat_count, time

    def get_disease_statistics_during_time(self, person_disease_condition: Health_Condition):
        times = list()
        statistics_over_time = list()

        for observation_id in range(self.observation_id):
            stat_count, time = self.get_health_statistics(person_disease_condition, observation_id)
            times.append(Time.convert_unix_to_datetime(time))
            statistics_over_time.append(stat_count)

        return statistics_over_time, times

    def plot_disease_statistics_during_time(self, person_disease_condition: Health_Condition):
        statistics_over_time, times = self.get_disease_statistics_during_time(person_disease_condition)

        Plot.plot_line(times, statistics_over_time, "Simulation Time",
                       f'Number of {self.translate_person_disease_condition(person_disease_condition)} People',
                       f'Statistics of {self.translate_person_disease_condition(person_disease_condition)} People')

    def translate_person_disease_condition(self, person_disease_condition: Health_Condition):
        if person_disease_condition is Health_Condition.IS_INFECTED:
            return "Diseased"
        elif person_disease_condition is Health_Condition.IS_NOT_INFECTED:
            return "Healthy"
        elif person_disease_condition is Health_Condition.HAS_BEEN_INFECTED:
            return "Confirmed"
        elif person_disease_condition is Health_Condition.HAS_NOT_BEEN_INFECTED:
            return "Not Confirmed"
        elif person_disease_condition is Health_Condition.ALIVE:
            return "Alive"
        elif person_disease_condition is Health_Condition.DEAD:
            return "Dead"

        return person_disease_condition

    def plot_simple_map(self, condition_id: int):
        Xs = list()
        Ys = list()
        colors = list()
        for person in self.observed_simulators[condition_id]["people"]:
            if person.is_alive:
                x, y = person.get_current_location()
                Xs.append(x)
                Ys.append(y)
                if person.infection_status is not Infection_Status.CLEAN:
                    colors.append("r")
                else:
                    colors.append("g")
        Plot.plot_map(Xs, Ys, colors)

    def plot_simple_map_with_communities(self, condition_id: int):
        Xs = list()
        Ys = list()
        colors = list()
        for person in self.observed_simulators[condition_id]["people"]:
            if person.is_alive:
                x, y = person.get_current_location()
                Xs.append(x)
                Ys.append(y)
                if person.infection_status is not Infection_Status.CLEAN:
                    colors.append("r")
                else:
                    colors.append("g")

        communities_x = list()
        communities_y = list()
        community_sizes = list()
        all_communities = list()
        for community_list in self.observed_simulators[condition_id]["communities"].values():
            all_communities.extend(community_list)
        for community in all_communities:
            x, y = community.location
            communities_x.append(x)
            communities_y.append(y)
            community_sizes.append(100 * community.size)

        Plot.plot_map_with_communities(Xs, Ys, colors, communities_x, communities_y, community_sizes)
