from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class RedisStorage:
    host: str
    port: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool
    supports: list[int]


@dataclass
class Channel:
    channel_id: list[int]


@dataclass
class Products:
    product_list: list[int]


@dataclass
class Miscellaneous:
    other_params: str = None
    allowed_users: list = None
    secret_code: str = None
    mono_token: str = None
    mono_card_id: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    channel: Channel
    product: Products
    redis: RedisStorage


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            supports=env.list("SUPPORTS")
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('PG_PASSWORD'),
            user=env.str('PG_USER'),
            database=env.str('PG_NAME')
        ),
        redis=RedisStorage(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT')
        ),
        misc=Miscellaneous(
            allowed_users=[],
            secret_code=env.str('SECRET_CODE'),
            mono_token=env.str('MONO_TOKEN'),
            mono_card_id=env.str('MONO_CARD_ID')
        ),
        channel=Channel(
            channel_id=env.list("CHANNELS")
        ),
        product=Products(
            product_list=[]
        )
    )
