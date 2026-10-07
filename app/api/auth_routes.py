from fastapi import APIRouter, Depends , HTTPException,status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.auth  import hash_password
from app.schemas import LoginRequest, Token
from app.auth import verify_password, create_access_token , get_current_user

router = APIRouter(
    prefix  = "/auth",
    tags = ["Authentication"]

)




#--------------------------
# Signup Endpoint    
#--------------------------    


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    #Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Email already registered"
        )
    #hash password
    hashed_pw = hash_password(user.password)

    #create user
    new_user = models.User(
        email = user.email,
        password_hash = hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model = Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
            )
    
    # Verify password 
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Invalid email or password"
        ) 
    
    #Create JWT token (sub MUST be string)

    access_token = create_access_token( 
        data= {"sub": str(user.id)}
    )

    return {
        "access_token" : access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def read_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }

