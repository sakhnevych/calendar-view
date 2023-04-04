from unittest import TestCase

from calendar_view.core.data import CalendarConfig


class TestCalendarConfig(TestCase):
    def test_get_hours_range(self):
        self.assertEqual((0, 24), CalendarConfig(hours=None).get_hours_range())
        self.assertEqual((0, 24), CalendarConfig(hours='').get_hours_range())
        self.assertEqual((0, 24), CalendarConfig(hours='  ').get_hours_range())

        self.assertEqual((0, 24), CalendarConfig(hours='0 - 24').get_hours_range())
        self.assertEqual((0, 24), CalendarConfig(hours='0-24').get_hours_range())

        self.assertEqual((2, 23), CalendarConfig(hours='2 - 23').get_hours_range())
        self.assertEqual((4, 17), CalendarConfig(hours='4:00 - 17:00').get_hours_range())
        self.assertEqual((4, 18), CalendarConfig(hours='4:00 - 17:01').get_hours_range())

        self.assertRaises(ValueError, CalendarConfig(hours='8').get_hours_range)
        self.assertRaises(ValueError, CalendarConfig(hours='6:00').get_hours_range)
        self.assertRaises(ValueError, CalendarConfig(hours='4:00 - 4:00').get_hours_range)
        self.assertRaises(ValueError, CalendarConfig(hours='15:00 - 10:00').get_hours_range)
        self.assertRaises(ValueError, CalendarConfig(hours='15:00 - 14:55').get_hours_range)
