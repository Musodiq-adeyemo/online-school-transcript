from fastapi import APIRouter,Depends,status,HTTPException
from  project.models.schemas import CreateGpa,DisplayGpa
from typing import List
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.repository import gpa
from fastapi_jwt_auth import AuthJWT

router = APIRouter(
    tags=["User Gpa"],
    prefix = "/gpa"
)

@router.post('/create',response_model=DisplayGpa, status_code = status.HTTP_201_CREATED,summary="Create Gpa")
def create_gpa(request:CreateGpa,db:Session = Depends(get_db)):
    return gpa.create_gpa(request,db)

@router.put('/update/{id}',response_model=DisplayGpa, status_code = status.HTTP_202_ACCEPTED,summary="Update Gpa")
def update_gpa(id,request:CreateGpa,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return gpa.update_gpa(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Gpa")
def delete_gpa(id,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    
    return gpa.delete_gpa(id,db,Authorize)


@router.get('/get_gpa', status_code = status.HTTP_200_OK,summary="Get Student Gpa")
def get_gpa(matric_no:int,level:int,db:Session = Depends(get_db)):
    return gpa.get_gpa(db,matric_no,level)

