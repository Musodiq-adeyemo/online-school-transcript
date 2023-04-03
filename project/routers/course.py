from fastapi import APIRouter,Depends,status,HTTPException
from  project.models.schemas import ShowCourse,CreateCourse,DisplayCourse,UserCourse
from typing import List
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.repository import course
from project.models.models import Course
from fastapi_jwt_auth import AuthJWT


router = APIRouter(
    tags=["User Courses"],
    prefix = "/course"
)

@router.get('/get_all',response_model=List[UserCourse], status_code = status.HTTP_200_OK,summary="Get All Courses")
def get_all_course(db:Session = Depends(get_db)):
    return course.get_all_course(db)

@router.post('/create',response_model=DisplayCourse, status_code = status.HTTP_201_CREATED,summary="Create Course")
def create_course(request:CreateCourse,db:Session = Depends(get_db)):
    return course.create_course(request,db)

@router.put('/update/{id}',response_model=UserCourse, status_code = status.HTTP_202_ACCEPTED,summary="Update Course")
def update_course(id,request:CreateCourse,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return course.update_course(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Course")
def delete_course(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return course.delete_course(id,db,Authorize)

@router.get('/{id}',response_model=DisplayCourse, status_code = status.HTTP_200_OK,summary="Get Course by Id")
def get_course(id,db:Session = Depends(get_db)):
    return course.get_course(id,db)

@router.get('/get_gpa', status_code = status.HTTP_200_OK,summary="Get Student Gpa")
def get_gpa(matric_no:int,level:int,db:Session = Depends(get_db)):
    return course.get_gpa(db,matric_no,level)

@router.get('/get_cgpa', status_code = status.HTTP_200_OK,summary="Get Stdent Cgpa")
def get_cgpa(matric_no:int,level:int,db:Session = Depends(get_db)):
    
    return course.get_cgpa(db,matric_no,level)