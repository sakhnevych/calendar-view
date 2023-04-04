from unittest import TestCase

from datetime import time, date, timedelta
from calendar_view.core import time_utils


class TestTimeUtils(TestCase):
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
        self.assertEqual(date(2019, 6, 17), time_utils.parse_date('2019-06-17'))
        self.assertEqual(date(2019, 3, 17), time_utils.parse_date('17.03.2019'))
        self.assertEqual(date(2019, 3, 2).day, time_utils.parse_date('02/03').day)
        self.assertEqual(date(2019, 3, 2).month, time_utils.parse_date('02/03').month)

        now = date.today()
        self.assertEqual(now + timedelta(0 - now.weekday()), time_utils.parse_date('Mo'))
        self.assertEqual(now + timedelta(1 - now.weekday()), time_utils.parse_date('вт'))
        self.assertEqual(now + timedelta(2 - now.weekday()), time_utils.parse_date('ср'))
        self.assertEqual(now + timedelta(3 - now.weekday()), time_utils.parse_date('th'))
        self.assertEqual(now + timedelta(4 - now.weekday()), time_utils.parse_date('Fr'))
        self.assertEqual(now + timedelta(5 - now.weekday()), time_utils.parse_date('sa'))
        self.assertEqual(now + timedelta(6 - now.weekday()), time_utils.parse_date('вс'))

        self.assertRaises(ValueError, time_utils.parse_date, 'четверг')
        self.assertRaises(ValueError, time_utils.parse_date, '2019=06=17')
        self.assertRaises(ValueError, time_utils.parse_date, '2019')
        self.assertRaises(ValueError, time_utils.parse_date, '2019.03')
        self.assertRaises(ValueError, time_utils.parse_date, '209-06-17')
        self.assertRaises(ValueError, time_utils.parse_date, '2200-06-17')

    def test_parse_date_interval(self):
        self.assertEqual((date(2019, 6, 17), date(2019, 6, 20)), time_utils.parse_date_interval('2019-06-17 - 2019-06-20'))
        self.assertEqual((date(date.today().year, 5, 20), date(date.today().year, 5, 21)), time_utils.parse_date_interval('20.05 - 21.05'))
        self.assertEqual((date(2019, 12, 30), date(2020, 1, 3)), time_utils.parse_date_interval('2019-12-30 - 2020-01-03'))
        self.assertEqual((date(2001, 4, 28), date(2001, 4, 28)), time_utils.parse_date_interval('28.04.2001'))

        start, end = time_utils.parse_date_interval('Mo - Fr')
        self.assertEqual(timedelta(days=4), end - start)
        start, end = time_utils.parse_date_interval('we - we')
        self.assertEqual(timedelta(days=7), end - start)
        start, end = time_utils.parse_date_interval('sa - mo')
        self.assertEqual(timedelta(days=2), end - start)

        self.assertRaises(ValueError, time_utils.parse_date_interval, '2019.03.21 - 2019.03.19')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '01.21 - 01.19')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '28.12 - 02.01')
        self.assertRaises(ValueError, time_utils.parse_date_interval, '2019-09-20 - 2019-10-10')
