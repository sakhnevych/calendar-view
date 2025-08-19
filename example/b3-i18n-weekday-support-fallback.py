from calendar_view.calendar import Calendar
from calendar_view.core.data import CalendarConfig
from calendar_view.core.event import EventStyles, Event

config = CalendarConfig(
    lang='fr',
    title='Test Schedule',
    dates='Lun - Ven',
    hours='8 - 20',
    mode=None,
    show_date=False,
    show_year=False,
    legend=False,
)

events = [
    Event(day='Lun', start='12:00', end='14:00', title='My first event', style=EventStyles.GREEN),
    Event(day='Mer', start='17:00', end='18:30', title='The most important meeting', style=EventStyles.RED),
]

calendar = Calendar.build(config)
calendar.add_events(events)

calendar.save("b3-i18n-weekday-support-fallback.png")
