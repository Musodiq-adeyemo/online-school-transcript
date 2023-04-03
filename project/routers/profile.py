from fastapi import APIRouter,Depends,status,UploadFile,File,HTTPException
from  project.models.schemas import ShowProfile,CreateProfile,DisplayProfile
from typing import List
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.repository import profile
from project.models.models import ProfileImage
import shutil 
from fastapi_jwt_auth import AuthJWT


router = APIRouter(
    tags=["Users Profile"],
    prefix = "/profile"
)

@router.post('/create',response_model=ShowProfile, status_code = status.HTTP_201_CREATED,summary="Create User Profile")
def create_profile(request:CreateProfile,db:Session = Depends(get_db)):
    
    return profile.create_profile(request,db)

@router.get('/get_all',response_model=List[ShowProfile], status_code = status.HTTP_200_OK,summary="Get All Users profile")
def get_all_profile(db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return profile.get_all_profile(db)

@router.get('/{id}',response_model=DisplayProfile, status_code = status.HTTP_200_OK,summary="Get Profile by Id")
def show_profile(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return profile.show_profile(id,db)

@router.put('/update/{id}',response_model=ShowProfile, status_code = status.HTTP_202_ACCEPTED,summary="Update User Profile")
def update_profile(id,request:CreateProfile,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return profile.update_profile(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete User Profile")
def delete_profile(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return profile.delete_profile(id,db,Authorize)

@router.post("/upload",summary="Upload your Profile picture")
def upload(profile_id:int,db:Session = Depends(get_db),file:UploadFile = File(...),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    with open(f"BlogPosts/static/profileimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = file.filename
    mimetype = file.content_type

    image_upload = ProfileImage(img = file.file.read(),minetype=mimetype, name=name,profile_id=profile_id)
    db.add(image_upload)
    db.commit()
    return f"{name} has been Successfully Uploaded"