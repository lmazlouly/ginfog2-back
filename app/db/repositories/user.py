from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security.password import get_password_hash, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    @staticmethod
    def get(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_superuser=user_in.is_superuser,
            is_active=user_in.is_active,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate) -> User:
        user_data = user_in.dict(exclude_unset=True)
        if "password" in user_data and user_data["password"]:
            user_data["hashed_password"] = get_password_hash(user_data["password"])
            del user_data["password"]
        for field, value in user_data.items():
            setattr(db_user, field, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> User:
        user = db.query(User).get(user_id)
        if user:
            db.delete(user)
            db.commit()
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserRepository.get_by_email(db, email=email)
        if not user:
            user = UserRepository.get_by_username(db, username=email)
            if not user:
                return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
