import logging
from datetime import date, time, datetime, timedelta
from typing import List, Tuple

from PIL import Image, ImageDraw

from calendar_view.config import i18n, style
from calendar_view.core import data, time_utils
from calendar_view.core.config import CalendarConfig
from calendar_view.core.event import Event
from calendar_view.core.round_rectangle import draw_rounded_rectangle


class CalendarEvents(object):
    def __init__(self, config: CalendarConfig):
        self.config = config
        self.event_image: Image = None
        self.event_draw: ImageDraw = None
        self.full_image: Image = None
        self.events: List[Event] = []

    def draw_grid(self, size: Tuple[float, float]):
        self.event_image = Image.new("RGBA", size, (0, 0, 0, 0))
        self.event_draw = ImageDraw.Draw(self.event_image)

    def add_event(self, event: Event) -> None:
        """
        Skip the empty events with a duration of fewer than 0 seconds.
        Splits events, if needed, to the separate days. The event in the result list has to be for 1 day only.
        Cut the event's time out of the visible time range.
        Validate events.
        """
        if event.get_duration_seconds(self.config) < 1:
            logging.warning(f"Skipping event, the duration is too small: {event}")
            return
        end_date: date = event.get_end_date(self.config)
        start_date: date = event.get_start_date(self.config)
        if end_date < self.config.get_date_range()[0]:
            logging.warning(f"Skipping event, it ends before the visible range: {event}")
            return
        if start_date > self.config.get_date_range()[1]:
            logging.warning(f"Skipping event, it starts after the visible range: {event}")
            return

        if start_date == end_date or ((end_date - start_date).days == 1 and event.end_time == time(0, 0)):
            self.__do_add_event(event)
        else:
            logging.debug(f'Splitting the event: {event}')
            iter_from: date = max(start_date, self.config.get_date_range()[0])
            iter_to: date = min(end_date, self.config.get_date_range()[1])
            for single_date in time_utils.date_range(iter_from, iter_to):
                next_date: date = single_date + timedelta(days=1)
                if single_date == start_date:
                    fr: datetime = datetime.combine(single_date, event.start_time)
                    to: datetime = datetime.combine(next_date, time(0, 0))
                elif single_date == end_date:
                    fr: datetime = datetime.combine(single_date, time(0, 0))
                    to: datetime = datetime.combine(single_date, event.end_time)
                else:
                    fr: datetime = datetime.combine(single_date, time(0, 0))
                    to: datetime = datetime.combine(next_date, time(0, 0))
                self.__do_add_event(Event(name=event.name, style=event.style, start=fr, end=to))

    def __do_add_event(self, event: Event) -> None:
        data.validate_event(event, self.config)
        self.events.append(event)
        logging.debug(f'Added internal event: {event}')

        # if legend is needed
        if self.config.legend is None and event.name is not None:
            y = self.__get_event_y(event.start_time, event.end_time)
            height = y[1] - y[0]
            width = style.day_width
            text_size = style.event_name_font.getsize_multiline(event.name)
            if width < text_size[0] or height < text_size[1]:
                self.config.legend = True

    def _draw_event(self, event: Event):
        """
        The events have already been split to the separate days. The event is for 1 day only.
        """
        day_number = (event.get_start_date(self.config) - self.config.get_date_range()[0]).days
        x = self.__get_event_x(day_number)
        y = self.__get_event_y(event.start_time, event.end_time)
        p1 = (x[0] + style.line_day_width/2, y[0])
        p2 = (x[1] - style.line_day_width/2, y[1])
        draw_rounded_rectangle(self.event_draw, [p1, p2], style.event_radius, outline=event.style.event_border, fill=event.style.event_fill,
                               width=style.event_border_width)

        if not self.config.legend and event.name is not None:
            text_size = style.event_name_font.getsize_multiline(event.name)
            title_pos = ((x[0] + x[1]) / 2 - text_size[0]/2, (y[0] + y[1]) / 2 - text_size[1]/2)
            self.event_draw.multiline_text(title_pos, event.name, align='center',
                                           font=style.event_name_font, fill=style.event_name_color)

    def destroy(self):
        del self.event_image
        del self.event_draw
        del self.full_image

    def draw_events(self) -> Image:
        for e in self.events:
            self._draw_event(e)
        return self.event_image

    def draw_legend(self) -> Image:
        if not self.config.legend or len(self.events) == 0:
            return None
        width = 0
        height = 0
        for e in self.events:
            text = self._get_event_legend_text(e)
            text_width, text_height = style.legend_name_font.getsize_multiline(text)
            width = max(width, text_width)
            height += text_height

        width += style.legend_padding_left + style.legend_padding_right
        height += (len(self.events) - 1) * style.legend_spacing + style.legend_padding_top + style.legend_padding_bottom

        legend_image: Image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        legend_draw = ImageDraw.Draw(legend_image)

        x = style.legend_padding_left
        y = style.legend_padding_top
        for e in self.events:
            _, text_height = style.event_name_font.getsize_multiline(e.name)
            text = self._get_event_legend_text(e)
            legend_draw.multiline_text((x, y), text, font=style.legend_name_font, fill=style.legend_name_color)
            y += text_height + style.legend_spacing

        del legend_draw
        return legend_image

    def _get_event_legend_text(self, event: Event) -> str:
        date_text = self._get_day_title(event.get_start_date(self.config))
        time_text = '{:%H:%M} - {:%H:%M}'.format(event.start_time, event.end_time)
        return '{}, {} - {}'.format(date_text, time_text, event.name)

    def _get_day_title(self, day: date) -> str:
        weekday = i18n.day_of_week(day.weekday(), self.config.lang)
        if not self.config.show_date:
            return weekday
        else:
            date = day.strftime('%d.%m') + (day.strftime('.%Y') if self.config.show_year else '')
            return '{}, {}'.format(weekday, date)

    def __get_event_y(self, start: time, end: time):
        start_hour: int = start.hour
        end_hour: int = 24 if (end.hour == 0 and end.minute == 0) else end.hour
        config_start_hour = self.config.get_hours_range()[0]
        if config_start_hour > 0:
            start_hour -= config_start_hour
            end_hour -= config_start_hour

        y_start = style.padding_vertical + style.hour_height + start_hour * style.hour_height + (start.minute / 60) * style.hour_height
        y_end = style.padding_vertical + style.hour_height + end_hour * style.hour_height + (end.minute / 60) * style.hour_height
        return y_start, y_end

    @staticmethod
    def __get_event_x(day_number: int):
        x_start = style.padding_horizontal + day_number * style.day_width
        return x_start, x_start + style.day_width
