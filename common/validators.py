from datetime import date
from rest_framework.exceptions import ValidationError


def validate_birthdate_from_token(request):
  token_data = getattr(request, 'auth', None)

  birthdate_str = token_data.get('birthdate') if token_data else None

  if not birthdate_str or birthdate_str == 'None':
    raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

  try:
    birthdate = date.fromisoformat(str(birthdate_str))
  except ValueError:
    raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

  today = date.today()
  age = (
      today.year
      - birthdate.year
      - ((today.month, today.day) < (birthdate.month, birthdate.day))
  )

  if age < 18:
    raise ValidationError('Вам должно быть 18 лет, чтобы создать продукт.')