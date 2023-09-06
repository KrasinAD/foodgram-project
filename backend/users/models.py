# from foodgram.settings import USERNAME_CHARACTERS

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(unique=True)
    # username = models.TextField('Юзернейм')
    # first_name = models.TextField('Имя')
    # last_name = models.TextField('Фамилия')
    # password = models.TextField('Пароль')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # def __str__(self):
    #     return self.username[:USERNAME_CHARACTERS]

    # class Meta:
    #     verbose_name = 'Пользователь'
    #     verbose_name_plural = 'Пользователи'