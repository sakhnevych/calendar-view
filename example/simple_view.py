from calendar_view.calendar import Calendar

calendar = Calendar.build()
calendar.add_event(day_of_week=0, start='08:00', end='17:00')
calendar.add_event(day_of_week=5, start='10:00', end='13:00')
calendar.add_event(day_of_week=6, start='15:00', end='18:00')
calendar.save("simple_view.png")
