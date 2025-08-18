import logging
import re
from datetime import time, date, timedelta, datetime
from typing import Tuple, Optional

from calendar_view.config import i18n
from calendar_view.core.utils import StringUtils

logger = logging.getLogger(__name__)

MAX_DAYS_RANGE_ALLOWED = 15
ZERO_TIME = time(0, 0)
TIME_REGEX = re.compile(r'^([0-9]{1,2})(:([0-9]{2}))?$')


class LocalizedWeekdayParser:
    warning_logged: bool = False

    @staticmethod
    def _localized_weekday_dict(lang: str) -> dict[str, int]:
        """
        Returns a mapping of lowercase localised weekday abbreviations to weekday indices [0..6]
        for the given language.
        """
        localized: list[str] = [s.lower() for s in i18n.days_of_week(lang)]
        return {name: idx for idx, name in enumerate(localized)}

    @staticmethod
    def _try_convert_weekday_to_date(value: str, lang: str) -> Optional[date]:
        mapping: dict[str, int] = LocalizedWeekdayParser._localized_weekday_dict(lang)
        weekday: Optional[int] = mapping.get(value.lower())
        if weekday is not None:
            return current_week_day(weekday)
        return None

    @staticmethod
    def _fallback_parse_localized_weekday(value: str) -> Optional[date]:
        for lang in i18n.supported_languages():
            result: Optional[date] = LocalizedWeekdayParser._try_convert_weekday_to_date(value, lang)
            if result:
                return result
        return None

    @staticmethod
    def convert_weekday_to_date(value: str, lang: Optional[str]) -> Optional[date]:
        """
        If 'value' matches a weekday language-specific token,
        return the corresponding current week date, else None.

        The fallback logic if the language is not configured. This may happen when the event is create
        as a separate object outside the calendar object and the weekday names are used.
        For example,
        ```
        config = CalendarConfig(..)
        events = [
          Event(day='Tu', start='11:00', end='12:30', title='Test title'),
          ..
        ]
        calendar = Calendar.build(config)
        calendar.add_events(events)
        calendar.save("yoga_class.png")
        ```
        """
        if lang:
            return LocalizedWeekdayParser._try_convert_weekday_to_date(value, lang)

        # The fallback logic if the language is not configured (events outside the Calendar object).
        result: Optional[date] = LocalizedWeekdayParser._try_convert_weekday_to_date(value, i18n.default_lang)
        if result:
            return result
        result: Optional[date] = LocalizedWeekdayParser._fallback_parse_localized_weekday(value)
        if result is not None and not LocalizedWeekdayParser.warning_logged:
            logger.warning(f"Fallback date parsing is used in all supported languages. It is most likely that "
                           f"the event you created is a separate entity for which no language has been defined. "
                           f"Date parsing may be incorrect if the language is not '{i18n.default_lang}'.")
            LocalizedWeekdayParser.warning_logged = True
        return result

    @staticmethod
    def is_weekday_token(value: str, lang: str) -> bool:
        mapping: dict[str, int] = LocalizedWeekdayParser._localized_weekday_dict(lang)
        return value.lower() in mapping


def parse_time(value: str) -> Optional[time]:
    """
    Parses time value. Can be used format: 'hh:mm' or 'hh'
    """
    if StringUtils.is_blank(value):
        return None
    m = TIME_REGEX.search(value)
    if m is None:
        raise ValueError("Wrong time format: {}. Use: 'hh:mm' or 'hh'".format(value))
    hour = int(m.group(1))
    minute_match = m.group(3)
    minute = int(minute_match) if minute_match else 0
    if hour == 24 and minute == 0:
        hour = 0
    if (0 <= hour <= 23) and (0 <= minute <= 59):
        return time(hour=hour, minute=minute)
    else:
        raise ValueError("Wrong time format: {}. Use: 'hh:mm' or 'hh'".format(value))


def is_valid_time(value: str) -> bool:
    try:
        return parse_time(value) is not None
    except ValueError:
        return False


def parse_time_interval(interval: str) -> Optional[Tuple[time, time]]:
    """
    Important: If both start and end date is 00:00 or 24:00, the interval will be the full day 924 hours)
    """
    interval = interval.strip()
    if interval is None:
        return None
    if '-' not in interval:
        raise ValueError('Wrong interval format: {}. Use: \'hh:mm - hh:mm\''.format(interval))

    start_value, end_value = interval.split('-')
    start = parse_time(start_value.strip())
    end = parse_time(end_value.strip())

    if end <= start and end != ZERO_TIME:
        raise ValueError('Start time has to be before end time: {} - {}'.format(start, end))

    return start, end


