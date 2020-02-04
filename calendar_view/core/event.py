from calendar_view.core.config import CalendarConfig
from calendar_view.core.time_utils import *
from calendar_view.core.utils import *


class Event:
    def __init__(self, name: str, day: str, day_of_week: int, start_time: str, end_time: str, interval: str):
        self.name = name
        self.day = day
        self.day_of_week = day_of_week
        self.__start_time = start_time
        self.__end_time = end_time
        self.interval = interval

    def validate(self):
        if is_not_blank(self.interval) and (is_not_blank(self.__start_time) or is_not_blank(self.__end_time)):
            raise Exception("Start or end time couldn't be defined, if 'interval' exists.")
        if is_blank(self.interval) and is_blank(self.__start_time) and is_blank(self.__end_time):
            raise Exception("At least 'interval' or 'start'-'end' values has to be defined for event.")
        if self.day is None and self.day_of_week is None:
            raise Exception("At least one value has to be specified: 'date' or 'day_of_week'")
        if self.day is not None and self.day_of_week is not None:
            raise Exception("Only one value can be specified: 'date' or 'day_of_week'")
        if self.day_of_week is not None and not (0 <= self.day_of_week <= 6):
            raise Exception("'day_of_week' has to be in the interval [0, 6]. Current value is: {}".format(self.day_of_week))
        if is_not_blank(self.__start_time) or is_not_blank(self.__end_time):
            parse_time_interval('{} - {}'.format(self.__start_time, self.end_time))

    def get_date(self, config: CalendarConfig) -> date:
        if is_not_blank(self.day):
            return parse_date(self.day)
        if config is None:
            return current_week_day(self.day_of_week)

        start_date, end_date = config.get_date_range()
        result_date = week_day_for_date(start_date, self.day_of_week)
        if start_date <= result_date or end_date <= result_date + timedelta(weeks=1):
            return result_date
        return result_date + timedelta(weeks=1)

    @property
    def start_time(self) -> time:
        if is_not_blank(self.__start_time):
            return parse_time(self.__start_time)
        return parse_time_interval(self.interval)[0]

    @property
    def end_time(self) -> time:
        if is_not_blank(self.__end_time):
            return parse_time(self.__end_time)
        return parse_time_interval(self.interval)[1]
