from sqlmodel import SQLModel, create_engine, Session

db_file = "auratrack.db"
db_url = f"sqlite:///{db_file}"

engine = create_engine(db_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as db:
        yield db
