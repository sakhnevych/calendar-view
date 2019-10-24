from calendar_view.core import data
from calendar_view.calendar import Calendar

config = data.CalendarConfig(
    lang='en',
    title='Sprint 23',
    dates='2019-09-23 - 2019-09-27',
    show_year=True,
    mode='working_hours',
    legend=False,
)
events = [
    data.event('Planning', date='2019-09-23', interval='11:00 - 13:00'),
    data.event('Demo', date='2019-09-27', interval='15:00 - 16:00'),
    data.event('Retrospective', date='2019-09-27', interval='17:00 - 18:00'),
]

data.validate_config(config)
data.validate_events(events, config)

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("sprint_23.png")
