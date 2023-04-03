from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.models.models import User
from fastapi_jwt_auth import AuthJWT
from datetime import timedelta
from project.security.hashing import Hash
from project.models.schemas import Settings,Login


router = APIRouter(
    tags=["Authentication"]
)

access_token_expire =timedelta(minutes=30)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

@AuthJWT.load_config
def get_config():
    return Settings()

@router.post('/login',summary="Login Your Account")
def login(request:Login,Authorize:AuthJWT=Depends(), db:Session=Depends(get_db)):
    
    user = db.query(User).filter(User.username==request.username).first()
    
    verify_password = Hash.verify_password(request.password,user.password)
   
    if (request.username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=request.username,expires_time=access_token_expire, algorithm=access_algorithm)
        refresh_token = Authorize.create_refresh_token(subject=request.username,expires_time=refresh_token_expire,algorithm=refresh_algorithm)
        
        #Authorize.set_access_cookies(access_token)
        #Authorize.set_refresh_cookies(refresh_token)
        return {"access-token":access_token,"refresh_token":refresh_token}

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Username or Password")
        

@router.get("/login/refresh",summary="Refresh Login Access Token")
def refresh_login(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    current_user = Authorize.get_jwt_subject()
    
    new_access_token = Authorize.create_access_token(subject=current_user,fresh=True,expires_time=new_access_token_expire)
    #Authorize.set_access_cookies(new_access_token)
    
    return {"new_access_token" : new_access_token}


@router.get("/current_user",summary="Get Current User")
def get_user(Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")

    current_user = Authorize.get_jwt_subject()
    return {"current_user":current_user}
