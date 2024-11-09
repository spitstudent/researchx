from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session 
from fastapi.responses import JSONResponse
import schemas, models
from database import get_db
import utils
import oauth2

router = APIRouter()


@router.post('/createuser', response_class=JSONResponse)
async def create_user(user: schemas.NewUser, db: Session  = Depends(get_db)):
        
    new_user = models.User(**user.model_dump())
    new_user.password = utils.hash(new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@router.post('/login', response_class=JSONResponse)
async def login(creds: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == creds.email).first()
    access_token = oauth2.create_access_token(data={'user_name': user.username,})
    
    if user:
        if utils.verify(creds.password, user.password):
            return {"token":access_token}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        raise HTTPException(status_code=404, detail="User not found")
