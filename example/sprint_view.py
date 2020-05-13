from calendar_view.calendar import Calendar
from calendar_view.core import data
from calendar_view.core.event import Event

config = data.CalendarConfig(
    lang='en',
    title='Sprint 23',
    dates='2019-09-23 - 2019-09-27',
    show_year=True,
    mode='working_hours',
    legend=False,
)
events = [
    Event('Planning', day='2019-09-23', start='11:00', end='13:00'),
    Event('Demo', day='2019-09-27', start='15:00', end='16:00'),
    Event('Retrospective', day='2019-09-27', start='17:00', end='18:00'),
]

data.validate_config(config)
data.validate_events(events, config)

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("sprint_23.png")
