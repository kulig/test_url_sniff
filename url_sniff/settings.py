"""Модуль настроек."""

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    """Настроки приложения. """

    debug: bool = False
    max_workers: int = 5


class DBSettings(BaseSettings):
    """Настройки БД."""

    host: str = 'localhost'
    port: int = 5432
    database: str = 'postgres'
    username: str = 'postgres'
    password: str = ''

    class Config:
        """Определяет префикс для настроек БД и варианты названия настроек."""

        env_prefix = 'db_'
        fields = {
            'database': {
                'env': [f'{env_prefix}name', f'{env_prefix}database'],
            },
            'username': {
                'env': [f'{env_prefix}user', f'{env_prefix}username'],
            },
        }


app_settings = AppSettings()
db_settings = DBSettings()
