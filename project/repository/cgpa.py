from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from project.models.models import Cgpa,User
from project.models.schemas import CreateCgpa
from fastapi_jwt_auth import AuthJWT



def create_cgpa(request:CreateCgpa,db:Session):
    new_gpa = Cgpa(
        matric_no = request.matric_no,
        gpa = request.gpa,
        level = request.level,
        no_of_semester = request.no_of_semester
    )

    db.add(new_gpa)
    db.commit()
    db.refresh(new_gpa)
    return new_gpa

def update_cgpa(id:int,request:CreateCgpa,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    gpa = db.query(Cgpa).filter(Cgpa.id == id).first()
    
    gpa.matric_no = request.matric_no,
    gpa.gpa = request.gpa,
    gpa.level = request.level,
    gpa.no_of_semester = request.no_of_semester

    if user.id == gpa.user:
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this cgpa information")

    return gpa

def delete_cgpa(id:int,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    gpa_delete = db.query(Cgpa).filter(Cgpa.id==id).first()

    if gpa_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    if user.id == gpa_delete.user:
        db.delete(gpa_delete)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this cgpa information")

    return f"Cgpa with id {id} has been successfully deleted."

def get_cgpa(id:int,db:Session):
    gpa = db.query(Cgpa).filter(Cgpa.id==id).first()

    if gpa  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        return gpa