from script.db import AsyncDB
import asyncio, json
from script.logger import logger

async def main():
    async with AsyncDB() as db:
        data = await db.fetchall(
        """
        SELECT schema_name 
        FROM information_schema.schemata;
        """)
        logger.debug(data)

if __name__ == '__main__':
    asyncio.run(main())