from datetime import date, timedelta
from typing import Tuple

from PIL import Image, ImageDraw

from calendar_view.config import i18n, style
from calendar_view.core.config import CalendarConfig
from calendar_view.core.utils import FontUtils


class CalendarGrid(object):
    def __init__(self, config: CalendarConfig):
        self.config = config
        self._grid_image: Image = None
        self._grid_draw: ImageDraw = None

    def get_image(self) -> Image:
        return self._grid_image

    def get_size(self) -> Tuple[float, float]:
        return self._grid_image.size

    def draw_grid(self):
        date_from, date_to = self.config.get_date_range()
        day_count = (date_to - date_from).days + 1
        hour_from, hour_to = self.config.get_hours_range()
        hour_count = hour_to - hour_from
        day_height = hour_count * style.hour_height
        size = (day_count * style.day_width + 2 * style.padding_horizontal, style.hour_height + day_height + 2 * style.padding_vertical)
        self._grid_image = Image.new("RGBA", size, (0, 0, 0, 0))
        self._grid_draw = ImageDraw.Draw(self._grid_image)

        # draw hours
        table_width = day_count * style.day_width
        x = (style.padding_horizontal, style.padding_horizontal + table_width)
        for i in range(1, hour_count + 2):
            y = style.padding_vertical + i * style.hour_height
            self._grid_draw.line([(x[0], y), (x[1], y)], fill=style.line_hour_color, width=style.line_hour_width)

        # draw days
        for i in range(day_count + 1):
            x = self.__get_event_x(i)
            y = style.padding_vertical + style.hour_height
            self._grid_draw.line([(x[0], y), (x[0], y + day_height)], fill=style.line_day_color, width=style.line_day_width)

        # write hour numbers
        for i in range(hour_count + 1):
            text = str(hour_from + i)
            text_size: Tuple[int, int] = FontUtils.get_text_size(style.hour_number_font, text)
            x = style.padding_horizontal - text_size[0] - 10
            y = style.padding_vertical + style.hour_height + i * style.hour_height - text_size[1] / 2

            self._grid_draw.text((x, y), text, font=style.hour_number_font, fill=style.hour_number_color)

        # write day of week
        for i in range(day_count):
            day = date_from + timedelta(days=i)
            text = self._get_day_title(day)
            text_size: Tuple[int, int] = FontUtils.get_text_size(style.day_of_week_font, text)
            x = style.padding_horizontal + i * style.day_width + style.day_width / 2 - text_size[0] / 2
            y = style.padding_vertical + text_size[1] / 2
            self._grid_draw.text((x, y), text, font=style.day_of_week_font, fill=style.day_of_week_color)

    def destroy(self):
        del self._grid_image
        del self._grid_draw

    def _get_day_title(self, day: date) -> str:
        weekday = i18n.day_of_week(day.weekday(), self.config.lang)
        if not self.config.show_date:
            return weekday
        else:
            date_value = day.strftime('%d.%m') + (day.strftime('.%Y') if self.config.show_year else '')
            return '{}, {}'.format(weekday, date_value)

    @staticmethod
    def __get_event_x(day_number: int):
        x_start = style.padding_horizontal + day_number * style.day_width
        return x_start, x_start + style.day_width
