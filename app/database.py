import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/archreq_db")

# Fix for cloud providers (Supabase, Neon, Render) that output postgres://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush=False,
    bind = engine   

)
Base = declarative_base()


#---------------------------
# DB Dependency
#---------------------------

def get_db() -> Session: # type: ignore
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
