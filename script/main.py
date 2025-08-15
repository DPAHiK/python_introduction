from script.db import AsyncDB
from script.logger import logger
import asyncio, json, argparse, datetime

parser = argparse.ArgumentParser()
parser.add_argument('--students', default='./data/students.json')
parser.add_argument('--rooms', default='./data/rooms.json')
parser.add_argument('--format', default='json')

DB_QUERIES = [
            """
            select r.name, count(s.room) as students_count 
            from rooms r inner join students s on r.id = s.room 
            group by r.name;
            """,

            """
            select r.name 
            from rooms r inner join students s on r.id = s.room 
            group by r.name 
            order by avg(AGE(CURRENT_DATE, s.birthday)) asc 
            limit 5;
            """,

            """
            select r.name 
            from rooms r inner join students s on r.id = s.room 
            group by r.name 
            order by max(AGE(CURRENT_DATE, s.birthday)) - min(AGE(CURRENT_DATE, s.birthday)) desc 
            limit 5;
            """,

            """
            select r.name 
            from rooms r inner join students s on r.id = s.room 
            group by r.name 
            having count(distinct s.sex) > 1;
            """
]

async def parse_students_birthday(students):
    for student in students:
        try:
            student['birthday'] = datetime.datetime.strptime(student.get('birthday', ''), '%Y-%m-%dT%H:%M:%S.%f')
        except (ValueError, TypeError): 
            student['birthday'] = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

async def main(students_path=None, rooms_path=None, format=None):
    if students_path is None or rooms_path is None or format is None:
        logger.error("None-type arguments for main script function")
        return
    
    logger.info("Starting loading data to DB...")
    rooms_data = []
    students_data = []

    with open(students_path) as f:
        students_data = json.load(f)
        await parse_students_birthday(students_data)

    with open(rooms_path) as f:
        rooms_data = json.load(f)

    async with AsyncDB() as db:
        for room in rooms_data:
            await db.execute(
                """
                INSERT INTO rooms(id, name)
                VALUES($1, $2)
                """,
                room.get('id', None),
                room.get('name', None)
            )
        
        for student in students_data:
            await db.execute(
                """
                INSERT INTO students(id, name, sex, birthday, room)
                VALUES($1, $2, $3, $4, $5)
                """,
                student.get('id', None),
                student.get('name', None),
                student.get('sex', None),
                student.get('birthday', None),
                student.get('room', None)
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