def week_day_for_date(d, weekday: int) -> date:
    days_ahead = weekday - d.weekday()
    return d + timedelta(days_ahead)


def current_week_day(weekday: int) -> date:
    return week_day_for_date(date.today(), weekday)


def parse_date(value: str, lang: Optional[str]) -> Optional[date]:
    """
    Allowed formats:
    'YYYY-mm-dd'
    'YYYY.mm.dd'
    'dd.mm.YYYY'
    'dd.mm.YY'
    'dd.mm' - current year

    Both '-', '.' and '/' can be used as delimiter.

    Allowed year range: [1900, 2100]
    Specification: ISO 8601
    """
    weekday_date: Optional[date] = LocalizedWeekdayParser.convert_weekday_to_date(value, lang)
    if weekday_date is not None:
        return weekday_date
    elif value.isalpha():
        raise ValueError(f'Cannot parse the weekday name for the language "{lang}": {value}')

    dash = '-' in value
    dot = '.' in value
    slash = '/' in value
    sum: int = int(dot) + int(slash) + int(dash)
    if sum == 0:
        raise ValueError(f'Wrong date format: {value}')
    elif sum > 1:
        raise ValueError(f"Wrong date format: {value}. Use only one type of separator: '-', '.' or '/'")

    parsed = value.split('-' if dash else '.' if dot else '/')
    if not (2 <= len(parsed) <= 3):
        raise ValueError(f'Wrong date format: {value}.')

    result = _parse_date(parsed)
    if not (1900 <= result.year <= 2100):
        raise ValueError(f'Wrong date range: {value}. Can use only dates with year from 1900 to 2100.')
    return result


def _parse_date(parsed: list) -> date:
    try:
        # format 'dd.mm'
        if len(parsed) == 2:
            return date(year=date.today().year, month=int(parsed[1]), day=int(parsed[0]))

        # format 'YYYY.mm.dd'
        if len(parsed[0]) == 4:
            return date(year=int(parsed[0]), month=int(parsed[1]), day=int(parsed[2]))

        # format 'dd.mm.YYYY'
        if len(parsed[2]) == 4:
            return date(year=int(parsed[2]), month=int(parsed[1]), day=int(parsed[0]))

        # format 'dd.mm.YY'
        if len(parsed[2]) == 2:
            return date(year=int(parsed[2]), month=int(parsed[1]), day=int(parsed[0]))
    except ValueError:
        pass
    raise ValueError(f'Wrong date format: {parsed}')


def parse_date_interval(dates: str, lang: str) -> Optional[Tuple[date, date]]:
    dates = dates.strip()
    if StringUtils.is_blank(dates):
        return None

    if ' - ' not in dates:
        one_day: date = parse_date(dates.strip(), lang=lang)
        return one_day, one_day

    start_value, end_value = dates.split(' - ')
    start_str = start_value.strip()
    end_str = end_value.strip()
    start: date = parse_date(start_str, lang=lang)
    end: date = parse_date(end_str, lang=lang)

    # If both tokens are weekday names and end <= start, treat it as a range within the next week
    if LocalizedWeekdayParser.is_weekday_token(start_str, lang) \
            and LocalizedWeekdayParser.is_weekday_token(end_str, lang) and end <= start:
        end = end + timedelta(weeks=1)

    if end <= start:
        raise ValueError('Start date has to be before end date: {} - {}'.format(start, end))
    if (end - start).days > MAX_DAYS_RANGE_ALLOWED:
        raise ValueError('Maximum allowed range of days is {}. But {} is configured.'.format(MAX_DAYS_RANGE_ALLOWED, (end - start).days))

    return start, end


def date_range(start_date: date, end_date: date):
    """
    Iterate through dates.
    """
    if end_date < start_date:
        raise ValueError(f'{start_date} is after the {end_date}')
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def get_week_borders(any_time: datetime) -> Tuple[date, date]:
    """
    Returns the start end the end of the week.
    """
    start: datetime = any_time - timedelta(days=any_time.weekday())
    return start.date(), start + timedelta(days=6)
