from datetime import date, timedelta
from unittest import TestCase

from calendar_view.core.config import CalendarConfig


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

    def test_get_date_range_with_days(self):
        # given
        cfg = CalendarConfig(days=3, dates=None)

        # when
        start, end = cfg.get_date_range()

        # then
        self.assertEqual(date.today(), start)
        self.assertEqual(date.today() + timedelta(days=2), end)

    def test_get_date_range_with_dates_string(self):
        # given
        cfg = CalendarConfig(lang='en', dates='2019-06-17 - 2019-06-20')

        # when
        start, end = cfg.get_date_range()

        # then
        self.assertEqual(date(2019, 6, 17), start)
        self.assertEqual(date(2019, 6, 20), end)

    def test_modes_affect_hours(self):
        cfg = CalendarConfig(mode='day_hours')
        self.assertEqual((8, 22), cfg.get_hours_range())

        cfg = CalendarConfig(mode='working_hours')
        self.assertEqual((8, 19), cfg.get_hours_range())

    def test_week_mode_sets_dates(self):
        # given
        cfg = CalendarConfig(mode='week', lang='en')

        # when
        start, end = cfg.get_date_range()

        # then
        # Should represent current week (Mon..Sun)
        today = date.today()
        expected_start = today - timedelta(days=today.weekday())
        expected_end = expected_start + timedelta(days=6)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)
