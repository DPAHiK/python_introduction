import asyncpg
from asyncpg import Connection
from asyncpg.cursor import Cursor
from typing import Optional, Any, List, Tuple
from functools import wraps
from script.config import settings
from script.logger import logger

def log_db_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncpg.PostgresError as e:
            logger.error(f"Database error: {e}")  
            raise
        except Exception as e:
            logger.error(f"Unknown error: {e}")  
            raise
    return wrapper

class AsyncDB:
    def __init__(self, dict_cursor: bool = False):
        self.dbname = settings.db_name
        self.user = settings.db_user
        self.password = settings.db_pass
        self.host = settings.db_host
        self.dict_cursor = dict_cursor
        self.conn: Optional[Connection] = None
        self.cur: Optional[Cursor] = None

    @log_db_exceptions
    async def __aenter__(self):
        self.conn = await asyncpg.connect(
            database=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host
        )
        return self

    @log_db_exceptions
    async def __aexit__(self, exc_type, exc, tb):
        if self.conn:
            await self.conn.close()

    @log_db_exceptions
    async def fetchall(self, query: str, *args, **kwargs) -> List[Any]:
        if self.dict_cursor:
            return await self.conn.fetch(query, *args, **kwargs)
        else:
            return await self.conn.fetch(query, *args, **kwargs)

    @log_db_exceptions
    async def fetchone(self, query: str, *args, **kwargs) -> Optional[Any]:
        if self.dict_cursor:
            return await self.conn.fetchrow(query, *args, **kwargs)
        else:
            return await self.conn.fetchrow(query, *args, **kwargs)

    @log_db_exceptions
    async def execute(self, query: str, *args, **kwargs) -> None:
        await self.conn.execute(query, *args, **kwargs)

    @log_db_exceptions
    async def executemany(self, query: str, args: List[Tuple], *_, **kwargs) -> None:
        await self.conn.executemany(query, args, **kwargs)
