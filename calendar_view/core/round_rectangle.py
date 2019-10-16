from PIL.ImageDraw import ImageDraw


def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None, width=None):
    rad = corner_radius
    upper_left = xy[0]
    bottom_right = xy[1]
    self.rectangle(
        [
            (upper_left[0], upper_left[1] + rad),
            (bottom_right[0], bottom_right[1] - rad)
        ],
        fill=fill,
    )
    self.rectangle(
        [
            (upper_left[0] + rad, upper_left[1]),
            (bottom_right[0] - rad, bottom_right[1])
        ],
        fill=fill,
    )
    self.pieslice([upper_left, (upper_left[0] + rad * 2, upper_left[1] + rad * 2)],
        180, 270, fill=fill
    )
    self.pieslice([(bottom_right[0] - rad * 2, bottom_right[1] - rad * 2), bottom_right],
        0, 90, fill=fill
    )
    self.pieslice([(upper_left[0], bottom_right[1] - rad * 2), (upper_left[0] + rad * 2, bottom_right[1])],
        90, 180, fill=fill
    )
    self.pieslice([(bottom_right[0] - rad * 2, upper_left[1]), (bottom_right[0], upper_left[1] + rad * 2)],
        270, 360, fill=fill
    )

    border_delta = width/2 - 1
    if width > 0:
        self.line([(upper_left[0] + rad, upper_left[1] + border_delta), (bottom_right[0] - rad, upper_left[1] + border_delta)],
                  fill=outline, width=width)
        self.line([(bottom_right[0] - border_delta, upper_left[1] + rad), (bottom_right[0] - border_delta, bottom_right[1] - rad)],
                  fill=outline, width=width)
        self.line([(bottom_right[0] - rad, bottom_right[1] - border_delta), (upper_left[0] + rad, bottom_right[1] - border_delta)],
                  fill=outline, width=width)
        self.line([(upper_left[0] + border_delta, bottom_right[1] - rad), (upper_left[0] + border_delta, upper_left[1] + rad)],
                  fill=outline, width=width)

        self.arc([upper_left, (upper_left[0] + rad * 2, upper_left[1] + rad * 2)],
                 180, 270, fill=outline, width=width)
        self.arc([(bottom_right[0] - rad * 2, upper_left[1]), (bottom_right[0], upper_left[1] + rad * 2)],
                 270, 360, fill=outline, width=width)
        self.arc([(bottom_right[0] - rad * 2, bottom_right[1] - rad * 2), bottom_right],
                 0, 90, fill=outline, width=width)
        self.arc([(upper_left[0], bottom_right[1] - rad * 2), (upper_left[0] + rad * 2, bottom_right[1])],
                 90, 180, fill=outline, width=width)
