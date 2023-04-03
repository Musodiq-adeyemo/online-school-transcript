from fastapi import APIRouter,Depends,status,HTTPException
from  project.models.schemas import CreateCgpa,DisplayCgpa
from typing import List
from sqlalchemy.orm import Session
from project.models.database import get_db
from fastapi_jwt_auth import AuthJWT
from project.repository import cgpa


router = APIRouter(
    tags=["User Cgpa"],
    prefix = "/cgpa"
)

@router.post('/create',response_model=DisplayCgpa, status_code = status.HTTP_201_CREATED,summary="Create Cgpa")
def create_cgpa(request:CreateCgpa,db:Session = Depends(get_db)):
    
    return cgpa.create_cgpa(request,db)

@router.put('/update/{id}',response_model=DisplayCgpa, status_code = status.HTTP_202_ACCEPTED,summary="Update Cgpa")
def update_cgpa(id,request:CreateCgpa,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return cgpa.update_cgpa(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Cgpa")
def delete_cgpa(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return cgpa.delete_cgpa(id,db,Authorize)


@router.get('/get_cgpa', status_code = status.HTTP_200_OK,summary="Get Student Cgpa")
def get_cgpa(matric_no:int,level:int,db:Session = Depends(get_db)):
    
    return cgpa.get_cgpa(db,matric_no,level)
    
    
    

