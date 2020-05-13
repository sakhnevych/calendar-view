from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.calendar import Calendar
from calendar_view.core.event import Event

config = CalendarConfig(
    lang='en',
    title='Yoga Class Schedule',
    dates='Mo - Su',
    hours='8 - 22',
    show_date=False,
    legend=True,
)
events = [
    Event(day_of_week=0, start='11:00', end='12:30', name='Ashtanga, 90 mins, with Gina'),
    Event(day_of_week=1, start='18:00', end='19:15', name='HOT Core Yoga, 75 mins, with David'),
    Event(day_of_week=2, start='09:00', end='10:00', name='Meditation - Yoga Nidra, 60 mins, with Heena'),
    Event(day_of_week=2, start='19:00', end='20:15', name='Hatha Yoga, 75 mins, with Jo'),
    Event(day_of_week=3, start='19:00', end='20:00', name='Pilates, 60 mins, with Erika'),
    Event(day_of_week=4, start='18:30', end='20:00', name='Kundalini Yoga, 90 mins, with Dan'),
    Event(day_of_week=5, start='10:00', end='11:15', name='Hatha Yoga, 75 mins, with Amelia'),
    Event(day_of_week=6, start='10:00', end='11:15', name='Yoga Open, 75 mins, with Klaudia'),
    Event(day_of_week=6, start='14:00', end='15:15', name='Hatha Yoga, 75 mins, with Vick'),
]

data.validate_config(config)
data.validate_events(events, config)

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("yoga_class.png")
