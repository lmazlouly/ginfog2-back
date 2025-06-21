from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config.settings import settings
from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.db.repositories.user import UserRepository
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import User, UserCreate, UserUpdate, ChangePasswordRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, operation_id="login")
def login_access_token(
    response: Response,
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = UserRepository.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        print(f"Variable value: {form_data.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Set JWT as HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # Adjust based on your security requirements
        secure=settings.COOKIE_SECURE,  # Should be True in production with HTTPS
    )
    
    # Return token in body as well for compatibility
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=User, operation_id="register")
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Register a new user
    """
    user = UserRepository.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    username_exists = UserRepository.get_by_username(db, username=user_in.username)
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )
    
    user = UserRepository.create(db, user_in=user_in)
    return user


@router.get("/me", response_model=User, operation_id="getMe")
def read_users_me(current_user = Depends(get_current_user)) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=User, operation_id="updateProfile")
def update_users_me(
    *, 
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user = Depends(get_current_user)
) -> Any:
    """
    Update current user information
    """
    user = UserRepository.update(db, db_user=current_user, user_in=user_in)
    return user


@router.post("/logout", operation_id="logout")
def logout(response: Response) -> Any:
    """
    Logout user by clearing the cookie
    """
    response.delete_cookie(key="access_token")
    return {"status": "success"}


@router.post("/change-password", operation_id="changePassword")
def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: ChangePasswordRequest,
    current_user = Depends(get_current_user)
) -> Any:
    """
    Change current user password
    """
    # Verify current password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Verify new password confirmation
    if password_data.new_password != password_data.new_password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )
    
    # Ensure new password is different from old password
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    user_update = UserUpdate(password=password_data.new_password)
    UserRepository.update(db, db_user=current_user, user_in=user_update)
    
    return {"status": "success", "message": "Password changed successfully"}
