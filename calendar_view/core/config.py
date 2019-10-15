from typing import Tuple, List
from datetime import date, timedelta

from calendar_view.core import utils, time_utils


class CalendarConfig:
    """
    Mode will override some parameters.
    Available modes:
    'auto' - modes 'week' + 'day_hours'
    'week' - show current week
    'day_hours' - show hours range '8:00 - 22:00'
    'working_hours' - show hours range '8:00 - 19:00'
    """
    def __init__(self,
                 lang: str = 'en',
                 title: str = '',
                 dates: str = None,
                 days: int = 7,
                 hours: str = None,
                 mode: str = None,
                 show_date: bool = True,
                 show_year: bool = False,
                 legend: bool = None
                 ):
        self.lang = lang
        self.title = title
        self.dates = dates
        self.days = days
        self.hours = hours
        self.mode = mode
        self.show_date = show_date
        self.show_year = show_year
        self.legend = legend
        self._configure_mode()

    def _configure_mode(self):
        if self.mode is None:
            return
        modes: List[str] = self.mode.replace(' ', '').split(',')
        if 'auto' in modes:
            modes.append('week')
            modes.append('day_hours')
        if 'week' in modes:
            self.dates = '{} - {}'.format(
                time_utils.current_week_day(0).strftime('%Y-%m-%d'),
                time_utils.current_week_day(6).strftime('%Y-%m-%d')
            )
        if 'day_hours' in modes:
            self.hours = '8:00 - 22:00'
        if 'working_hours' in modes:
            self.hours = '8:00 - 19:00'

    def validate(self):
        if utils.is_blank(self.lang):
            raise Exception("Parameter 'lang' is empty. Language has to be specified")
        if not (0 < self.days <= 14):
            raise Exception("Parameter 'days' can be in interval [1, 14]")
        self.get_hours_range()
        self.get_date_range()
        if self.dates and self.days:
            # TODO [OS]: Add warn
            pass
        if self.show_year and not self.show_date:
            # TODO [OS]: Add warn
            pass

    def get_date_range(self) -> Tuple[date, date]:
        """
        Returns tuple of start and end day for visualisation. For example: 'date(2019, 05, 17), date(2019, 05, 20)'
        """
        if utils.is_not_blank(self.dates):
            return time_utils.parse_date_interval(self.dates)
        if self.days:
            return date.today(), date.today() + timedelta(days=self.days)
        # TODO [OS] log default value - Date range is not defined
        return time_utils.current_week_day(0), time_utils.current_week_day(6)

    def get_hours_range(self) -> Tuple[int, int]:
        """
        Returns tuple of start and end hour for visualisation. For example: '10, 18'
        """
        if utils.is_blank(self.hours):
            return 0, 24

        start, end = time_utils.parse_time_interval(self.hours)
        fixed_end = end.hour if end.minute == 0 else end.hour + 1
        if fixed_end == 0:
            fixed_end = 24

        return start.hour, fixed_end
