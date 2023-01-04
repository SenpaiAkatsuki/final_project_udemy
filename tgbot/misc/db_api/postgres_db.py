import logging
from typing import Union

from asyncpg import Pool, Connection, DuplicateTableError, create_pool


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create_connection(self, user, password, host, database):
        self.pool = await create_pool(
            user=user,
            password=password,
            host=host,
            database=database
        )
        # logging.info("DB Open")

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        try:
            sql = """
            CREATE TABLE Users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            telegram_id BIGINT NOT NULL UNIQUE,
            referral_id BIGINT,
            balance BIGINT DEFAULT 0,
            purchase_list VARCHAR DEFAULT '---'
            );
            """
            await self.execute(sql, execute=True)
            logging.info("TABLE Users CREATED")
        except DuplicateTableError:
            logging.info("Table already exists")
            pass

    async def create_table(self):
        try:
            sql = """
            CREATE TABLE Products (
            product_id VARCHAR(255) UNIQUE PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            price BIGINT NOT NULL,
            photo VARCHAR(255) NOT NULL,
            quantity INT NOT NULL
            );
            """
            await self.execute(sql, execute=True)
            logging.info("TABLE Products CREATED")
        except DuplicateTableError:
            logging.info("Table already exists")
            pass

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    # ========================================= SQL commands for products    =========================================

    async def change_quantity(self, quantity, product_id):
        sql = "UPDATE products SET quantity = $1 WHERE product_id = $2"
        return await self.execute(sql, quantity, product_id, execute=True)

    async def create_product(self, product_id, name, description, price, photo, quantity):
        sql = "INSERT INTO products (product_id, name, description, price, photo, quantity) VALUES ($1, $2, $3, $4, $5, $6)"
        return await self.execute(sql, product_id, name, description, price, photo, quantity, fetchrow=True)

    async def get_products_sorted(self, value):
        sql = "SELECT * FROM Products WHERE name LIKE $1 "
        return await self.execute(sql, value, fetch=True)

    async def get_products(self):
        sql = "SELECT * FROM Products ORDER BY name ASC"
        return await self.execute(sql, fetch=True)

    async def select_product(self, **kwargs):
        sql = "SELECT * FROM Products WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def get_product_id(self):
        sql = "SELECT product_id FROM Products"
        return await self.execute(sql, fetch=True)

    async def update_product_name(self, name, product_id):
        sql = "UPDATE products SET name = $1 WHERE product_id = $2"
        return await self.execute(sql, name, product_id, execute=True)

    async def update_product_description(self, description, product_id):
        sql = "UPDATE products SET description = $1 WHERE product_id = $2"
        return await self.execute(sql, description, product_id, execute=True)

    async def update_product_price(self, price, product_id):
        sql = "UPDATE products SET price = $1 WHERE product_id = $2"
        return await self.execute(sql, price, product_id, execute=True)

    async def update_product_photo(self, photo, product_id):
        sql = "UPDATE products SET photo = $1 WHERE product_id = $2"
        return await self.execute(sql, photo, product_id, execute=True)

    # ========================================= SQL commands for users =========================================
    async def add_user(self, username, telegram_id, referral_id=None):
        if referral_id:
            sql = "INSERT INTO users (username, telegram_id, referral_id) VALUES($1, $2, $3) returning *"
            return await self.execute(sql, username, telegram_id, int(referral_id), fetchrow=True)
        else:
            sql = "INSERT INTO users (username, telegram_id) VALUES($1, $2) returning *"
            return await self.execute(sql, username, telegram_id, fetchrow=True)

    async def insert_purchase_list(self, purchase_id, telegram_id):
        sql = "UPDATE users SET purchase_list = purchase_list || ' | ' || $1 WHERE telegram_id = $2"
        return await self.execute(sql, purchase_id, telegram_id, execute=True)

    async def change_user_balance(self, balance, telegram_id):
        sql = "UPDATE users SET balance = $1 WHERE telegram_id = $2"
        return await self.execute(sql, balance, telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def get_telegram_id(self):
        sql = "SELECT telegram_id FROM users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def check_referrals(self, referral_id):
        sql = "SELECT telegram_id FROM users WHERE referral_id=$1"
        return await self.execute(sql, referral_id, fetch=True)

    async def get_referrals(self):
        sql = "SELECT referral_id FROM users"
        return await self.execute(sql, fetch=True)

    async def referral_test(self):
        sql = "SELECT username FROM users WHERE referral_id=394893206"
        return await self.execute(sql, fetch=True)

    async def update_referral(self, referral):
        sql = "UPDATE users SET referral_id WHERE telegram_id=$1"
        return await self.execute(sql, referral, execute=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def close(self) -> None:
        if self.pool is None:
            return None
        # logging.info("DB closed")

        await self.pool.close()
