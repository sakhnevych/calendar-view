from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.core.data import event
from calendar_view.calendar import Calendar

config = CalendarConfig(
    lang='en',
    title='Yoga Class Schedule',
    dates='Mo - Su',
    hours='8 - 22',
    show_date=False,
    legend=True,
)
events = [
    event(day_of_week=0, interval='11:00 - 12:30', name='Ashtanga, 90 mins, with Gina'),
    event(day_of_week=1, interval='18:00 - 19:15', name='HOT Core Yoga, 75 mins, with David'),
    event(day_of_week=2, interval='09:00 - 10:00', name='Meditation - Yoga Nidra, 60 mins, with Heena'),
    event(day_of_week=2, interval='19:00 - 20:15', name='Hatha Yoga, 75 mins, with Jo'),
    event(day_of_week=3, interval='19:00 - 20:00', name='Pilates, 60 mins, with Erika'),
    event(day_of_week=4, interval='18:30 - 20:00', name='Kundalini Yoga, 90 mins, with Dan'),
    event(day_of_week=5, interval='10:00 - 11:15', name='Hatha Yoga, 75 mins, with Amelia'),
    event(day_of_week=6, interval='10:00 - 11:15', name='Yoga Open, 75 mins, with Klaudia'),
    event(day_of_week=6, interval='14:00 - 15:15', name='Hatha Yoga, 75 mins, with Vick'),
]

data.validate_config(config)
data.validate_events(events, config)

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("yoga_class.png")
