from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from project.models.models import Profile,User
from project.models.schemas import CreateProfile
from fastapi_jwt_auth import AuthJWT

def get_all_profile(db:Session):
    profiles = db.query(Profile).all()
    return profiles

def create_profile(request:CreateProfile,db:Session):
    new_profile = Profile (
        lastname= request.lastname,
        firstname= request.firstname,
        othername= request.othername,
        dob= request.dob,
        gender= request.gender,
        matric_no= request.matric_no
        )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

def delete_profile(id:int,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    delete_profile = db.query(Profile).filter(Profile.id == id).first()

    if delete_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if user.id == delete_profile.user:
        db.delete(delete_profile)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this post")

    return f"Profile with id {id} has been successfully deleted."
    
def update_profile(id:int,request:CreateProfile,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
   
    update_profile = db.query(Profile).filter(Profile.id == id).first()

    update_profile.lastname= request.lastname,
    update_profile.firstname= request.firstname,
    update_profile.othername= request.othername,
    update_profile.dob= request.dob,
    update_profile.gender= request.gender,
    update_profile.matric_no= request.matric_no

    if update_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    
    if user.id == update_profile.user :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this profile")
    
    return update_profile
    
def show_profile(id:int,db:Session):
    profile = db.query(Profile).filter(Profile.id==id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Profile with id {id} not found")
    
    return profile