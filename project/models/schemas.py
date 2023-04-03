from pydantic import BaseModel,Field,BaseSettings
from typing import List,Optional
from datetime import datetime
from enum import Enum

class Level(int,Enum):
    LEVEL1A = 101,
    LEVEL1B = 102,
    LEVEL2A = 201,
    LEVEL2B = 202,
    LEVEL3A = 301,
    LEVEL3B = 302,
    LEVEL4A = 401,
    LEVEL4B = 402,
    LEVEL5A = 501,
    LEVEL5B = 502


class CreateUser(BaseModel):
    email: str
    username : str
    password : str
    matric_no : int

class ShowUser(BaseModel):
    username : str
    email: str
    class Config():
        orm_mode = True

class ShowProfile(BaseModel):
    lastname : str
    firstname : str
    gender : str
    class Config():
        orm_mode = True

class ShowProfileImage(BaseModel):
    name : str
    class Config():
        orm_mode = True

class ShowCourse(BaseModel):
    course_title = str
    course_code = str
    class Config():
        orm_mode = True

class UserCourse(BaseModel):
    course_title : str
    course_code : str
    course_unit : int
    class Config():
        orm_mode = True

class ShowCgpa(BaseModel):
    gpa: float
    class Config():
        orm_mode = True

class ShowSchool(BaseModel):
    name : str
    class Config():
        orm_mode = True

class DisplayUser(BaseModel):
    id: int
    email: str
    username : str
    is_active : bool
    is_staff : bool
    course : List[UserCourse]= []
    cgpa : List[ShowCgpa]=[]
    school: List[ShowSchool] =[]
    profile : List[ShowProfile] = []
    class Config():
        orm_mode = True

class CreateProfile(BaseModel):
    lastname : str
    firstname : str
    othername : str
    dob : datetime
    matric_no : int
    gender : str

class DisplayProfile(BaseModel):
    id: int
    lastname : str
    firstname : str
    dob : datetime
    matric_no : int
    othername : str
    gender : str
    profile_image : List[ShowProfileImage] = []
    class Config():
        orm_mode = True

class ProfileImage(BaseModel):
    id : int
    name : str
    profile : int

class CreateCourse(BaseModel):
    matric_no : int
    course_title : str
    course_code : str
    course_unit : int
    level : int
    score : int
    

class DisplayCourse(BaseModel):
    id : int
    matric_no : int
    course_title : str
    course_code : str
    course_unit : int
    level : int
    score : int
    grade : str
    grade_point : int
    class Config():
        orm_mode = True

class CreateGpa(BaseModel):
    matric_no : int
    course_unit : str
    level : int
    score : int
    gpa : float
    grade_point : int

class DisplayGpa(BaseModel):
    id : int
    matric_no : int
    course_unit : str
    level : int
    score : int
    gpa : float
    grade_point : int
    class Config():
        orm_mode = True

class CreateCgpa(BaseModel):
    matric_no : int
    gpa : float
    level : int
    no_of_semester : int
    

class DisplayCgpa(BaseModel):
    id : int
    matric_no : int
    gpa : float
    level : int
    no_of_semester : int
    class Config():
        orm_mode = True

class CreateSchool(BaseModel):
    matric_no : int
    name : str
    address : str
    department : str
    faculty : str
    discipline : str
    

class DisplaySchool(BaseModel):
    id : int
    matric_no : int
    name : str
    address : str
    department : str
    faculty : str
    discipline : str
    class Config():
        orm_mode = True

class Login(BaseModel):
    username : str
    password : str

class Settings(BaseModel):
    authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
    authjwt_decode_algorithms : set = {"HS384","HS512"}
    #authjwt_token_location : set = {"cookies"}
    #auth_jwt_cookies_csrf_protect : bool = False

class Setting(BaseModel):
   authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
   #authjwt_decode_algorithms : set = {"HS384","HS512"}
   authjwt_token_location : set = {"cookies"}
   auth_jwt_cookies_csrf_protect : bool = False 