.. image:: https://img.shields.io/pypi/v/calendar-view.svg
   :target: https://pypi.org/project/calendar-view/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/calendar-view.svg
   :target: https://pypi.org/project/calendar-view/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/dm/calendar-view
   :target: https://pypi.org/project/calendar-view/
   :alt: PyPi Package Monthly Download

.. image:: https://img.shields.io/pypi/l/calendar-view.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License


=============
Calendar View
=============

Library provides a graphical view of the calendar. View, title and events can be easily configured.

The output in ``*.png`` file.


Input parameters
================

Configuration
-------------

Configuration for the all view can be done using ``CalendarConfig`` class.

.. csv-table::
   :header: "Parameter", "Type", "Description"
   :widths: 17, 10, 73

   ``lang``, str, "Language, which is used for name of the weekday. Supported values: en, ru, ua. Default value: **en**"
   ``title``, str, "Title of the view. Can be empty"
   ``dates``, str, "The range of the days to show. Default value: **'Mo - Su'**"
   ``days``, int, "If ``dates`` does not exist, the number of days to display can be configured starting from Monday. For example, '4' means ``dates='Mo - Th'``"
   ``hours``, str, "Hour range to display"
   ``mode``, str, "Mode will override some parameters. Available modes:
    - 'week' - show current week
    - 'day_hours' - show hours range '8:00 - 22:00'
    - 'working_hours' - show hours range '8:00 - 19:00'
    - 'auto' - modes 'week' + 'day_hours'"
   ``show_date``, bool, "Defines is the date has to be shown. Format: ``'dd.mm'`` or ``'dd.mm.YYYY'`` if ``show_year=True``. Default value: **True**"
   ``show_year``, bool, "Defines is the year has to be added to the date format. Omitted if ``show_date=False``. Default value: **False**"
   ``legend``, bool, "If ``False`` - draw the name of the event inside the block. If ``True`` - draw the name in the legend. If not defined, will be chosen automatically."

Example:

.. code-block:: python

    config = CalendarConfig(
        lang='en',
        title='Yoga Class Schedule',
        dates='Mo - Fr',
        hours='8 - 22',
        mode=None,
        show_date=True,
        show_year=False,
        legend=True,
    )

    # you can validate your config
    validate_config(config)


Event
-----

.. csv-table::
   :header: "Parameter", "Type", "Description"
   :widths: 20, 10, 70

   ``name``, str, "Language, which is used for name of the weekday. Supported values: en, ru, ua"
   ``day``, str, "Title of the view. Can be empty"
   ``day_of_week``, int, "The range of the days to show."
   ``start_time``, str, "Start of the event in format **HH:mm** or **HH**. Can't be used together with ``interval``."
   ``end_time``, str, "End of the event in format **HH:mm** or **HH**. Can't be used together with ``interval``."
   ``interval``, str, "Start and end of the event in format **HH:mm - HH:mm** or **HH - HH**. Can't be used together with ``start_time`` and ``end_time``."


Dates
-----

The date can be defines using next rules.

1. Allowed year range: [1900, 2100]

2. Any delimiter from the list can be used:

    * ``-``

    * ``.``

    * ``/``

3. Allowed formats:

    * ``YYYY.mm.dd``

    * ``dd.mm.YYYY``

    * ``dd.mm.YY`` - will use 20th century

    * ``dd.mm`` - for the current year


As an example, let's look for example at the same data in all formats (assume, that current year is 2019):

* 2019-06-21
* 21.06.2019
* 21/06/19
* 21/06


Examples
========

1. Basic usage
--------------

Most basic and simplest usage. Doesn't have configuration.

Code:

.. code-block:: python

    from calendar_view.core import data
    from calendar_view.calendar import Calendar

    calendar = Calendar.build()
    calendar.add_event(data.event(day_of_week=0, interval='08:00 - 17:00'))
    calendar.add_event(data.event(day_of_week=5, interval='10:00 - 13:00'))
    calendar.add_event(data.event(day_of_week=6, interval='15:00 - 18:00'))
    calendar.save("simple_view.png")

Output:

.. image:: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/simple_view.png
    :target: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/simple_view.png
    :width: 600 px
    :align: center

2. Configuration and specific dates
-----------------------------------

View for one script. Configuration object and events with specific dates are used.

Code:

.. code-block:: python

    from calendar_view.core import data
    from calendar_view.calendar import Calendar

    config = data.CalendarConfig(
        lang='en',
        title='Sprint 23',
        dates='2019-09-23 - 2019-09-27',
        show_year=True,
        mode='working_hours',
        legend=False,
    )
    events = [
        data.event('Planning', date='2019-09-23', interval='11:00 - 13:00'),
        data.event('Demo', date='2019-09-27', interval='15:00 - 16:00'),
        data.event('Retrospective', date='2019-09-27', interval='17:00 - 18:00'),
    ]

    data.validate_config(config)
    data.validate_events(events, config)

    calendar = Calendar.build(config)
    calendar.add_events(events)
    calendar.save("sprint_23.png")


Output:

.. image:: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/sprint_23.png
    :target: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/sprint_23.png
    :width: 600 px
    :align: center


3. Legend view
--------------

If the name of event is too long, it can ee printed in the legend.

Code::

    from calendar_view.core import data
    from calendar_view.core.config import CalendarConfig
    from calendar_view.core.data import event
    from calendar_view.calendar import Calendar

    config = CalendarConfig(
        lang='en',
        title='Yoga Class Schedule',
        dates='Mo - Su',
        hours='8 - 22',
        show_date=False,
        legend=True,
    )
    events = [
        event(day_of_week=0, interval='11:00 - 12:30', name='Ashtanga, 90 mins, with Gina'),
        event(day_of_week=1, interval='18:00 - 19:15', name='HOT Core Yoga, 75 mins, with David'),
        event(day_of_week=2, interval='09:00 - 10:00', name='Meditation - Yoga Nidra, 60 mins, with Heena'),
        event(day_of_week=2, interval='19:00 - 20:15', name='Hatha Yoga, 75 mins, with Jo'),
        event(day_of_week=3, interval='19:00 - 20:00', name='Pilates, 60 mins, with Erika'),
        event(day_of_week=4, interval='18:30 - 20:00', name='Kundalini Yoga, 90 mins, with Dan'),
        event(day_of_week=5, interval='10:00 - 11:15', name='Hatha Yoga, 75 mins, with Amelia'),
        event(day_of_week=6, interval='10:00 - 11:15', name='Yoga Open, 75 mins, with Klaudia'),
        event(day_of_week=6, interval='14:00 - 15:15', name='Hatha Yoga, 75 mins, with Vick'),
    ]

    data.validate_config(config)
    data.validate_events(events, config)

    calendar = Calendar.build(config)
    calendar.add_events(events)
    calendar.save("yoga_class.png")


Output:

.. image:: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/yoga_class.png
    :target: https://raw.githubusercontent.com/sakhnevych/CalendarView/master/docs/yoga_class.png
    :width: 600 px
    :align: center


License
=======

CalendarView is licensed under a MIT license. Please see the `LICENSE <LICENSE.rst>`_ file for details.
