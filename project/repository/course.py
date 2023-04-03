from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from project.models.models import Course,User
from project.models.schemas import CreateCourse
from fastapi_jwt_auth import AuthJWT

def create_course(request:CreateCourse,db:Session):

    if request.score <= 100 and request.score >= 70 :
        grade = 'A'
        grade_point = 5 * request.course_unit
    elif request.score <= 69 and request.score >= 60 :
        grade = 'B'
        grade_point = 4 * request.course_unit
    elif request.score <= 59 and request.score >= 50 :
        grade = 'C'
        grade_point = 3 * request.course_unit
    elif request.score <= 49 and request.score >= 45 :
        grade = 'CD'
        grade_point = 2 * request.course_unit
    elif request.score <= 44 and request.score >= 40 :
        grade = 'D'
        grade_point = 1 * request.course_unit
    elif request.score <= 39 and request.score >= 0 :
        grade = 'F'
        grade_point = 0 * request.course_unit
    else:
        grade_point = 0
    
    new_course = Course(
        course_title = request.course_title,
        course_code = request.course_code,
        matric_no = request.matric_no,
        course_unit = request.course_unit,
        level = request.level,
        score = request.score,
        grade = grade,
        grade_point = grade_point
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

def update_course(id:int,request:CreateCourse,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    course_update = db.query(Course).filter(Course.id==id).first()
    
    course_update.course_title = request.course_title,
    course_update.course_code = request.course_code,
    course_update.matric_no = request.matric_no,
    course_update.course_unit = request.course_unit,
    course_update.level = request.level,
    course_update.score = request.score

    if user.id == course_update.user :
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to update this Course")
    
    
    return course_update

def delete_course(id:int,db:Session,Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()
    
    course_delete = db.query(Course).filter(Course.id==id).first()

    if course_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    if user.id == course_delete.user:
        db.delete(course_delete)
        db.commit()
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not Authorized to delete this Course")

    return f"Course with id {id} has been successfully deleted."

def get_course(id:int,db:Session):
    course = db.query(Course).filter(Course.id==id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Course with id {id} not found")
    
    return course

def get_gpa(matric_no:int,level:int,db:Session):
    courses = db.query(Course).all()
    course_unit = 0
    grade_point = 0
    total_grade_point = 0
    total_course_unit = 0
    for course in courses:
        if course.matric_no == matric_no and course.level == level:
            for i in course.course_unit:
                course_unit.append(i)
            for i in course.grade_point:
                grade_point.append(i)    
                grade_points = [grade_point * course_unit for grade_point,course_unit in zip(grade_point,course_unit)]
                for i in grade_points:
                    total_grade_point += i
                for k in course_unit:
                    total_course_unit += k
                gpa = total_grade_point / total_course_unit

    return {"Gpa":gpa}

def get_cgpa(matric_no:int,level:int,db:Session):
    courses = db.query(Course).all()
    course_unit = []
    grade_point = []
    total_grade_point = 0
    total_course_unit = 0
    for course in courses:
        if course.matric_no == matric_no and course.level == level:
            for i in course.course_unit:
                course_unit.append(i)
            for i in course.grade_point:
                grade_point.append(i)    
                grade_points = [grade_point * course_unit for grade_point,course_unit in zip(grade_point,course_unit)]
                for i in grade_points:
                    total_grade_point += i
                for k in course_unit:
                    total_course_unit += k
                gpa = total_grade_point / total_course_unit
                if course.level == 101 :
                    cgpa = gpa/1
                elif course.level == 102 :
                    cgpa = gpa/2
                elif course.level == 201 :
                    cgpa = gpa/3
                elif course.level == 202 :
                    cgpa = gpa/4
                elif course.level == 301 :
                    cgpa = gpa/5
                elif course.level == 302 :
                    cgpa = gpa/6
                elif course.level == 401 :
                    cgpa = gpa/7
                elif course.level == 402 :
                    cgpa = gpa/8
                elif course.level == 501 :
                    cgpa = gpa/9
                elif course.level == 502 :
                    cgpa = gpa/10

    return {"CGPA":cgpa}

def get_all_course(db:Session):
    courses = db.query(Course).all()
    return courses