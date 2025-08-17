from pydantic_settings import BaseSettings
import argparse

class Settings(BaseSettings):
    db_port: str
    db_host: str
    db_user: str
    db_name: str
    db_pass: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

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

DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$'

parser = argparse.ArgumentParser()
parser.add_argument('--students', default='./data/students.json')
parser.add_argument('--rooms', default='./data/rooms.json')
parser.add_argument('--format', default='json')