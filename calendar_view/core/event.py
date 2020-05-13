from datetime import datetime
from typing import Union

from calendar_view.core.config import CalendarConfig
from calendar_view.core.time_utils import *
from calendar_view.core.utils import *


class Event(object):
    def __init__(self, name: str = None, day_of_week: int = None, day: Union[date, datetime, str] = None,
                 start: Union[datetime, time, str] = None, end: Union[datetime, time, str] = None) -> None:
        if day_of_week and not (0 <= day_of_week <= 6):
            raise ValueError("'day_of_week' has to be in the interval [0, 6]. Current value is: {}".format(day_of_week))

        self.name: str = name

        # parse date of the event
        self.__start_date: date = self.__parse_start_date(day_of_week, day, start)
        self.__end_date: date = self.__parse_end_date(day_of_week, day, end)
        if self.__end_date is None:
            self.__end_date: date = self.__start_date
        if day_of_week is not None:
            self.__day_of_week: int = day_of_week
        if self.__start_date and self.__end_date and self.__end_date < self.__start_date:
            raise ValueError("Event's start date has to be before end date")

        # parse the time of the start and end of the event
        if not start:
            raise ValueError("'start' argument is required")
        self.__start_time: time = Event.__parse_time(start)
        if not end:
            raise ValueError("'end' argument is required")
        self.__end_time: time = Event.__parse_time(end)
        if self.__start_time == self.__end_time and self.__end_time < self.__start_time:
            raise ValueError("Event's start time has to be before end time")

        # run additional validation
        self.__validate()

    @staticmethod
    def __parse_start_date(day_of_week: int, day: Union[date, datetime, str], start: Union[datetime, time, str]) -> Optional[date]:
        if sum([day_of_week is not None, day is not None, start is not None and start is datetime]) != 1:
            raise ValueError("One argument from the list has to be defined: 'day_of_week'; 'day'; 'start' as a datetime value")
        return Event.__parse_date(day, start)

    @staticmethod
    def __parse_end_date(day_of_week: int, day: Union[date, datetime, str], end: Union[datetime, time, str]) -> Optional[date]:
        if sum([day_of_week is not None, day is not None, end is not None and end is datetime]) != 1:
            raise ValueError("One argument from the list has to be defined: 'day_of_week'; 'day'; 'end' as a datetime value")
        return Event.__parse_date(day, end)

    @staticmethod
    def __parse_date(day: Union[date, datetime, str], time_entry: Union[datetime, time, str]) -> Optional[date]:
        if day:
            if isinstance(day, date):
                return day
            if isinstance(day, datetime):
                return day.date()
            if isinstance(day, str):
                return parse_date(day)
        if time_entry and isinstance(time_entry, datetime):
            return time_entry.date()
        return None

    @staticmethod
    def __parse_time(time_entry: Union[datetime, time, str]) -> Optional[time]:
        if isinstance(time_entry, datetime):
            return time_entry.time()
        if isinstance(time_entry, time):
            return time_entry
        if isinstance(time_entry, str):
            return parse_time(time_entry)

    def __validate(self):
        if self.__start_date is None and self.__day_of_week is None:
            raise ValueError("Either date of the start event or the day of the week has to be defined.")
        if self.__end_date is None and self.__day_of_week is None:
            raise ValueError("Either date of the end event or the day of the week has to be defined.")

    def get_start_date(self, config: CalendarConfig) -> date:
        if self.__start_date:
            return self.__start_date
        if config is None:
            return current_week_day(self.__day_of_week)

        start_date, end_date = config.get_date_range()
        result_date = week_day_for_date(start_date, self.__day_of_week)
        if start_date <= result_date or end_date <= result_date + timedelta(weeks=1):
            return result_date
        return result_date + timedelta(weeks=1)

    @property
    def start_time(self) -> time:
        return self.__start_time

    @property
    def end_time(self) -> time:
        return self.__end_time


class EventBak(object):
    def __init__(self, name: str, day: str, day_of_week: int, start_time: str, end_time: str, interval: str) -> None:
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
