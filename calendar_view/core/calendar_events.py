import logging
import textwrap
from collections import defaultdict
from datetime import date, time, datetime, timedelta
from typing import List, Tuple, Optional, NoReturn

from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont

from calendar_view.config import i18n, style
from calendar_view.core import data, time_utils
from calendar_view.core.config import CalendarConfig, VerticalAlign
from calendar_view.core.event import Event
from calendar_view.core.round_rectangle import draw_rounded_rectangle
from calendar_view.core.utils import StringUtils


class MultilineTextMetadata(object):
    """
    The required information to draw the text (title or notes) for the event.
    """
    def __init__(self, text: Optional[str] = None, size: tuple[int, int] = (0, 0)):
        self.text: Optional[str] = text
        self.size: tuple[int, int] = size
        self.visible: bool = text is not None and size[0] > 0 and size[1] > 0
        # self.trimmed: bool = False

    def __repr__(self) -> str:
        return f'MultilineTextMetadata[visible: {self.visible}, size: {self.size}, text: {self.text}]'


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
                self.__do_add_event(Event(title=event.title, style=event.style, start=fr, end=to))

    def __do_add_event(self, event: Event) -> None:
        data.validate_event(event, self.config)
        self.events.append(event)
        logging.debug(f'Added internal event: {event}')

        # if legend is needed
        if self.config.legend is None and event.title is not None:
            y = self.__get_event_y(event.start_time, event.end_time)
            height = y[1] - y[0]
            width = style.day_width
            text_size = style.event_title_font.getsize_multiline(event.title)
            if width < text_size[0] or height < text_size[1]:
                self.config.legend = True

    def group_cascade_events(self) -> NoReturn:
        group_counter: int = 1
        groups: dict[int, list[Event]] = defaultdict(list)
        for i in self.events:
            for j in self.events:
                if j == i:
                    pass
                else:
                    if i.start_time < j.start_time < i.end_time \
                            and i.get_start_date(self.config) == j.get_start_date(self.config):
                        if i.cascade_group == 0 and j.cascade_group == 0:
                            i.cascade_group = group_counter
                            j.cascade_group = group_counter
                            group_counter += 1
                        elif i.cascade_group == 0 and j.cascade_group != 0 or i.cascade_group != 0 \
                                and j.cascade_group == 0:
                            group_index: int = max(i.cascade_group, j.cascade_group)
                            i.cascade_group, j.cascade_group = group_index, group_index
                        elif i.cascade_group != j.cascade_group:
                            for k in self.events:
                                if k.cascade_group == i.cascade_group:
                                    k.cascade_group = j.cascade_group

        for i in self.events:
            if i.cascade_group > 0:
                group: list[Event] = groups[i.cascade_group]
                group.append(i)
        for i in groups.values():
            total_group_cascade: int = len(i)
            event_index: int = 1
            for j in i:
                j.cascade_index = event_index
                event_index += 1
                j.cascade_total = total_group_cascade

        for i in groups.values():
            for j in i:
                for k in i:
                    if j.cascade_index > k.cascade_index and j.start_time < k.start_time:
                        j.cascade_index, k.cascade_index = k.cascade_index, j.cascade_index

    def _draw_event(self, event: Event) -> NoReturn:
        """
        The events have already been split to the separate days. The event is for 1 day only.
        """
        day_number = (event.get_start_date(self.config) - self.config.get_date_range()[0]).days
        x = self.__get_event_x(day_number)
        y = self.__get_event_y(event.start_time, event.end_time)
        event_width: int = x[1] - x[0] - style.line_day_width
        cascade_event_width: int = event_width / event.cascade_total
        x1 = x[0] + style.line_day_width / 2 + (event.cascade_index - 1) * cascade_event_width
        x2 = x1 + cascade_event_width
        p1 = (x1, y[0])
        p2 = (x2, y[1])
        draw_rounded_rectangle(self.event_draw, [p1, p2], style.event_radius, outline=event.style.event_border,
                               fill=event.style.event_fill, width=style.event_border_width)

        if self.config.legend:
            return  # The title and notes are printed in the legend. Skip drawing here.

        cell_inner_size: tuple[int, int] = EventDrawHelper.count_cell_inner_size(x, y)
        if cell_inner_size[0] == 0 or cell_inner_size[1] == 0:
            return  # not possible to draw nothing inside the event cell

        # calculate text block sizes
        title_metadata: MultilineTextMetadata = EventDrawHelper.build_title_metadata(event.title, cell_inner_size)
        notes_inner_size: tuple[int, int] = (
            cell_inner_size[0],
            cell_inner_size[1] - (title_metadata.size[1] + style.event_title_margin if title_metadata.visible else 0)
        )
        notes_metadata: MultilineTextMetadata = EventDrawHelper.build_notes_metadata(event.notes, notes_inner_size)

        total_height: int = EventDrawHelper.count_final_text_height(title_metadata, notes_metadata)
        y_top_offset: int = y[0] + style.event_padding
        # print title
        if title_metadata.visible:
            # calculate the top position of the title multiline text block
            y_text_offset: int = EventDrawHelper.calculate_text_y_position_offset(self.config.title_vertical_align,
                                                                                  box_height=cell_inner_size[1],
                                                                                  text_height=title_metadata.size[1],
                                                                                  total_text_height=total_height)
            # the top-left position of the title block
            title_pos: tuple[int, int] = (
                (p1[0] + p2[0]) / 2 - title_metadata.size[0] / 2,
                y_top_offset + y_text_offset
            )
            self.event_draw.multiline_text(title_pos, title_metadata.text, align='center',
                                           font=style.event_title_font, fill=style.event_title_color)
            # update offset for notes
            y_top_offset = title_pos[1] + title_metadata.size[1] + style.event_title_margin

        # print notes
        if notes_metadata.visible:
            y_text_offset: int = 0  # draw the notes right after the title
            if not title_metadata.visible:
                # if the title is not visible, calculate the top-left position of the notes multiline text block
                y_text_offset = EventDrawHelper.calculate_text_y_position_offset(self.config.title_vertical_align,
                                                                                 box_height=cell_inner_size[1],
                                                                                 text_height=notes_metadata.size[1],
                                                                                 total_text_height=total_height)
            # the top-left position of the notes block
            notes_pos: tuple[int, int] = (
                p1[0] + style.event_padding,
                y_top_offset + y_text_offset
            )
            self.event_draw.multiline_text(notes_pos, notes_metadata.text, align='left',
                                           font=style.event_notes_font, fill=style.event_notes_color)

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
            _, text_height = style.event_title_font.getsize_multiline(e.title)
            text = self._get_event_legend_text(e)
            legend_draw.multiline_text((x, y), text, font=style.legend_name_font, fill=style.legend_name_color)
            y += text_height + style.legend_spacing

        del legend_draw
        return legend_image

    def _get_event_legend_text(self, event: Event) -> str:
        date_text = self._get_day_title(event.get_start_date(self.config))
        time_text = '{:%H:%M} - {:%H:%M}'.format(event.start_time, event.end_time)
        return '{}, {} - {}'.format(date_text, time_text, event.title)

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

        y_start = style.padding_vertical + style.hour_height + start_hour * style.hour_height + (
                    start.minute / 60) * style.hour_height
        y_end = style.padding_vertical + style.hour_height + end_hour * style.hour_height + (
                    end.minute / 60) * style.hour_height
        return y_start, y_end

    @staticmethod
    def __get_event_x(day_number: int):
        x_start = style.padding_horizontal + day_number * style.day_width
        return x_start, x_start + style.day_width


