import asyncpg, json
from asyncpg import Connection
from asyncpg.cursor import Cursor
from typing import Optional, Any, List, Tuple
from functools import wraps
from script.config import settings
from script.logger import logger
from dict2xml import dict2xml

def handle_db_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncpg.PostgresError as e:
            logger.error(f"Database error: {e}")  
        except Exception as e:
            logger.error(f"Unknown error: {e}")  
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

    @handle_db_exceptions
    async def __aenter__(self):
        self.conn = await asyncpg.connect(
            database=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host
        )
        return self

    @handle_db_exceptions
    async def __aexit__(self, exc_type, exc, tb):
        if self.conn:
            await self.conn.close()

    @handle_db_exceptions
    async def fetchall(self, query: str, *args, **kwargs) -> List[Any]:
        if self.dict_cursor:
            return await self.conn.fetch(query, *args, **kwargs)
        else:
            return await self.conn.fetch(query, *args, **kwargs)

    @handle_db_exceptions
    async def fetchone(self, query: str, *args, **kwargs) -> Optional[Any]:
        if self.dict_cursor:
            return await self.conn.fetchrow(query, *args, **kwargs)
        else:
            return await self.conn.fetchrow(query, *args, **kwargs)

    @handle_db_exceptions
    async def execute(self, query: str, *args, **kwargs) -> None:
        await self.conn.execute(query, *args, **kwargs)

    @handle_db_exceptions
    async def executemany(self, query: str, args: List[Tuple], *_, **kwargs) -> None:
        await self.conn.executemany(query, args, **kwargs)

    @handle_db_exceptions
    async def execute_and_save(self, query: str, file_format: str, result_num: str, *args, **kwargs) -> None:
        if file_format != "xml" and file_format != "json":
            raise ValueError("Invalid format argument")
            
        result = []
        file_output = {}
        result = await self.conn.fetch(query, *args, **kwargs)

        with open(f"./data/result_{result_num}.{file_format}", mode='w+') as f:
            file_output["query"] = query
            file_output["result"] = [dict(item) for item in result]
            f.write(json.dumps(file_output) if file_format == "json" else dict2xml(file_output))
