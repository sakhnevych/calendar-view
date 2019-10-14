def is_blank(value: str):
    return not (value and value.strip())


def is_not_blank(value: str):
    return bool(value and value.strip())
