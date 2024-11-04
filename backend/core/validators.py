from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_greater_than_zero(value):
    if value <= 0:
        raise ValidationError(
            'Стоимость события должно быть больше нуля!'
        )


def validate_close_date_greater_than_created_at(value):
    if value <= now():
        raise ValidationError(
            'Время закрытия должно быть позже текущего!'
        )
