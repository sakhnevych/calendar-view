from typing import Union

from calendar_view.config import style
from calendar_view.core.config import CalendarConfig
from calendar_view.core.time_utils import *


class EventStyle(object):
    """
    Defined the style of the painted event.
    """
    def __init__(self, event_border: Tuple[int, int, int, int] = None, event_fill: Tuple[int, int, int, int] = None) -> None:
        """
        :param event_border: the color of the border as a tuple (r, g, b, a)
            Example: (120, 180, 120, 240) - green
        :param event_fill: the color of the background as a tuple (r, g, b, a)
            Example: (196, 234, 188, 180) - light green
        """
        self.event_border = event_border if event_border else style.event_border_default
        self.event_fill = event_fill if event_fill else style.event_fill_default


class EventStyles(object):
    """
    Predefined colors
    """
    GREEN = EventStyle(event_border=(120, 180, 120, 240), event_fill=(196, 234, 188, 180))
    RED = EventStyle(event_border=(220, 50, 50, 240), event_fill=(220, 50, 50, 180))
    BLUE = EventStyle(event_border=(100, 100, 220, 240), event_fill=(150, 150, 234, 180))
    GRAY = EventStyle(event_border=(110, 110, 110, 240), event_fill=(200, 200, 200, 190))


class Event(object):
    def __init__(self, name: str = None, day_of_week: int = None, day: Union[date, datetime, str] = None,
                 start: Union[datetime, time, str] = None, end: Union[datetime, time, str] = None, style: EventStyle = None) -> None:
        if day_of_week and not (0 <= day_of_week <= 6):
            raise ValueError("'day_of_week' has to be in the interval [0, 6]. Current value is: {}".format(day_of_week))

        self.name: str = name
        self.style: EventStyle = style if style else EventStyle()

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
    def __parse_start_date(day_of_week: Optional[int],
                           day: Union[date, datetime, str],
                           start: Optional[Union[datetime, time, str]]) -> Optional[date]:
        if day_of_week is not None and day is not None:
            raise ValueError("'day_of_week' is defined together with a 'day'.")
        if day_of_week is not None and (start is not None and isinstance(start, datetime)):
            raise ValueError("'day_of_week' is defined together with a 'start' as a datetime.")
        return Event.__parse_date(day_of_week, day, start)

    @staticmethod
    def __parse_end_date(day_of_week: Optional[int],
                         day: Optional[Union[date, datetime, str]],
                         end: Optional[Union[datetime, time, str]]) -> Optional[date]:
        if day_of_week is not None and day is not None:
            raise ValueError("'day_of_week' is defined together with a 'day'.")
        if day_of_week is not None and (end is not None and isinstance(end, datetime)):
            raise ValueError("'day_of_week' is defined together with a 'end' as a datetime.")
        return Event.__parse_date(day_of_week, day, end)

    @staticmethod
    def __parse_date(day_of_week: Optional[int],
                     day: Optional[Union[date, datetime, str]],
                     time_entry: Optional[Union[datetime, time, str]]) -> Optional[date]:
        if day_of_week:
            return None
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

    def get_end_date(self, config: CalendarConfig) -> date:
        if self.__end_date:
            return self.__end_date
        if config is None:
            return current_week_day(self.__day_of_week)

        start_date, end_date = config.get_date_range()
        result_date = week_day_for_date(end_date, self.__day_of_week)
        if start_date <= result_date or end_date <= result_date + timedelta(weeks=1):
            return result_date
        return result_date + timedelta(weeks=1)

    def get_duration_seconds(self, config: CalendarConfig) -> float:
        duration: timedelta = datetime.combine(self.get_end_date(config), self.end_time) - datetime.combine(self.get_start_date(config), self.start_time)
        return duration.total_seconds()

    @property
    def start_time(self) -> time:
        return self.__start_time

    @property
    def end_time(self) -> time:
        return self.__end_time
