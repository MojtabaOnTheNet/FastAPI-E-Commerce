from sqlmodel import create_engine
from .models import *
from .core.config import settings

engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})

