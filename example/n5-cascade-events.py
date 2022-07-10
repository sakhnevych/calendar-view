from calendar_view.calendar import Calendar
from calendar_view.config import style
from calendar_view.core import data
from calendar_view.core.event import Event

style.hour_height = 80
style.day_width = 600
style.event_notes_color = '#7F7F7F'

config = data.CalendarConfig(
    lang='en',
    title='Massage. Antonio',
    dates='2022-06-22 - 2022-06-24',
    show_year=True,
    mode='working_hours',
    title_vertical_align='top'
)
events = [
    Event(day='2022-06-23', start='10:00', end='12:00', title='Elena Miller'),
    Event(day='2022-06-23', start='11:00', end='13:00', title='Karry', notes='No music'),
    Event(day='2022-06-23', start='14:30', end='16:00', title='Selena', notes='No music'),
    Event(day='2022-06-24', start='11:00', end='13:00', title='SUSUSUS', notes='No music'),
    Event(day='2022-06-24', start='14:30', end='16:30', title='Serenada', notes='No music'),
    Event(day='2022-06-22', start='14:30', end='16:30', title='KArman', notes='No music'),
    Event(day='2022-06-22', start='10:30', end='15:30', title='Zareboba', notes='No music'),
    #Event(day='2022-06-23', start='15:00', end='16:30', title='Mia Williams'),
    #Event(day='2022-06-23', start='17:00', end='18:00', title='Xander'),
]

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("massage-cascade.png")