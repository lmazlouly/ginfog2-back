from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import ssl

from app.core.config.settings import settings

# Configure SSL for MySQL connection
ssl_args = {
    "ssl": {
        "ca": "ca.pem",  # Can specify CA certificate path if needed
        "cert": None,  # Can specify client cert if needed
        "key": None,  # Can specify client key if needed
        "ssl_verify_cert": True,
        "ssl_verify_identity": False
    }
}

engine = create_engine(settings.DATABASE_URL, connect_args=ssl_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
