import calendar
from datetime import datetime, timedelta
from enum import Enum


# TODO: remove minutes from time, and use a unified timeline.

class Time:
    """A class to handle time during the simulation.

    This class provides the simulation with all the necessary timing methods, and handles
    both normal datetime objects and unix time integers. Additionally, the class has a set
    of static conversion methods, and can also work using just the minutes passed from a
    certain origin.
    ...

    Attributes:
        unix_time (int): This holds the value of current unix time in
        seconds as the baseline.

        init_date_time (datetime): This contains the starting point of
        the Time object.

    """

    def __init__(self, delta_time: timedelta, init_date_time: datetime = None):
        """Build a Time object to handle timing during the simulation.

        Args:
            delta_time (timedelta): The amount of time in the time container.
            init_date_time (datetime, optional): Initial date time to determine
            the origin of the timeline. Defaults to None.
        """
        self.init_date_time = init_date_time

        # determine the initial time point
        if self.init_date_time is None:
            self.init_date_time = Time.convert_unix_to_datetime(0)

        # set unix datetime
        self.unix_time = Time.convert_datetime_to_unix(self.init_date_time + delta_time)

    # special minutes functions since the simulator is minutes based
    def add_minutes(self, minutes):
        """Add minutes to the base time.

        Args:
            minutes (float): Input the amount of minutes to add to the base time.
        """
        self.unix_time += (minutes * 60)

    def get_minutes(self) -> int:
        """Get the elapsed minutes.

        Returns:
            float: The elapsed time in minutes.
        """
        return int((self.unix_time - Time.convert_datetime_to_unix(self.init_date_time)) // 60)

    def set_minutes(self, minutes):
        """Set the current time to an specific time in minutes.

        Args:
            minutes (float): The amount of minutes to set the current time.
        """
        self.unix_time = (minutes * 60) + Time.convert_datetime_to_unix(self.init_date_time)

    def get_total_days(self):
        """Get the total days elapsed from the origin up to the function call time.

        Returns:
            int: The number of elapsed day.
        """
        return int(self.get_minutes() / (60 * 24))

    # general functions
    def get_utc_time(self) -> datetime:
        """Get the current time in UTC format.

        Returns:
            datetime: UTC date time.
        """
        return Time.convert_unix_to_datetime(self.unix_time)

    def get_day_of_week(self):
        """Obtain the name of the day, e.g. Wednesday.

        Returns:
            WeekDays: The current weekday.
        """
        day = self.get_utc_time().weekday()
        return Week_Days(day)

    def to_json(self):
        """Convert object fields to a JSON dictionary.

        Returns:
            dict: The JSON dictionary.
        """
        minutes = self.get_minutes()
        return dict(name=self.__class__.__name__,
                    minutes=minutes,
                    unix_time=self.unix_time)

    @staticmethod
    def check_equal(time1, time2):
        """Check whether two times are equal or not.

        Args:
            time1 (Time): The first input time.
            time2 (Time): The second input time.

        Returns:
            bool: Return true the two inputs are equal.
        """
        return time1.get_minutes() == time2.get_minutes()

    @staticmethod
    def check_less(time1, time2):
        """Check whether the first time is less than the second.

        Args:
            time1 (Time): The first input time.
            time2 (Time): The second input time.

        Returns:
            bool: Return true the first one is less.
        """
        return time1.get_minutes() < time2.get_minutes()

    @staticmethod
    def convert_day_to_minutes(day):
        """Convert day to minutes.

        Args:
            day (int): The number of days.

        Returns:
            int: Amount of minutes equal to the number of days.
        """
        return 24 * 60 * day

    @staticmethod
    def convert_hour_to_minutes(hour):
        """Convert hours to minutes.

        Args:
            hour (int): Number of hours to be converted.

        Returns:
            int: Number of minutes equal to the input hour.
        """
        return 60 * hour

    @staticmethod
    def convert_minute_to_days(minute):
        """Convert minutes to days.

        Args:
            minute (int): The amount of input minutes.

        Returns:
            float: Number of days equal to the input minute.
        """
        return minute / (24 * 60)

    @staticmethod
    def convert_datetime_to_unix(date_time: datetime) -> int:
        """Convert datetime object to unix time.

        Args:
            date_time (datetime): Input datetime object.

        Returns:
            int: The unix time.
        """
        return calendar.timegm(date_time.utctimetuple())

    @staticmethod
    def convert_unix_to_datetime(unix: int) -> datetime:
        """Convert unix time to datetime object

        Args:
            unix (int): The input unix time.

        Returns:
            datetime: The datetime object.
        """
        return datetime.utcfromtimestamp(unix)


class Week_Days(Enum):
    '''An enum to hold the weekdays.

    This class is created to be used as the days enum.
    '''

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
