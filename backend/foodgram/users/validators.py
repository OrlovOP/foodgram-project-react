import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """Валидация имени пользователя."""
    invalid_symbols = ''.join(
        set(re.sub(r'[\w\.@+-]+', '', username))
    )
    if invalid_symbols:
        raise ValidationError('Некоректные символы в поле Username.')
    if username == 'me':
        raise ValidationError('Поле Username не может быть me.')
    return username
