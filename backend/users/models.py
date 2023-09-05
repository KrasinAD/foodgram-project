# from foodgram.settings import USERNAME_CHARACTERS

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField('Электронная почта', unique=True)
    password = models.CharField('Пароль', max_length=150, blank=True)
    # bio = models.TextField('Биография', blank=True)
    # role = models.CharField('Тип пользователя', max_length=20,
    #                         choices=ROLES, default=USER)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['email']

    # def __str__(self):
    #     return self.username[:USERNAME_CHARACTERS]

    # class Meta:
    #     verbose_name = 'Пользователь'
    #     verbose_name_plural = 'Пользователи'