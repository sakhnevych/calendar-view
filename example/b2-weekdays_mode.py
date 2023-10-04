from calendar_view.calendar import Calendar
from calendar_view.core import data
from calendar_view.core.event import EventStyles

config = data.CalendarConfig(
    lang='en',
    title='Test Schedule',
    dates='Sa - Th',
    hours='8 - 20',
    mode=None,
    show_date=False,
    show_year=False,
    legend=False,
)

calendar = Calendar.build(config)
calendar.add_event(day_of_week=3, start='08:00', end='17:00', style=EventStyles.GRAY)
calendar.save("b2-weekdays_mode.png")
