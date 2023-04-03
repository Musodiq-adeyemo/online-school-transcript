from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from project.models.models import School,User
from project.models.schemas import CreateSchool
from fastapi_jwt_auth import AuthJWT



def create_school(request:CreateSchool,db:Session):
    new_student = School(
        name = request.name,
        address = request.address,
        matric_no = request.matric_no,
        department = request.department,
        faculty = request.faculty,
        discipline = request.discipline
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

def update_school(id:int,request:CreateSchool,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    school = db.query(School).filter(School.id == id).first()
    school.name = request.name,
    school.address = request.address,
    school.matric_no = request.matric_no,
    school.department = request.department,
    school.faculty = request.faculty,
    school.discipline = request.discipline

    if user.id == school.user :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this school information")
    
    
    return school

def delete_school(id:int,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    school = db.query(School).filter(School.id == id).first()

    if school  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    if user.id == school.user:
        db.delete(school)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this school information")

    return f"School with id {id} has been successfully deleted."

def get_school(id:int,db:Session):
    school = db.query(School).filter(School.id == id).first()

    if school  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        return school