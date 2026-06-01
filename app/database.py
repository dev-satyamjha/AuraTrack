from sqlmodel import SQLModel, create_engine, Session
import os

sqlite_file_name = "auratrack.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Generates the tables based on our SQLModel schemas."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency injection for database sessions."""
    with Session(engine) as session:
        yield session
