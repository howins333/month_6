from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager
from django.core.validators import RegexValidator

phone_validator = RegexValidator(regex=r'^996\d{9}$',
                                 message='Номер телефона должен быть в формате 996XXXXXXXXX')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(validators=[phone_validator],
                                    max_length=12,
                                    blank=True,
                                    null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Фамилия")
    registration_source = models.CharField(
        max_length=50,
        default='local',
        verbose_name="Источник регистрации"
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    birthdate = models.DateField(
        null=True, blank=True, verbose_name="Дата рождения"
    )

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['phone_number']
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email or ""


class ConfirmationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='confirmation_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Код подтверждения для {self.user.email}"