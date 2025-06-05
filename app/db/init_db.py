import logging

from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.db.repositories.user import UserRepository
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize the database with a first superuser."""
    # Create a superuser if no users exist
    user = UserRepository.get_by_email(db, email="admin@example.com")
    if not user:
        user_in = UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin",
            is_superuser=True,
        )
        user = UserRepository.create(db, user_in=user_in)
        logger.info(f"Superuser created: {user.email}")
    else:
        logger.info(f"Superuser already exists: {user.email}")
