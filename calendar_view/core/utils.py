from typing import Union, List, Tuple

from PIL import ImageFont, ImageDraw, Image


class StringUtils:
    @staticmethod
    def is_blank(value: str) -> bool:
        return not (value and value.strip())

    @staticmethod
    def is_not_blank(value: str) -> bool:
        return bool(value and value.strip())

    @staticmethod
    def strip_lines(input_lines: List[str], strip_lines: bool) -> List[str]:
        result: list[str] = []
        for line in input_lines:
            for row in line.split('\n'):
                if strip_lines:
                    row = row.strip()
                result.append(row)
        return result

    @staticmethod
    def count_max_text_width(text: Union[str, List[str]], left_strip_lines: bool = False) -> int:
        if isinstance(text, str):
            return max([len(StringUtils.strip(line, left_strip_lines, True)) for line in text.split('\n')])
        if isinstance(text, list):
            return max([StringUtils.count_max_text_width(line, left_strip_lines) for line in text])
        raise ValueError(f'Wrong input type. Required: Union[str, list[str]]. Actual: {type(text)}')

    @staticmethod
    def strip(text: str, left_strip: bool, right_strip: bool) -> str:
        if left_strip:
            text = text.lstrip()
        if right_strip:
            text = text.rstrip()
        return text


class FontUtils:
    @staticmethod
    def get_text_size(font: ImageFont, text: str) -> Tuple[int, int]:
        if hasattr(font, 'getsize'):
            return font.getsize(text)

        # More information: https://pillow.readthedocs.io/en/stable/deprecations.html
        left, top, right, bottom = font.getbbox(text)
        return right - left, bottom - top

    @staticmethod
    def get_multiline_text_size(font: ImageFont, text: str) -> Tuple[int, int]:
        if hasattr(font, 'getsize_multiline'):
            return font.getsize_multiline(text)

        dummy_draw: ImageDraw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        # More information: https://pillow.readthedocs.io/en/stable/deprecations.html
        left, top, right, bottom = dummy_draw.multiline_textbbox((0, 0), text, font=font)
        return right - left, bottom - top
