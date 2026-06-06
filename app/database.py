from sqlmodel import SQLModel, create_engine
# from models import *

SQLITE_URL = "sqlite:///database.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

