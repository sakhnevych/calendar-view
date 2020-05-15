from calendar_view.calendar import Calendar
from calendar_view.core.event import EventStyles

calendar = Calendar.build()
calendar.add_event(day_of_week=0, start='08:00', end='17:00', style=EventStyles.GRAY)
calendar.add_event(day_of_week=5, start='10:00', end='13:00', style=EventStyles.BLUE)
calendar.add_event(day_of_week=6, start='15:00', end='18:00')
calendar.save("simple_view.png")
