from typing import Union


class StringUtils:
    @staticmethod
    def is_blank(value: str) -> bool:
        return not (value and value.strip())

    @staticmethod
    def is_not_blank(value: str) -> bool:
        return bool(value and value.strip())

    @staticmethod
    def strip_lines(input_lines: list[str], strip_lines: bool) -> list[str]:
        result: list[str] = []
        for line in input_lines:
            for row in line.split('\n'):
                if strip_lines:
                    row = row.strip()
                result.append(row)
        return result

    @staticmethod
    def count_max_text_width(text: Union[str, list[str]], left_strip_lines: bool = False) -> int:
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
