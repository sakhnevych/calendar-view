day_of_week_i18n = {
    'en': [
        'Mo',
        'Tu',
        'We',
        'Th',
        'Fr',
        'Sa',
        'Su'
    ],
    'ru': [
        'Пн',
        'Вт',
        'Ср',
        'Чт',
        'Пт',
        'Сб',
        'Вс'
    ],
    'ua': [
        'Пн',
        'Вт',
        'Ср',
        'Чт',
        'Пт',
        'Сб',
        'Нд'
    ],
}


def days_of_week(lang: str = 'en'):
    """
    Returns the localization for the names of all days of the week
    """
    if lang not in day_of_week_i18n.keys():
        raise ValueError('Not defined for language ' + lang)
    return day_of_week_i18n[lang]


def day_of_week(day_of_week: int, lang: str = 'en'):
    """
    Returns the localization for the name of particular day of the week
    :param day_of_week: 0 - Monday, 1 - Tuesday, ..., 6 - Sunday
    """
    if lang not in day_of_week_i18n.keys():
        raise ValueError('Not defined for language ' + lang)
    if not (0 <= day_of_week <= 6):
        raise ValueError('Day of week has to be in range [0, 6]. Currect value: ' + str(day_of_week))
    return day_of_week_i18n[lang][day_of_week]
