from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.calendar import Calendar
from calendar_view.core.event import Event, EventStyles

config = CalendarConfig(
    lang='en',
    title='Yoga Class Schedule',
    dates='Mo - Su',
    hours='8 - 22',
    show_date=False,
    legend=True,
)
data.validate_config(config)

events = [
    Event(day_of_week=0, start='11:00', end='12:30', name='Ashtanga, 90 mins, with Gina', style=EventStyles.GRAY),
    Event(day_of_week=1, start='18:00', end='19:15', name='HOT Core Yoga, 75 mins, with David', style=EventStyles.RED),
    Event(day_of_week=2, start='09:00', end='10:00', name='Meditation - Yoga Nidra, 60 mins, with Heena', style=EventStyles.BLUE),
    Event(day_of_week=2, start='19:00', end='20:15', name='Hatha Yoga, 75 mins, with Jo', style=EventStyles.GREEN),
    Event(day_of_week=3, start='19:00', end='20:00', name='Pilates, 60 mins, with Erika', style=EventStyles.GRAY),
    Event(day_of_week=4, start='18:30', end='20:00', name='Kundalini Yoga, 90 mins, with Dan', style=EventStyles.RED),
    Event(day_of_week=5, start='10:00', end='11:15', name='Hatha Yoga, 75 mins, with Amelia', style=EventStyles.GREEN),
    Event(day_of_week=6, start='10:00', end='11:15', name='Yoga Open, 75 mins, with Klaudia', style=EventStyles.BLUE),
    Event(day_of_week=6, start='14:00', end='15:15', name='Hatha Yoga, 75 mins, with Vick', style=EventStyles.GREEN)
]

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("yoga_class.png")
