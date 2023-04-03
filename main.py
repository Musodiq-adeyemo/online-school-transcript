from fastapi import FastAPI,Request,Depends,Form,status,UploadFile,File,HTTPException
from project.routers import authentication
from project.routers import users
from project.routers import profile
from project.routers import school
from project.routers import course
from project.routers import gpa
from project.routers import cgpa
from fastapi.responses import HTMLResponse,RedirectResponse,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from project.models.database import get_db
from project.models.models import Course,User,Profile,ProfileImage,School
from fastapi_jwt_auth import AuthJWT
from datetime import timedelta
from project.security.hashing import Hash
from project.models.schemas import Setting
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil

app= FastAPI(
    docs_url = "/docs",
    redoc_url= "/redocs",
    title="SIRMUSO ONLINE TRANSCRIPT API",
    description="FRAMEWORK FOR SIRMUSO ONLINE TRANSCRIPT",
    version="4.0",
    openapi_url="/api/v2/openapi.json",   
)

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(school.router)
app.include_router(course.router)
app.include_router(gpa.router)
app.include_router(cgpa.router)


access_token_expire =timedelta(minutes=120)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

@AuthJWT.load_config
def get_config():
    return Setting()


templates = Jinja2Templates(directory="project/templates")
app.mount("/static",StaticFiles(directory="project/static"),name="static")


@app.get("/",response_class=HTMLResponse,tags=["Template"])
def home(request: Request,Authorize:AuthJWT=Depends()):
    current_user = Authorize.get_jwt_subject()
    return templates.TemplateResponse("home.html",{"request":request,"current_user":current_user})

# USER REGISTRATION
@app.get("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request):
    return templates.TemplateResponse("signup.html",{"request":request})

@app.post("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request,username:str=Form(...),email:str=Form(...),password:str=Form(...),password2:str=Form(...),matric_no : int=Form(...), db:Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.username==username).first()
    email_exist = db.query(User).filter(User.email==email).first()
    errors=[]

    if email_exist:
        errors.append("Email Already Exist,Login or Change Email.")

    if user_exist:
        errors.append("Username Already Exist,Try another one.")
    
    if not email :
        errors.append("Not a proper Email")

    if password == password2 and len(password) > 7 :
        new_user = User(username=username,email=email,password=Hash.bcrypt(password),matric_no=matric_no)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        redirect_url = "signin"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
    if len(errors) > 0 :
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})
    else:
        errors.append("Password dont match or less than 8 charaters")
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})

#LOGIN AUTHENTICATION
@app.get("/signin",tags=["Template"])
def login(request: Request):
    return templates.TemplateResponse("signin.html",{"request":request})


@app.post("/signin",tags=["Template"])
def login(request: Request,response:Response,Authorize:AuthJWT=Depends(),username:str=Form(...),password:str=Form(...),db:Session = Depends(get_db)):
    errors = []
    user = db.query(User).filter(User.username==username).first()

    if user is None:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})
    
    verify_password = Hash.verify_password(password,user.password)

    if (username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=user.username,expires_time=access_token_expire)
        redirect_url = "/profile_settings"
        resp = RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
        Authorize.set_access_cookies(access_token,resp)
        return resp
    else:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})

