from script.db import AsyncDB
from script import logger, DB_QUERIES, DATE_PATTERN, parser
import asyncio, json, datetime, re

async def main(students_path=None, rooms_path=None, format=None):
    if students_path is None or rooms_path is None or format is None:
        logger.error("None-type arguments for main script function")
        return
    if format != "xml" and format != "json":
        logger.error("Invalid format argument (only json and xml are allowed)")
        return
    
    logger.info("Starting loading data to DB...")
    rooms_data = []
    students_data = []

    with open(students_path) as f:
        students_data = json.load(f)
        students_data = [{**student,
                           'birthday': datetime.datetime.strptime(student.get('birthday', ''), '%Y-%m-%dT%H:%M:%S.%f')
                            if re.fullmatch(DATE_PATTERN, student.get('birthday', ''))
                            else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)}
                            for student in students_data]

    with open(rooms_path) as f:
        rooms_data = json.load(f)

    async with AsyncDB() as db:
        room_values = [(room.get('id', None), room.get('name', None)) for room in rooms_data]
        await db.executemany(
            """
            INSERT INTO rooms(id, name)
            VALUES($1, $2)
            """,
            room_values
        )
        
        student_values = [
        (student.get('id', None), student.get('name', None), student.get('sex', None),
        student.get('birthday', None), student.get('room', None))
        for student in students_data
        ]
        await db.executemany(
            """
            INSERT INTO students(id, name, sex, birthday, room)
            VALUES($1, $2, $3, $4, $5)
            """,
            student_values
        )
    
    logger.info("Done loading data to DB")

    logger.info("Executing queries...")

    async with AsyncDB() as db:
        for query, num in zip(DB_QUERIES, range(len(DB_QUERIES))):
            await db.execute_and_save(query, format, num)

    logger.info("Done executing queries")

if __name__ == '__main__':
    args = parser.parse_args()
    asyncio.run(main(students_path=args.students, rooms_path=args.rooms, format=args.format))