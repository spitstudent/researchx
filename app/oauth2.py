from jose import JWTError, jwt
from datetime import timedelta
from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import schemas
import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl ='login')

SECRET_KEY = "b18e633da5c2450f964ede54bbdf92e6277565953b88dfb87ec13c8940f28a08"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    # Ensure user_role is included
    if "user_role" not in to_encode:
        to_encode["user_role"] = "default_role"  # or handle it appropriately

    # Create the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("user_name")
        user_role: str = payload.get("user_role")

        print("Decoded payload:", payload)

        if user_name is None or user_role is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(user_name=user_name, user_role=user_role)
        return token_data
    except JWTError as e:
        print("JWTError:", e) 
        raise credentials_exception



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)