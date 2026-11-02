import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Fetch connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./citizen_dev.db")

# 2. Render.com URI Fix: Render provides connection strings prefixed with postgres://
# whereas SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Configure Engine
# pool_pre_ping=True handles stale connections and auto-reconnects after cloud idle periods
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# 4. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Declarative Base
Base = declarative_base()

# 6. Database Dependency Generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

