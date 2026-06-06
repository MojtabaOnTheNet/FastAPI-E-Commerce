from sqlmodel import SQLModel, create_engine
import models

SQLITE_URL = "sqlite:///database.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

