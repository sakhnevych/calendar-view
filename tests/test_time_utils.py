from unittest import TestCase, mock

from datetime import time, date, timedelta, datetime
from calendar_view.core import time_utils


class TestTimeUtils(TestCase):
    @mock.patch('calendar_view.core.time_utils.i18n', autospec=True)
    @mock.patch('calendar_view.core.time_utils.date')
    def test_convert_weekday_to_date(self, mock_date, mock_i18n):
        # Setup mock for date.today()
        mock_date.today.return_value = date(2024, 1, 3)  # Wednesday
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Setup mock for i18n
        mock_i18n.default_lang = 'en'
        mock_i18n.supported_languages.return_value = ['en', 'de']
        mock_i18n.days_of_week.side_effect = lambda lang: {
            'en': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
            'de': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        }.get(lang, [])

        # Test with a specific language
        self.assertEqual(date(2024, 1, 3), time_utils.LocalizedWeekdayParser.convert_weekday_to_date('We', lang='en'))
        self.assertIsNone(time_utils.LocalizedWeekdayParser.convert_weekday_to_date('xx', lang='en'))

        # Test fallback to default language
        self.assertEqual(date(2024, 1, 5), time_utils.LocalizedWeekdayParser.convert_weekday_to_date('Fr', lang=None))

        # Test fallback to other supported languages
        self.assertEqual(date(2024, 1, 2), time_utils.LocalizedWeekdayParser.convert_weekday_to_date('Di', lang=None))

        # Test when token is not in any language
        self.assertIsNone(time_utils.LocalizedWeekdayParser.convert_weekday_to_date('xx', lang=None))

    def test_week_day_for_date(self):
        # Monday
        d = date(2024, 1, 1)
        self.assertEqual(date(2024, 1, 1), time_utils.week_day_for_date(d, 0))  # Monday
        self.assertEqual(date(2024, 1, 7), time_utils.week_day_for_date(d, 6))  # Sunday

        # Sunday
        d = date(2024, 1, 7)
        self.assertEqual(date(2024, 1, 1), time_utils.week_day_for_date(d, 0))  # Monday
        self.assertEqual(date(2024, 1, 7), time_utils.week_day_for_date(d, 6))  # Sunday

        # Wednesday
        d = date(2024, 1, 3)
        self.assertEqual(date(2024, 1, 1), time_utils.week_day_for_date(d, 0))
        self.assertEqual(date(2024, 1, 7), time_utils.week_day_for_date(d, 6))

    def test_current_week_day(self):
        # Mock date.today() to return a fixed date (e.g., Wednesday, Jan 3, 2024)
        with mock.patch('calendar_view.core.time_utils.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            # Monday of that week is Jan 1, 2024
            self.assertEqual(date(2024, 1, 1), time_utils.current_week_day(0))
            # Sunday of that week is Jan 7, 2024
            self.assertEqual(date(2024, 1, 7), time_utils.current_week_day(6))

    def test_is_valid_time(self):
        self.assertFalse(time_utils.is_valid_time(''))
        self.assertFalse(time_utils.is_valid_time('    '))
        self.assertFalse(time_utils.is_valid_time('zz'))
        self.assertFalse(time_utils.is_valid_time('55'))
        self.assertFalse(time_utils.is_valid_time('25'))
        self.assertFalse(time_utils.is_valid_time('-1'))
        self.assertFalse(time_utils.is_valid_time('24:01'))

        self.assertTrue(time_utils.is_valid_time('10:00'))
        self.assertTrue(time_utils.is_valid_time('00:00'))
        self.assertTrue(time_utils.is_valid_time('0'))
        self.assertTrue(time_utils.is_valid_time('00'))
        self.assertTrue(time_utils.is_valid_time('00:00'))
        self.assertTrue(time_utils.is_valid_time('1'))
        self.assertTrue(time_utils.is_valid_time('23'))
        self.assertTrue(time_utils.is_valid_time('23:59'))
        self.assertTrue(time_utils.is_valid_time('24'))
        self.assertTrue(time_utils.is_valid_time('24:00'))

    def test_parse_time(self):
        self.assertEqual(None, time_utils.parse_time(''))
        self.assertEqual(None, time_utils.parse_time('  '))

        self.assertEqual(time(0, 0), time_utils.parse_time('00:00'))
        self.assertEqual(time(5, 0), time_utils.parse_time('5'))
        self.assertEqual(time(10, 0), time_utils.parse_time('10:00'))
        self.assertEqual(time(14, 5), time_utils.parse_time('14:05'))
        self.assertEqual(time(0, 0), time_utils.parse_time('24:00'))

        self.assertRaises(ValueError, time_utils.parse_time, 'zz')
        self.assertRaises(ValueError, time_utils.parse_time, '01:60')
        self.assertRaises(ValueError, time_utils.parse_time, '-1')
        self.assertRaises(ValueError, time_utils.parse_time, '25')
        self.assertRaises(ValueError, time_utils.parse_time, '24:01')

    def test_parse_interval(self):
        self.assertEqual((time(10, 0), time(14, 0)), time_utils.parse_time_interval('10:00 - 14:00'))
        self.assertEqual((time(10, 0), time(0, 0)), time_utils.parse_time_interval('10:00 - 24:00'))
        self.assertEqual((time(10, 0), time(0, 0)), time_utils.parse_time_interval('10:00 - 00:00'))

        # -> read description, why it is so
        self.assertEqual((time(0, 0), time(0, 0)), time_utils.parse_time_interval('00:00 - 00:00'))
        self.assertEqual((time(0, 0), time(0, 0)), time_utils.parse_time_interval('24:00 - 00:00'))

        self.assertRaises(ValueError, time_utils.parse_time_interval, '10:33 - 10:33')
        self.assertRaises(ValueError, time_utils.parse_time_interval, '11:00 - 10:00')

    def test_parse_date(self):
        self.assertEqual(date(2019, 6, 17), time_utils.parse_date('2019-06-17', lang='en'))
        self.assertEqual(date(2019, 3, 17), time_utils.parse_date('17.03.2019', lang='en'))
        self.assertEqual(date(2019, 3, 2).day, time_utils.parse_date('02/03', lang='en').day)
        self.assertEqual(date(2019, 3, 2).month, time_utils.parse_date('02/03', lang='en').month)

        now = date.today()
        self.assertEqual(now + timedelta(0 - now.weekday()), time_utils.parse_date('Mo', lang=None))
        self.assertEqual(now + timedelta(1 - now.weekday()), time_utils.parse_date('вт', lang=None))
        self.assertEqual(now + timedelta(2 - now.weekday()), time_utils.parse_date('ср', lang=None))
        self.assertEqual(now + timedelta(3 - now.weekday()), time_utils.parse_date('th', lang=None))
        self.assertEqual(now + timedelta(4 - now.weekday()), time_utils.parse_date('Fr', lang=None))
        self.assertEqual(now + timedelta(5 - now.weekday()), time_utils.parse_date('sa', lang=None))
        self.assertEqual(now + timedelta(6 - now.weekday()), time_utils.parse_date('вс', lang=None))

        self.assertRaises(ValueError, time_utils.parse_date, 'четверг', None)
        self.assertRaises(ValueError, time_utils.parse_date, '2019=06=17', 'en')
        self.assertRaises(ValueError, time_utils.parse_date, '2019', 'en')
        self.assertRaises(ValueError, time_utils.parse_date, '2019.03', 'en')
        self.assertRaises(ValueError, time_utils.parse_date, '209-06-17', 'en')
        self.assertRaises(ValueError, time_utils.parse_date, '2200-06-17', 'en')

    def test_parse_date_interval(self):
        self.assertEqual((date(2019, 6, 17), date(2019, 6, 20)), time_utils.parse_date_interval('2019-06-17 - 2019-06-20', lang='en'))
        self.assertEqual((date(date.today().year, 5, 20), date(date.today().year, 5, 21)), time_utils.parse_date_interval('20.05 - 21.05', lang='en'))
        self.assertEqual((date(2019, 12, 30), date(2020, 1, 3)), time_utils.parse_date_interval('2019-12-30 - 2020-01-03', lang='en'))
        self.assertEqual((date(2001, 4, 28), date(2001, 4, 28)), time_utils.parse_date_interval('28.04.2001', lang='en'))

        start, end = time_utils.parse_date_interval('Mo - Fr', lang='en')
        self.assertEqual(timedelta(days=4), end - start)
        start, end = time_utils.parse_date_interval('we - we', lang='en')
        self.assertEqual(timedelta(days=7), end - start)
        start, end = time_utils.parse_date_interval('sa - mo', lang='en')
        self.assertEqual(timedelta(days=2), end - start)

        self.assertRaises(ValueError, time_utils.parse_date_interval, '2019.03.21 - 2019.03.19', 'en')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '01.21 - 01.19', 'en')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '28.12 - 02.01', 'en')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '2019-09-20 - 2019-10-10', 'en')

    def test_date_range_iterates_inclusive(self):
        start = date(2024, 1, 1)
        end = date(2024, 1, 3)
        self.assertEqual(
            [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            list(time_utils.date_range(start, end))
        )

    def test_date_range_invalid(self):
        with self.assertRaises(ValueError):
            list(time_utils.date_range(date(2024, 1, 5), date(2024, 1, 1)))

    def test_get_week_borders(self):
        # Wednesday, Jan 3, 2024 -> Monday is Jan 1, 2024 and Sunday is Jan 7, 2024
        dt = datetime(2024, 1, 3, 12, 0)
        start, end = time_utils.get_week_borders(dt)
        # start is date, end may be date or datetime depending on implementation; compare dates
        end_date = end.date() if hasattr(end, 'date') else end
        self.assertEqual(date(2024, 1, 1), start)
        self.assertEqual(date(2024, 1, 7), end_date)

    def test_weekday_token_detection(self):
        self.assertTrue(time_utils.LocalizedWeekdayParser.is_weekday_token('Mo', 'en'))
        self.assertTrue(time_utils.LocalizedWeekdayParser.is_weekday_token('fr', 'en'))
        self.assertFalse(time_utils.LocalizedWeekdayParser.is_weekday_token('xyz', 'en'))
