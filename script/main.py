from script.db import AsyncDB
from script.logger import logger
import asyncio, json, argparse, datetime

parser = argparse.ArgumentParser()
parser.add_argument('--students', default='./data/students.json')
parser.add_argument('--rooms', default='./data/rooms.json')
parser.add_argument('--format', default='json')

async def parse_students_birthday(students):
    for student in students:
        try:
            student['birthday'] = datetime.datetime.strptime(student.get('birthday', ''), '%Y-%m-%dT%H:%M:%S.%f')
        except (ValueError, TypeError): 
            student['birthday'] = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

async def main(students_path=None, rooms_path=None):
    if students_path is None or rooms_path is None:
        logger.error("students_path or rooms_path is not specified")
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

if __name__ == '__main__':
    args = parser.parse_args()
    asyncio.run(main(students_path=args.students, rooms_path=args.rooms))