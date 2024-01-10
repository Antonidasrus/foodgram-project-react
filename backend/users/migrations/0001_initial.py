# Generated by Django 3.2 on 2024-01-10 08:24

import core.validators
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(help_text='Введите адрес электронной почты.', max_length=254, unique=True, verbose_name='Email')),
                ('username', models.CharField(help_text='Введите ник пользователя', max_length=100, unique=True, validators=[core.validators.validate_username, core.validators.LatinCharRegexValidator(), core.validators.TwoCharValidator(2)], verbose_name='Ник')),
                ('first_name', models.CharField(help_text='Введите свое имя', max_length=100, validators=[core.validators.TwoCharValidator(2), core.validators.CyrillicCharRegexValidator()], verbose_name='Имя')),
                ('last_name', models.CharField(help_text='Введите свою фамилию', max_length=100, validators=[core.validators.TwoCharValidator(2), core.validators.CyrillicCharRegexValidator()], verbose_name='Фамилия')),
                ('password', models.CharField(help_text='Введите свой пароль', max_length=100, verbose_name='Пароль')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_date', models.DateTimeField(auto_now=True, verbose_name='Дата подписки')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_in_subscription', to=settings.AUTH_USER_MODEL, verbose_name='Автор в подписке')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('subscription_date',),
            },
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_subscription'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user_id=django.db.models.expressions.F('author_id')), name='no_self_subscription'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('username', 'email'), name='unique_username_email'),
        ),
    ]
