from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from project.models.models import Gpa,User
from project.models.schemas import CreateGpa
from fastapi_jwt_auth import AuthJWT


def create_gpa(request:CreateGpa,db:Session):
    if request.score <= 100 and request.score >= 70 :
        grade_point = 5 * request.course_unit
    elif request.score <= 69 and request.score >= 60 :
        grade_point = 4 * request.course_unit
    elif request.score <= 59 and request.score >= 50 :
        grade_point = 3 * request.course_unit
    elif request.score <= 49 and request.score >= 45 :
        grade_point = 2 * request.course_unit
    elif request.score <= 44 and request.score >= 40 :
        grade_point = 1 * request.course_unit
    elif request.score <= 39 and request.score >= 0 :
        grade_point = 0 * request.course_unit
    else:
        grade_point = 0
    
    new_gpa = Gpa(
        matric_no = request.matric_no,
        course_unit = request.course_unit,
        level = request.level,
        score = request.score,
        grade_point = grade_point
    )
    db.add(new_gpa)
    db.commit()
    db.refresh(new_gpa)

    return new_gpa

def update_gpa(id:int,request:CreateGpa,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    gpa_update = db.query(Gpa).filter(Gpa.id==id).first()
    
    gpa_update.grade_point = request.grade_point,
    gpa_update.matric_no = request.matric_no,
    gpa_update.course_unit = request.course_unit,
    gpa_update.level = request.level,
    gpa_update.score = request.score

    if user.id == gpa_update.user :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this post")
    
    
    return gpa_update

def delete_gpa(id:int,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    gpa_delete = db.query(Gpa).filter(Gpa.id==id).first()

    if gpa_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    if user.id == gpa_delete.user:
        db.delete(gpa_delete)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this Gpa")

    return f"Course with id {id} has been successfully deleted."

def get_gpa(matric_no:int,level:int,db:Session):
    gpas = db.query(Gpa).all()
    total_grade_point = 0
    total_course_unit = 0
    realGpa = 0
    cgpa = 0
    for gpa in gpas:
        if gpa.matric_no == matric_no and gpa.level == level:
            for i in gpa.course_unit:
                total_course_unit += i
            for j in gpa.grade_point:
                total_grade_point += j

    realGpa = total_grade_point / total_course_unit
    if gpa.level == 101 :
        cgpa = realGpa/1
    elif gpa.level == 102 :
        cgpa = realGpa/2
    elif gpa.level == 201 :
        cgpa = realGpa/3
    elif gpa.level == 202 :
        cgpa = realGpa/4
    elif gpa.level == 301 :
        cgpa = realGpa/5
    elif gpa.level == 302 :
        cgpa = realGpa/6
    elif gpa.level == 401 :
        cgpa = realGpa/7
    elif gpa.level == 402 :
        cgpa = realGpa/8
    elif gpa.level == 501 :
        cgpa = realGpa/9
    elif gpa.level == 502 :
        cgpa = realGpa/10

    return {"GPA":realGpa,"CGPA":cgpa}