from sqlalchemy import Integer,Column,DateTime,ForeignKey,Text,Float,String,Boolean,Enum
from project.models.database import Base,engine
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class Level(enum.Enum):
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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True)
    email = Column(String(200), unique=True,nullable=False)
    username = Column(String(100),unique=True,nullable=False)
    password = Column(String(100),nullable=False)
    matric_no = Column(Integer())
    course = relationship('Course',back_populates="student")
    profile = relationship('Profile',back_populates="owner")
    gpa =relationship('Gpa',back_populates="student_gpa")
    cgpa = relationship('Cgpa',back_populates='student_cgpa')
    school = relationship('School',back_populates='student')

    def __repr__(self):
        return f"<User : {self.username}>"


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer(), primary_key=True)
    matric_no = Column(Integer(),ForeignKey('users.matric_no'))
    othername =Column(String(100))
    firstname = Column(String(100),nullable=False)
    lastname = Column(String(100),nullable=False)
    dob = Column(DateTime(timezone=True))
    gender =Column(String(20),nullable=False)
    created_at = Column(DateTime(),default=datetime.utcnow)
    profile_picture = relationship('ProfileImage',back_populates ='owner_picture')
    owner = relationship('User',back_populates="profile")

    def __repr__(self):
        return f"<Profile : {self.lastname} {self.firstname}>"

class ProfileImage(Base):
    __tablename__ = 'profileimages'
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img =Column(String(70))
    minetype = Column(String(100))
    profile =Column(Integer(),ForeignKey('profiles.id'))
    owner_picture =relationship('Profile',back_populates="profile_picture")

    def __repr__(self):
        return f"UserImage {self.name}"

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer(), primary_key=True)
    matric_no = Column(Integer(),ForeignKey('users.matric_no'))
    course_title =Column(String(100))
    course_code = Column(String(100),nullable=False)
    grade = Column(String(100),nullable=False)
    grade_point = Column(Integer())
    level = Column(Integer())
    score = Column(Integer())
    course_unit = Column(Integer())
    student =relationship('User',back_populates="course")
    
    def __repr__(self):
        return f"Course {self.course_title}"

class Gpa(Base):
    __tablename__ = 'gpas'
    id = Column(Integer(), primary_key=True)
    matric_no = Column(Integer(),ForeignKey('users.matric_no'))
    level = Column(Integer())
    score = Column(Integer())
    course_unit = Column(Integer())
    grade_point = Column(Integer())
    gpa = Column(Float(precision=3),nullable=False)
    student_gpa = relationship('User',back_populates="gpa")
    def __repr__(self):
        return f"Gpa {self.matric_no}"

class Cgpa(Base):
    __tablename__ = 'cgpas'
    id = Column(Integer(), primary_key=True)
    matric_no = Column(Integer(),ForeignKey('users.matric_no'))
    level = Column(Integer())
    gpa = Column(Float(precision=3),nullable=False)
    no_of_semester = Column(Integer())
    student_cgpa = relationship('User',back_populates="cgpa")
    def __repr__(self):
        return f"Cgpa {self.matric_no}"

class School(Base):
    __tablename__ = 'school'
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    address = Column(Text())
    matric_no = Column(Integer(),ForeignKey('users.matric_no'))
    department = Column(Text())
    faculty = Column(Text())
    discipline= Column(Text())
    student = relationship('User',back_populates="school")
    
    def __repr__(self):
        return f"School {self.name}"

Base.metadata.create_all(bind=engine)