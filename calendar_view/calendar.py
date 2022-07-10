from collections import defaultdict
from typing import List, NoReturn

from PIL import Image, ImageDraw

from calendar_view.config import style
from calendar_view.core.calendar_events import CalendarEvents
from calendar_view.core.calendar_grid import CalendarGrid
from calendar_view.core.config import CalendarConfig
from calendar_view.core.event import Event
from calendar_view.core.utils import StringUtils


class Calendar:
    @staticmethod
    def build(config: CalendarConfig = CalendarConfig()):
        cal = Calendar(config)
        cal.draw_grid()
        return cal

    def __init__(self, config: CalendarConfig):
        self.config = config
        self.grid = CalendarGrid(config)
        self.events = CalendarEvents(config)
        self.full_image: Image = None

    def draw_grid(self):
        self.grid.draw_grid()
        self.events.draw_grid(self.grid.get_size())

    def add_events(self, events: List[Event]) -> None:
        """
        Adds the input events to the list to draw them later.
        :param events: the list of events
        """
        for e in events:
            self.events.add_event(e)

    def add_event(self, *events: Event, **kwargs) -> None:
        """
        Adds the event(s) to the list to draw them later.
        :param events: the event objects
        :param kwargs: the input arguments for the Event constructor
        """
        if events:
            for event in events:
                self.events.add_event(event)
        if kwargs:
            self.events.add_event(Event(**kwargs))

    def cascade(self):
        group_counter: int = 1
        groups: dict[int, list[Event]] = defaultdict(list)
        for i in self.events.events:
            for j in self.events.events:
                if j == i:
                    pass
                else:
                    if i.start_time < j.start_time < i.end_time and i.get_day() == j.get_day():
                        if i.cascade_group == 0 and j.cascade_group == 0:
                            i.cascade_group = group_counter
                            j.cascade_group = group_counter
                            group_counter += 1
                        elif i.cascade_group == 0 and j.cascade_group != 0 or i.cascade_group != 0 and j.cascade_group == 0:
                            group_index: int = max(i.cascade_group, j.cascade_group)
                            i.cascade_group, j.cascade_group = group_index, group_index
                        elif i.cascade_group != j.cascade_group:
                            for k in self.events.events:
                                if k.cascade_group == i.cascade_group:
                                    k.cascade_group = j.cascade_group


        for i in self.events.events:
            if i.cascade_group == 0:
                group_counter += 1
                i.cascade_group = group_counter
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
            if len(i) > 1:
                for j in i:
                    for k in i:
                        if j.cascade_index > k.cascade_index and j.start_time < k.start_time:
                            j.cascade_index, k.cascade_index = k.cascade_index, j.cascade_index

    def save(self, filename: str) -> NoReturn:
        self.cascade()
        self._build_image()
        self.full_image.save(filename, "PNG")

    def _build_image(self):
        grid_image: Image = self.grid.get_image()
        event_image: Image = self.events.draw_events()
        legend: Image = self.events.draw_legend()

        events: Image = Image.alpha_composite(grid_image, event_image)
        combined: Image = self._combine_image(events, self.config.title, legend)

        self.full_image = Image.new("RGBA", combined.size, style.image_bg)
        self.full_image = Image.alpha_composite(self.full_image, combined)

    def destroy(self):
        self.grid.destroy()
        self.events.destroy()
        del self.full_image

    @staticmethod
    def _combine_image(events: Image, title: str, legend: Image):
        """
        Add title and combine all images into one.
        """
        if StringUtils.is_blank(title) and legend is None:
            return events

        event_width, event_height = events.size
        legend_width, legend_height = (0, 0) if legend is None else legend.size
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
