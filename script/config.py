from pydantic_settings import BaseSettings

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