# profile settings route
@app.get("/profile_settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("settings.html",{"request":request})

@app.post("/profile_settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,matric_no:int=Form(...),firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),gender:str=Form(...),dob:datetime=Form(...), db:Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.matric_no == matric_no).first()
    if not profile:
        new_profile = Profile(lastname=lastname,matric_no=matric_no,dob=dob,gender=gender,firstname=firstname,othername=othername)
        db.add(new_profile)
        db.commit()
        redirect_url = "/profile"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)    
    else: 
        return templates.TemplateResponse("settings.html",{"request":request,"new_user":new_profile})

#profile page
@app.get("/profile",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    current_user = Authorize.get_jwt_subject()
    users = db.query(User).all()
    profiles = db.query(Profile).all()
    schools = db.query(School).all()
    images = db.query(ProfileImage).all()

    return templates.TemplateResponse("dashboard.html",{"request":request,"users":users,"profiles":profiles,"schools":schools,'current_user':current_user,'images':images})

#update profile
@app.get("/profile/{id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    profile = db.query(Profile).filter(Profile.id == id).first()
    return templates.TemplateResponse("dashboard.html",{"request":request,"profile":profile})

@app.post("/profile/{id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request, id:int,matric_no:int=Form(...),firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),gender:str=Form(...),dob:datetime=Form(...), db:Session = Depends(get_db)):
    try:
        update_profile = db.query(Profile).filter(Profile.id == id).first()

        update_profile.lastname = lastname,
        update_profile.firstname = firstname,
        update_profile.othername = othername,
        update_profile.dob = dob,
        update_profile.gender = gender,
        update_profile.matric_no = matric_no
    
        db.commit()
        redirect_url = "/profile"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("dashboard.html",{"request":request,"update_profile":update_profile})


#delete profile
@app.get("/delete_profile/{id}",response_class=HTMLResponse,tags=["Template"])
def profile_delete(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    delete_profile = db.query(Profile).filter(Profile.id == id).first()
    if delete_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        db.delete(delete_profile)
        db.commit()
        redirect_url = "/profile_settings"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

# profile image
@app.get("/profile_image",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_profile.html",{"request":request})

@app.post("/profile_image",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,profile_id:int=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    try:
        with open(f"project/static/profileimages/{file.filename}","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        name = secure_filename(file.filename)
        mimetype = file.content_type

        image_upload = ProfileImage(img = file.file.read(),minetype=mimetype, name=name,profile_id=profile_id)
        db.add(image_upload)
        db.commit()
        redirect_url = "/profile_settings"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("upload_profile.html",{"request":request,"image_upload":image_upload})

# create school route
@app.get("/create/school_info",response_class=HTMLResponse,tags=["Template"])
def school_info(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("school.html",{"request":request})

@app.post("/create/school_info",response_class=HTMLResponse,tags=["Template"])
def school_info(request: Request,matric_no:int=Form(...),name:str=Form(...),address:str=Form(...),faculty:str=Form(...),department:str=Form(...),discipline:str=Form(...), db:Session = Depends(get_db)):
    new_student = School(
        name = name,
        address = address,
        matric_no = matric_no,
        department = department,
        faculty = faculty,
        discipline = discipline
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    redirect_url = "/register/course"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

#update school route
@app.get("/update/school_info/{id}",response_class=HTMLResponse,tags=["Template"])
def update_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    school = db.query(School).filter(School.id == id).first()
    return templates.TemplateResponse("edit_school.html",{"request":request,"school":school})

@app.post("/update/school_info/{id}",response_class=HTMLResponse,tags=["Template"])
def update_school(request: Request,id:int,matric_no:int=Form(...),name:str=Form(...),address:str=Form(...),faculty:str=Form(...),department:str=Form(...),discipline:datetime=Form(...), db:Session = Depends(get_db)):
    school = db.query(School).filter(School.id== id).first()
    school.name = name,
    school.address =address,
    school.matric_no =matric_no,
    school.department =department,
    school.faculty =faculty,
    school.discipline =discipline

    db.commit()

    redirect_url = "/profile"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)


#delete school route
@app.get("/delete/school_info/{id}",response_class=HTMLResponse,tags=["Template"])
def delete_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    school = db.query(School).filter(School.id == id).first()

    if school  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        db.delete(school)
        db.commit()
        redirect_url = "/profile"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

@app.get("/check/school/{id}",response_class=HTMLResponse,tags=["Template"])
def check_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    school = db.query(School).filter(School.id == id).first()
    return templates.TemplateResponse("check_school.html",{"request":request,"school":school})



#create course
@app.get("/register/course",response_class=HTMLResponse,tags=["Template"])
def register_course(request: Request,Authorize:AuthJWT=Depends(),db:Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
        user = db.query(User).filter(User.username==username).first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("course.html",{"request":request,'user':user})

@app.post("/register/course",response_class=HTMLResponse,tags=["Template"])
def register_course(request: Request,matric_no:int=Form(...),course_title:str=Form(...),course_code:str=Form(...),course_unit:int=Form(...),score:int=Form(...),level:int=Form(...), db:Session = Depends(get_db)):
    if score <= 100 and score >= 70 :
        grade = 'A'
        grade_point = 5 * course_unit
    elif score <= 69 and score >= 60 :
        grade = 'B'
        grade_point = 4 * course_unit
    elif score <= 59 and score >= 50 :
        grade = 'C'
        grade_point = 3 * course_unit
    elif score <= 49 and score >= 45 :
        grade = 'CD'
        grade_point = 2 * course_unit
    elif score <= 44 and score >= 40 :
        grade = 'D'
        grade_point = 1 * course_unit
    elif score <= 39 and score >= 0 :
        grade = 'F'
        grade_point = 0 * course_unit
    else:
        grade_point = 0
    
    new_course = Course(
        course_title = course_title,
        course_code = course_code,
        matric_no = matric_no,
        course_unit = course_unit,
        level = level,
        score = score,
        grade = grade,
        grade_point = grade_point
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return templates.TemplateResponse("course.html",{"request":request})
# edit course
@app.get("/update/course/{id}",response_class=HTMLResponse,tags=["Template"])
def update_course(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("edit_course.html",{"request":request})

@app.post("/update/course/{id}",response_class=HTMLResponse,tags=["Template"])
def update_course(request: Request, id:int,matric_no:int=Form(...),course_title:str=Form(...),course_code:str=Form(...),course_unit:int=Form(...),score:int=Form(...),level:int=Form(...), db:Session = Depends(get_db)):
    course_update = db.query(Course).filter(Course.id==id).first()
    
    course_update.course_title = course_title,
    course_update.course_code =course_code,
    course_update.matric_no = matric_no,
    course_update.course_unit =course_unit,
    course_update.level = level,
    course_update.score = score

    db.commit()

    redirect_url = "/profile"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

#delete course
@app.get("/delete/course/{id}",response_class=HTMLResponse,tags=["Template"])
def delete_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    course_delete = db.query(Course).filter(Course.id==id).first()

    if school  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        db.delete(course_delete)
        db.commit()
        redirect_url = "register_course"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

@app.get("/transcript/{id}",response_class=HTMLResponse,tags=["Template"])
def transcript(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")

    user = db.query(User).filter(User.id==id).first()

    schools = db.query(School).all()

    profiles = db.query(Profile).all()

    courses = db.query(Course).all()

    units = []
    points = []
    total_grade_point = 0
    total_course_unit = 0
    
    gpa101 = 0
    gpa102 = 0
    gpa201 = 0
    gpa202 = 0
    gpa301 = 0
    gpa302 = 0
    gpa401 = 0
    gpa402 = 0

    cgpa101 = 0
    cgpa102 = 0
    cgpa201 = 0
    cgpa202 = 0
    cgpa301 = 0
    cgpa302 = 0
    cgpa401 = 0
    cgpa402 = 0

    for course in courses:
        if course.matric_no == user.matric_no:
            if course.level == 101:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa101 = total_grade_point/total_course_unit
                    gpa101 =round(gpa101,2)
                    cgpa101 = gpa101
            elif course.level == 102:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa102 = total_grade_point/total_course_unit
                    gpa102 =round(gpa102,2)
                    cgpa102 = (gpa101 + gpa102)/2
                    cgpa102 =round(cgpa102,2)
            elif course.level == 201:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa201 = total_grade_point/total_course_unit
                    gpa201 =round(gpa201,2)
                    cgpa201 = (gpa101 + gpa102 + gpa201)/3
                    cgpa201 =round(cgpa201,2)
            elif course.level == 202:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa202 = total_grade_point/total_course_unit
                    gpa202 =round(gpa202,2)
                    cgpa202 = (gpa101 + gpa102 + gpa201 +gpa202)/4
                    cgpa202 =round(cgpa202,2)
            elif course.level == 301:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa301 = total_grade_point/total_course_unit
                    gpa301 =round(gpa301,2)
                    cgpa301 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301)/5
                    cgpa301 =round(cgpa301,2)
            elif course.level == 302:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa302 = total_grade_point/total_course_unit
                    gpa302 =round(gpa302,2)
                    cgpa302 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302)/6
                    cgpa302 =round(cgpa302,2)
            elif course.level == 401:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa401 = total_grade_point/total_course_unit
                    gpa401 =round(gpa401,2)
                    cgpa401 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302 + gpa401)/7
                    cgpa401 =round(cgpa401,2)
            elif course.level == 402:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa402 = total_grade_point/total_course_unit
                    gpa402 =round(gpa402,2)
                    cgpa402 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302 + gpa401 + gpa402)/8
                    cgpa402 =round(cgpa402,2)

    gpa101 = gpa101
    gpa102 = gpa102
    gpa201 = gpa201
    gpa202 = gpa202
    gpa301 = gpa301
    gpa302 = gpa302
    gpa401 = gpa401
    gpa402 = gpa402

    cgpa101 = cgpa101
    cgpa102 = cgpa102
    cgpa201 = cgpa201
    cgpa202 = cgpa202
    cgpa301 = cgpa301
    cgpa302 = cgpa302
    cgpa401 = cgpa401
    cgpa402 = cgpa402
    
    return templates.TemplateResponse("transcript.html",
    {
        "request":request,
        "user":user,
        "courses":courses,
        "schools":schools,
        "profiles":profiles,
        "gpa101" :gpa101,
        "gpa102": gpa102,
        "gpa201": gpa201,
        "gpa202": gpa202,
        "gpa301" : gpa301,
        "gpa302" : gpa302,
        "gpa401" : gpa401,
        "gpa402": gpa402,
        "cgpa101" :cgpa101,
        "cgpa102": cgpa102,
        "cgpa201": cgpa201,
        "cgpa202": cgpa202,
        "cgpa301" : cgpa301,
        "cgpa302" : cgpa302,
        "cgpa401" : cgpa401,  
        "cgpa402":cgpa402

    })

@app.get("/check/transcript/{id}",response_class=HTMLResponse,tags=["Template"])
def check_transcript(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
   
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
   
    user = db.query(User).filter(User.id==id).first()

    schools = db.query(School).all()

    profiles = db.query(Profile).all()

    courses = db.query(Course).all()

    units = []
    points = []
    total_grade_point = 0
    total_course_unit = 0
    
    gpa101 = 0
    gpa102 = 0
    gpa201 = 0
    gpa202 = 0
    gpa301 = 0
    gpa302 = 0
    gpa401 = 0
    gpa402 = 0

    cgpa101 = 0
    cgpa102 = 0
    cgpa201 = 0
    cgpa202 = 0
    cgpa301 = 0
    cgpa302 = 0
    cgpa401 = 0
    cgpa402 = 0

    for course in courses:
        if course.matric_no == user.matric_no:
            if course.level == 101:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa101 = total_grade_point/total_course_unit
                    gpa101 =round(gpa101,2)
                    cgpa101 = gpa101
            elif course.level == 102:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa102 = total_grade_point/total_course_unit
                    gpa102 =round(gpa102,2)
                    cgpa102 = (gpa101 + gpa102)/2
                    cgpa102 =round(cgpa102,2)
            elif course.level == 201:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa201 = total_grade_point/total_course_unit
                    gpa201 =round(gpa201,2)
                    cgpa201 = (gpa101 + gpa102 + gpa201)/3
                    cgpa201 =round(cgpa201,2)
            elif course.level == 202:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa202 = total_grade_point/total_course_unit
                    gpa202 =round(gpa202,2)
                    cgpa202 = (gpa101 + gpa102 + gpa201 +gpa202)/4
                    cgpa202 =round(cgpa202,2)
            elif course.level == 301:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa301 = total_grade_point/total_course_unit
                    gpa301 =round(gpa301,2)
                    cgpa301 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301)/5
                    cgpa301 =round(cgpa301,2)
            elif course.level == 302:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa302 = total_grade_point/total_course_unit
                    gpa302 =round(gpa302,2)
                    cgpa302 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302)/6
                    cgpa302 =round(cgpa302,2)
            elif course.level == 401:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa401 = total_grade_point/total_course_unit
                    gpa401 =round(gpa401,2)
                    cgpa401 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302 + gpa401)/7
                    cgpa401 =round(cgpa401,2)
            elif course.level == 402:
                units.append(course.course_unit)
                points.append(course.grade_point)
                for i in units:
                    total_course_unit += i
                for j in points:
                    total_grade_point += j
                    gpa402 = total_grade_point/total_course_unit
                    gpa402 =round(gpa402,2)
                    cgpa402 = (gpa101 + gpa102 + gpa201 +gpa202 + gpa301+gpa302 + gpa401 + gpa402)/8
                    cgpa402 =round(cgpa402,2)

    gpa101 = gpa101
    gpa102 = gpa102
    gpa201 = gpa201
    gpa202 = gpa202
    gpa301 = gpa301
    gpa302 = gpa302
    gpa401 = gpa401
    gpa402 = gpa402

    cgpa101 = cgpa101
    cgpa102 = cgpa102
    cgpa201 = cgpa201
    cgpa202 = cgpa202
    cgpa301 = cgpa301
    cgpa302 = cgpa302
    cgpa401 = cgpa401
    cgpa402 = cgpa402

     
    return templates.TemplateResponse("check_transcript.html",
    {
        "request":request,
        "user":user,
        "courses":courses,
        "schools":schools,
        "profiles":profiles,
        "gpa101" :gpa101,
        "gpa102": gpa102,
        "gpa201": gpa201,
        "gpa202": gpa202,
        "gpa301" : gpa301,
        "gpa302" : gpa302,
        "gpa401" : gpa401,
        "gpa402": gpa402,
        "cgpa101" :cgpa101,
        "cgpa102": cgpa102,
        "cgpa201": cgpa201,
        "cgpa202": cgpa202,
        "cgpa301" : cgpa301,
        "cgpa302" : cgpa302,
        "cgpa401" : cgpa401,  
        "cgpa402":cgpa402

    })
        
    
@app.get("/logout")
def logout(Authorize:AuthJWT=Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies
    
    redirect_url = "/"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