class EventDrawHelper:
    @staticmethod
    def count_cell_inner_size(x: tuple[float, float], y: tuple[float, float]) -> tuple[int, int]:
        return (
            max(0, int(x[1] - x[0] - 2 * style.line_day_width) - 2 * style.event_padding),
            max(0, int(y[1] - y[0] - 2 * style.line_day_width) - 2 * style.event_padding)
        )

    @staticmethod
    def count_final_text_height(title: MultilineTextMetadata, notes: MultilineTextMetadata) -> int:
        """
        Count the final height for the blocks title and notes in hte calendar event
        """
        height: int = 0
        if title.visible:
            height += title.size[1]
        if notes.visible:
            height += notes.size[1]
        return height

    @staticmethod
    def build_title_metadata(title: Optional[str], cell_inner_size: tuple[int, int]) -> MultilineTextMetadata:
        """
        Try to fit the title in the event inner cell. Split the text into the multiple lines if required.
        """
        return EventDrawHelper.__build_text_metadata(title, cell_inner_size, style.event_title_font, True)

    @staticmethod
    def build_notes_metadata(notes: Optional[str], notes_inner_size: tuple[int, int]) -> MultilineTextMetadata:
        """
        Try to fit notes in the event inner cell. Split the text into the multiple lines if required.
        """
        return EventDrawHelper.__build_text_metadata(notes, notes_inner_size, style.event_notes_font, False)

    @staticmethod
    def calculate_text_y_position_offset(vertical_align: VerticalAlign, box_height: int, text_height: int,
                                         total_text_height: int) -> int:
        """
        Calculates the offset of the text block.
        :param vertical_align: the alignment of the text block
        :param box_height: the height of the inner event cell
        :param text_height: the height of the title or notes multiline text block
        :param total_text_height: the height of the title+notes text blocks
        """
        if vertical_align == 'top':
            return 0
        if vertical_align == 'center':
            return int(box_height / 2 - text_height / 2)
        if vertical_align == 'bottom':
            return max(0, box_height - total_text_height)
        raise RuntimeError(f'Wrong vertical align value: {vertical_align}')

    @staticmethod
    def __build_text_metadata(text: Optional[str], box_size: tuple[int, int], font: FreeTypeFont, strip_lines: bool) \
            -> MultilineTextMetadata:
        """
        Try to fit text in the given box. Split the text into the multiple lines if required.
        """
        if not text or len(text.strip()) == 0:
            return MultilineTextMetadata()
        if box_size[0] <= 0 or box_size[1] <= 0:
            return MultilineTextMetadata()

        text = text.strip()
        text_size: tuple[int, int] = font.getsize_multiline(text)
        if EventDrawHelper.__fits_the_borders(text_size, box_size):
            return MultilineTextMetadata(text, text_size)
        elif EventDrawHelper.__fits_the_width(text_size, box_size):
            return MultilineTextMetadata(text, text_size)

        max_width: int = StringUtils.count_max_text_width(text, strip_lines)
        base_new_text_width: int = int(box_size[0] * max_width / text_size[0])

        new_text: str = ''
        new_text_size: tuple[int, int] = (0, 0)
        for retry_count in range(0, 12, 2):
            new_test_width: int = base_new_text_width - retry_count
            if new_test_width <= 0:
                return MultilineTextMetadata(text, text_size)  # no place to fit the text

            lines: list[str] = textwrap.wrap(text, width=new_test_width, replace_whitespace=False)
            lines = StringUtils.strip_lines(lines, strip_lines)
            new_text = '\n'.join(lines)
            new_text_size = font.getsize_multiline(new_text)
            if EventDrawHelper.__fits_the_borders(new_text_size, box_size):
                return MultilineTextMetadata(new_text, new_text_size)
            elif EventDrawHelper.__fits_the_width(new_text_size, box_size):
                return MultilineTextMetadata(new_text, new_text_size)
        raise RuntimeError('Not possible to wrap the text to fit the width.')
        # textwrap.shorten(title, width=20, placeholder=' ...')

    @staticmethod
    def __fits_the_borders(size: tuple[int, int], border: tuple[int, int]) -> bool:
        return size[0] <= border[0] and size[1] <= border[1]

    @staticmethod
    def __fits_the_width(size: tuple[int, int], border: tuple[int, int]) -> bool:
        return size[0] <= border[0]
