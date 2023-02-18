from pydantic import BaseSettings


class AppSettings(BaseSettings):
    debug: bool = False


class DBSettings(BaseSettings):
    drivername: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    port: int = 5432
    database: str = 'postgres'
    username: str = 'postgres'
    password: str = ''

    class Config:
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