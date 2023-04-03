from fastapi import APIRouter,Depends,status,HTTPException
from  project.models.schemas import CreateSchool,DisplaySchool
from typing import List
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.repository import school
from fastapi_jwt_auth import AuthJWT



router = APIRouter(
    tags=["User School Information"],
    prefix = "/school"
)

@router.post('/create',response_model=DisplaySchool, status_code = status.HTTP_201_CREATED,summary="Create Student School Info")
def create_school(request:CreateSchool,db:Session = Depends(get_db)):
    
    return school.create_school(request,db)

@router.put('/update/{id}',response_model=DisplaySchool, status_code = status.HTTP_202_ACCEPTED,summary="Update Student School Info")
def update_school(id,request:CreateSchool,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return school.update_school(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Student School Info")
def delete_school(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return school.delete_school(id,db,Authorize)


@router.get('/get_school', status_code = status.HTTP_200_OK,summary="Get Student School Info")
def get_school(matric_no:int,level:int,db:Session = Depends(get_db)):
    
    return school.get_school(db,matric_no,level)

