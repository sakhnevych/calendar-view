from typing import List

from PIL import Image, ImageDraw
from datetime import date, timedelta, time

from calendar_view.config import i18n, style
from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.core.event import Event
from calendar_view.core import utils
from calendar_view.core.round_rectangle import rounded_rectangle

ImageDraw.rounded_rectangle = rounded_rectangle


class Calendar:
    @staticmethod
    def build(config: CalendarConfig = CalendarConfig()):
        cal = Calendar(config)
        cal.__draw_grid()
        return cal

    def __init__(self, config: CalendarConfig):
        self.config = config
        self.grid_image: Image = None
        self.grid_draw: ImageDraw = None
        self.event_image: Image = None
        self.event_draw: ImageDraw = None
        self.full_image: Image = None
        self.events: List[Event] = []

    def __draw_grid(self):
        (date_from, date_to) = self.config.get_date_range()
        day_count = (date_to - date_from).days + 1
        (hour_from, hour_to) = self.config.get_hours_range()
        hour_count = hour_to - hour_from
        day_height = hour_count * style.hour_height
        size = (day_count * style.day_width + 2 * style.padding_horizontal, style.hour_height + day_height + 2 * style.padding_vertical)
        self.grid_image = Image.new("RGBA", size, (0, 0, 0, 0))
        self.grid_draw = ImageDraw.Draw(self.grid_image)

        self.event_image = Image.new("RGBA", self.grid_image.size, (0, 0, 0, 0))
        self.event_draw = ImageDraw.Draw(self.event_image)

        # draw hours
        table_width = day_count * style.day_width
        x = (style.padding_horizontal, style.padding_horizontal + table_width)
        for i in range(1, hour_count + 2):
            y = style.padding_vertical + i * style.hour_height
            self.grid_draw.line([(x[0], y), (x[1], y)], fill=style.line_hour_color, width=style.line_hour_width)

        # draw days
        for i in range(0, day_count + 1):
            x = self.__get_event_x(i)
            y = style.padding_vertical + style.hour_height
            self.grid_draw.line([(x[0], y), (x[0], y + day_height)], fill=style.line_day_color, width=style.line_day_width)

        # write hour numbers
        for i in range(0, hour_count + 1):
            text = str(hour_from + i)
            text_size = style.hour_number_font.getsize(text)
            x = style.padding_horizontal - text_size[0] - 10
            y = style.padding_vertical + style.hour_height + i * style.hour_height - text_size[1] / 2

            self.grid_draw.text((x, y), text, font=style.hour_number_font, fill=style.hour_number_color)

        # write day of week
        for i in range(0, day_count):
            day = date_from + timedelta(days=i)
            text = self._get_day_title(day)
            text_size = style.day_of_week_font.getsize(text)
            x = style.padding_horizontal + i * style.day_width + style.day_width / 2 - text_size[0] / 2
            y = style.padding_vertical + text_size[1] / 2
            self.grid_draw.text((x, y), text, font=style.day_of_week_font, fill=style.day_of_week_color)

    def add_event_2(self, title: str, day_of_week: int, start_time: str, end_time: str):
        event = data.event(title, day_of_week=day_of_week, start_time=start_time, end_time=end_time)
        self.add_event(event)

    def add_event_3(self, title: str, day_of_week: int, interval: str):
        event = data.event(title, day_of_week=day_of_week, interval=interval)
        self.add_event(event)

    def add_events(self, events: list):
        for e in events:
            self.add_event(e)

    def add_event(self, event: Event):
        data.validate_event(event, self.config)
        self.events.append(event)

        # if legend is needed
        if self.config.legend is None and event.name is not None:
            y = self.__get_event_y(event.get_start_time(), event.get_end_time())
            height = y[1] - y[0]
            width = style.day_width
            text_size = style.event_name_font.getsize_multiline(event.name)
            if width < text_size[0] or height < text_size[1]:
                self.config.legend = True

    def _draw_event(self, event: Event):
        day_number = (event.get_date(self.config) - self.config.get_date_range()[0]).days
        x = self.__get_event_x(day_number)
        y = self.__get_event_y(event.get_start_time(), event.get_end_time())
        p1 = (x[0] + style.line_day_width/2, y[0])
        p2 = (x[1] - style.line_day_width/2, y[1])
        self.event_draw.rounded_rectangle([p1, p2], style.event_radius, outline=style.event_border, fill=style.event_fill, width=style.event_border_width)

        if not self.config.legend and event.name is not None:
            text_size = style.event_name_font.getsize_multiline(event.name)
            title_pos = ((x[0] + x[1]) / 2 - text_size[0]/2, (y[0] + y[1]) / 2 - text_size[1]/2)
            self.event_draw.multiline_text(title_pos, event.name, align='center',
                                           font=style.event_name_font, fill=style.event_name_color)

    def save(self, filename: str):
        self._build_image()
        self.full_image.save(filename, "PNG")

    def destroy(self):
        del self.grid_image
        del self.grid_draw
        del self.event_image
        del self.event_draw
        del self.full_image

    def _build_image(self):
        for e in self.events:
            self._draw_event(e)

        events: Image = Image.alpha_composite(self.grid_image, self.event_image)
        legend: Image = self._draw_legend()
        combined: Image = self._combine_image(events, self.config.title, legend)

        self.full_image = Image.new("RGBA", combined.size, style.image_bg)
        self.full_image = Image.alpha_composite(self.full_image, combined)

    def _draw_legend(self) -> Image:
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

    @staticmethod
    def _combine_image(events: Image, title: str, legend: Image):
        """
        Add title and combine all images into one.
        """
        if utils.is_blank(title) and legend is None:
            return events

        (event_width, event_height) = events.size
        (legend_width, legend_height) = (0, 0) if legend is None else legend.size
        title_size = style.title_font.getsize_multiline(title)
        title_width = title_size[0] + style.title_padding_left + style.title_padding_right
        title_height = title_size[1] + style.title_padding_top + style.title_padding_bottom
        final_width = max(event_width, title_width, legend_width)

        combined: Image = Image.new("RGBA", (final_width, event_height + title_height + legend_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(combined)
        # title
        title_padding_left = max(style.title_padding_left, (final_width - title_size[0]) / 2)
        draw.multiline_text((title_padding_left, style.title_padding_top), title, align='center',
                            font=style.title_font, fill=style.title_color)
        # events
        events_start = (int((final_width - event_width) / 2), title_height)
        combined.paste(events, events_start)
        if legend is not None:
            legend_start = (0, title_height + event_height)
            combined.paste(legend, legend_start)

        return combined

    def _get_event_legend_text(self, event: Event) -> str:
        date_text = self._get_day_title(event.get_date(self.config))
        time_text = '{:%H:%M} - {:%H:%M}'.format(event.get_start_time(), event.get_end_time())
        return '{}, {} - {}'.format(date_text, time_text, event.name)

    def _get_day_title(self, day: date) -> str:
        weekday = i18n.day_of_week(day.weekday(), self.config.lang)
        if not self.config.show_date:
            return weekday
        else:
            date = day.strftime('%d.%m') + (day.strftime('.%Y') if self.config.show_year else '')
            return '{}, {}'.format(weekday, date)

    def __get_event_x(self, day_number: int):
        x_start = style.padding_horizontal + day_number * style.day_width
        return x_start, x_start + style.day_width

    def __get_event_y(self, start: time, end: time):
        start_hour, end_hour = start.hour, end.hour
        config_start_hour = self.config.get_hours_range()[0]
        if config_start_hour > 0:
            start_hour -= config_start_hour
            end_hour -= config_start_hour

        y_start = style.padding_vertical + style.hour_height + start_hour * style.hour_height + (start.minute / 60) * style.hour_height
        y_end = style.padding_vertical + style.hour_height + end_hour * style.hour_height + (end.minute / 60) * style.hour_height
        return y_start, y_end
