from calendar_view.calendar import Calendar
from calendar_view.config import style
from calendar_view.core import data
from calendar_view.core.event import Event

style.hour_height = 80
style.event_notes_color = '#7F7F7F'

config = data.CalendarConfig(
    lang='en',
    title='Massage. Antonio',
    dates='2022-06-20 - 2022-06-24',
    show_year=True,
    mode='working_hours',
    title_vertical_align='top'
)
events = [
    Event(day='2022-06-20', start='11:00', end='12:00', title='Jesse Tyson'),
    Event(day='2022-06-20', start='12:30', end='14:00', title='Karry', notes='No music'),
    Event(day='2022-06-20', start='15:00', end='17:00', title='Taylor Davis',
          notes='Ask about the shin that hurts last time.'),
    Event(day='2022-06-20', start='17:30', end='18:30', title='Jose Hope'),

    Event(day='2022-06-22', start='10:00', end='12:00', title='Annabell Moore',
          notes='A therapist for her mother:\n+4487498375 Nick Adams'),
    Event(day='2022-06-22', start='12:30', end='14:00', title='Carlos Cassidy'),
    Event(day='2022-06-22', start='15:00', end='17:00', title='Joe'),
    Event(day='2022-06-22', start='17:30', end='18:30', title='Jose Hope'),

    Event(day='2022-06-23', start='10:00', end='11:00', title='Elena Miller'),
    Event(day='2022-06-23', start='11:30', end='13:30', title='Karry', notes='No music'),
    Event(day='2022-06-23', start='15:00', end='16:30', title='Mia Williams'),
    Event(day='2022-06-23', start='17:00', end='18:00', title='Xander'),
]

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("massage.png")
