from typing import List, Tuple

from PIL import Image, ImageDraw

from calendar_view.config import style
from calendar_view.core.calendar_events import CalendarEvents
from calendar_view.core.calendar_grid import CalendarGrid
from calendar_view.core.config import CalendarConfig
from calendar_view.core.event import Event
from calendar_view.core.utils import StringUtils, FontUtils


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

    def save(self, filename: str) -> None:
        self.events.group_cascade_events()
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
        title_size: Tuple[int, int] = FontUtils.get_multiline_text_size(style.title_font, title)
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
