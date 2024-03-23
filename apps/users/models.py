import random
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from datetime import datetime, timedelta

STUDENT, ADMIN, SUPER_ADMIN = (
    'student',
    'admin',
    'super_admin'
)


VIA_EMAIL, VIA_PHONE = (
    "via_email",
    'via_phone',
)

PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class User(AbstractUser):
    _validation_phone = RegexValidator(
        regex=r"^+998\d{9}",
        message="Telefon raqam +998 bilan boshlanishi lozim"
    )
    USER_ROLES = (
        (STUDENT, STUDENT),
        (ADMIN, ADMIN),
        (SUPER_ADMIN, SUPER_ADMIN)
    )
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    user_roles = models.CharField(max_length=255, choices=USER_ROLES, default=STUDENT)
    auth_type = models.CharField(max_length=255, choices=AUTH_TYPE, default=VIA_EMAIL)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=12, null=True, unique=True, validators=[_validation_phone])
    bio = models.TextField()

    objects = UserManager

    def __str__(self):
        return f'{self.username}'

    def create_verify_code(self, verify_type):
        code = ''.join([str(random.randint(0, 100) for _ in range(4))])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code
        )
        return code


class UserConfirmation(models.Model):
    TYPE_CHOICE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    code = models.CharField(max_length=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_confirmation')
    verify_type = models.CharField(max_length=255, choices=TYPE_CHOICE, default=VIA_PHONE)
    expiration_time = models.DateTimeField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
            else:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)



