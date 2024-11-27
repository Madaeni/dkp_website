from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


def validate_greater_than_zero(value):
    if value <= 0:
        raise ValidationError(
            'Стоимость события должно быть больше нуля!'
        )


def validate_close_date_greater_than_created_at(value, instance):
    if not instance.created_at and value <= now():
        raise ValidationError(
            _('Дата окончания должна быть позже даты создания.')
        )
