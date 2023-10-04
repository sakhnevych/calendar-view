from datetime import datetime

from calendar_view.calendar import Calendar
from calendar_view.config import style
from calendar_view.core import data
from calendar_view.core.event import Event

style.hour_height = 80
style.event_notes_color = '#7F7F7F'

config = data.CalendarConfig(
    lang='en',
    title='Massage. Antonio',
    dates='2023-06-05 - 2023-06-11',
    show_year=True,
    mode=None,
    title_vertical_align='top'
)
events = [
    Event(start=datetime(year=2023, month=6, day=6, hour=17), end=datetime(year=2023, month=6, day=7, hour=8),
          title='#1', notes='note #1'),
    Event(start=datetime(year=2023, month=6, day=8, hour=7), end=datetime(year=2023, month=6, day=8, hour=20),
          title='#2', notes='note #2'),
]

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("b1-split_events.png")
