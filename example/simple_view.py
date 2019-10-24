from calendar_view.core import data
from calendar_view.calendar import Calendar

calendar = Calendar.build()
calendar.add_event(data.event(day_of_week=0, interval='08:00 - 17:00'))
calendar.add_event(data.event(day_of_week=5, interval='10:00 - 13:00'))
calendar.add_event(data.event(day_of_week=6, interval='15:00 - 18:00'))
calendar.save("simple_view.png")
