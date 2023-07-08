# Generated by Django 3.2.3 on 2023-07-05 11:06

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=150, validators=[users.validators.validate_username], verbose_name='Юзернейм пользователя'),
        ),
    ]
