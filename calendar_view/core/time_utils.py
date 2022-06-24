import re
from datetime import time, date, timedelta, datetime
from typing import Tuple, Optional

from calendar_view.core.utils import StringUtils

MAX_DAYS_RANGE_ALLOWED = 15
ZERO_TIME = time(0, 0)
weekday_dict = {
    'mo': 0,
    'tu': 1,
    'we': 2,
    'th': 3,
    'fr': 4,
    'sa': 5,
    'su': 6,
    'пн': 0,
    'вт': 1,
    'ср': 2,
    'чт': 3,
    'пт': 4,
    'сб': 5,
    'вс': 6,
    'нд': 6,
}
time_regex = re.compile(r'^([0-9]{1,2})(:([0-9]{2}))?$')


def parse_time(value: str) -> Optional[time]:
    """
    Parses time value. Can be used format: 'hh:mm' or 'hh'
    """
    if StringUtils.is_blank(value):
        return None
    m = time_regex.search(value)
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


def week_day_for_date(d, weekday) -> date:
    days_ahead = weekday - d.weekday()
    return d + timedelta(days_ahead)


def current_week_day(weekday) -> date:
    return week_day_for_date(date.today(), weekday)


def parse_date(value: str) -> Optional[date]:
    """
    Allowed formats:
    'YYYY.mm.dd'
    'dd.mm.YYYY'
    'dd.mm.YY'
    'dd.mm' - current year

    Both '-', '.' and '/' can be used as delimiter.

    Allowed year range: [1900, 2100]
    Specification: ISO 8601
    """
    weekday = weekday_dict.get(value.lower())
    if weekday is not None:
        return current_week_day(weekday)

    dash = '-' in value
    dot = '.' in value
    slash = '/' in value
    sum = int(dot) + int(slash) + int(dash)
    if sum == 0:
        raise ValueError('Wrong date format: {}'.format(value))
    elif sum > 1:
        raise ValueError("Wrong date format: {}. Use only one type of separator: '-', '.' or '/'".format(value))

    parsed = value.split('-' if dash else '.' if dot else '/')
    if not (2 <= len(parsed) <= 3):
        raise ValueError('Wrong date format: {}.')

    result = _parse_date(parsed)
    if not (1900 <= result.year <= 2100):
        raise ValueError('Wrong date range: {}. Can use only dates with year from 1900 to 2100.')
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
        raise ValueError('Wrong date format: {}.')


def parse_date_interval(dates: str) -> Optional[Tuple[date, date]]:
    dates = dates.strip()
    if StringUtils.is_blank(dates):
        return None

    if ' - ' not in dates:
        one_day: date = parse_date(dates.strip())
        return one_day, one_day

    start_value, end_value = dates.split(' - ')
    start: date = parse_date(start_value.strip())
    end: date = parse_date(end_value.strip())

    if start_value.strip().lower() in weekday_dict and end_value.strip().lower() in weekday_dict and end <= start:
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
