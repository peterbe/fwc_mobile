# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class TurbineGroup(models.Model):
    group_id = models.IntegerField()
    group_name = models.CharField(max_length=192)
    class Meta:
        db_table = u'TURBINE_GROUP'

class TurbinePermission(models.Model):
    permission_id = models.IntegerField()
    permission_name = models.CharField(max_length=192)
    class Meta:
        db_table = u'TURBINE_PERMISSION'

class TurbineRole(models.Model):
    role_id = models.IntegerField()
    role_name = models.CharField(max_length=192)
    class Meta:
        db_table = u'TURBINE_ROLE'

class TurbineRolePermission(models.Model):
    role_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'TURBINE_ROLE_PERMISSION'

class TurbineUser(models.Model):
    user_id = models.IntegerField()
    login_name = models.CharField(max_length=192)
    password_value = models.CharField(max_length=150)
    first_name = models.CharField(max_length=192)
    last_name = models.CharField(max_length=192)
    email = models.CharField(max_length=192, blank=True)
    confirm_value = models.CharField(max_length=48, blank=True)
    modified = models.DateTimeField()
    created = models.DateTimeField()
    last_login = models.DateTimeField()
    objectdata = models.TextField(blank=True)
    class Meta:
        db_table = u'TURBINE_USER'

class TurbineUserGroupRole(models.Model):
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    role_id = models.IntegerField()
    class Meta:
        db_table = u'TURBINE_USER_GROUP_ROLE'

class Article(models.Model):
    headline = models.CharField(max_length=300)
    summary = models.TextField()
    type = models.CharField(max_length=150)
    content = models.TextField()
    author = models.CharField(max_length=300)
    date = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    owner = models.CharField(max_length=300)
    class Meta:
        db_table = u'article'

class ArticleStage(models.Model):
    headline = models.CharField(max_length=300)
    summary = models.TextField()
    type = models.CharField(max_length=150)
    content = models.TextField()
    author = models.CharField(max_length=300)
    date = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    owner = models.CharField(max_length=300)
    class Meta:
        db_table = u'article_stage'

class Calendar(models.Model):
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    event = models.CharField(max_length=150)
    class Meta:
        db_table = u'calendar'

class CalendarStage(models.Model):
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    event = models.CharField(max_length=150)
    class Meta:
        db_table = u'calendar_stage'

class Club(models.Model):
    name = models.CharField(max_length=150)
    email1 = models.CharField(max_length=150)
    email2 = models.CharField(max_length=150, blank=True)
    email3 = models.CharField(max_length=150, blank=True)
    phone1 = models.CharField(max_length=150)
    phone2 = models.CharField(max_length=150, blank=True)
    phone3 = models.CharField(max_length=150, blank=True)
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    address5 = models.CharField(max_length=150, blank=True)
    headinstructor = models.CharField(max_length=150)
    picfilename = models.CharField(max_length=150, blank=True)
    history = models.TextField()
    region = models.CharField(max_length=150)
    status = models.CharField(max_length=3, blank=True)
    assistantinstructor = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'club'

class ClubClass(models.Model):
    club = models.CharField(max_length=150)
    instructor = models.CharField(max_length=150)
    day = models.CharField(max_length=150)
    starttime = models.CharField(max_length=150)
    endtime = models.CharField(max_length=150)
    description1 = models.TextField()
    description2 = models.TextField()
    description3 = models.TextField()
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    address5 = models.CharField(max_length=150, blank=True)
    maplink = models.TextField()
    directions = models.TextField()
    style = models.CharField(max_length=150)
    class Meta:
        db_table = u'club_class'

class ClubClassStage(models.Model):
    club = models.CharField(max_length=150)
    instructor = models.CharField(max_length=150)
    day = models.CharField(max_length=150)
    starttime = models.CharField(max_length=150)
    endtime = models.CharField(max_length=150)
    description1 = models.TextField()
    description2 = models.TextField()
    description3 = models.TextField()
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    address5 = models.CharField(max_length=150, blank=True)
    maplink = models.TextField()
    directions = models.TextField()
    style = models.CharField(max_length=150)
    class Meta:
        db_table = u'club_class_stage'

class ClubStage(models.Model):
    name = models.CharField(max_length=150)
    email1 = models.CharField(max_length=150)
    email2 = models.CharField(max_length=150, blank=True)
    email3 = models.CharField(max_length=150, blank=True)
    phone1 = models.CharField(max_length=150)
    phone2 = models.CharField(max_length=150, blank=True)
    phone3 = models.CharField(max_length=150, blank=True)
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    address5 = models.CharField(max_length=150, blank=True)
    headinstructor = models.CharField(max_length=150)
    picfilename = models.CharField(max_length=150, blank=True)
    history = models.TextField()
    region = models.CharField(max_length=150)
    status = models.CharField(max_length=3, blank=True)
    assistantinstructor = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'club_stage'

class Grading(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    name = models.CharField(max_length=150)
    pattern = models.IntegerField()
    grade = models.CharField(max_length=12)
    released = models.CharField(max_length=12)
    class Meta:
        db_table = u'grading'

class IdTable(models.Model):
    id_table_id = models.IntegerField()
    table_name = models.CharField(max_length=765)
    next_id = models.IntegerField()
    quantity = models.IntegerField()
    class Meta:
        db_table = u'id_table'

class Instructor(models.Model):
    fullname = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    sex = models.CharField(max_length=3, blank=True)
    age = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=75)
    club = models.CharField(max_length=150)
    profile = models.TextField()
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    picfilename1 = models.CharField(max_length=150)
    picfilename2 = models.CharField(max_length=150, blank=True)
    picfilename3 = models.CharField(max_length=150, blank=True)
    picfilename4 = models.CharField(max_length=150, blank=True)
    picfilename5 = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'instructor'

class InstructorAnnouncement(models.Model):
    club = models.CharField(max_length=150)
    date = models.DateTimeField()
    announcement = models.CharField(max_length=300)
    live = models.CharField(max_length=12)
    class Meta:
        db_table = u'instructor_announcement'

class InstructorStage(models.Model):
    fullname = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    sex = models.CharField(max_length=3, blank=True)
    age = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=75)
    club = models.CharField(max_length=150)
    profile = models.TextField()
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    picfilename1 = models.CharField(max_length=150)
    picfilename2 = models.CharField(max_length=150, blank=True)
    picfilename3 = models.CharField(max_length=150, blank=True)
    picfilename4 = models.CharField(max_length=150, blank=True)
    picfilename5 = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'instructor_stage'

class Member(models.Model):
    fullname = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    nickname = models.CharField(max_length=150, blank=True)
    sex = models.CharField(max_length=3)
    age = models.IntegerField()
    yearstraining = models.IntegerField()
    hardstyle = models.CharField(max_length=3, blank=True)
    softstyle = models.CharField(max_length=3, blank=True)
    picfilename = models.CharField(max_length=150, blank=True)
    pattern = models.IntegerField(null=True, blank=True)
    martialachievements = models.TextField(blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    hobbies = models.TextField(blank=True)
    favouritefilm = models.TextField(blank=True)
    trainingexperience = models.TextField(blank=True)
    personalstatement = models.TextField(blank=True)
    link1 = models.CharField(max_length=150, blank=True)
    link2 = models.CharField(max_length=150, blank=True)
    link3 = models.CharField(max_length=150, blank=True)
    link4 = models.CharField(max_length=150, blank=True)
    club = models.CharField(max_length=150, blank=True)
    address1 = models.CharField(max_length=150, blank=True)
    address2 = models.CharField(max_length=150, blank=True)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    email1 = models.CharField(max_length=150, blank=True)
    email2 = models.CharField(max_length=150, blank=True)
    email3 = models.CharField(max_length=150, blank=True)
    phonehome = models.CharField(max_length=150, blank=True)
    phonework = models.CharField(max_length=150, blank=True)
    phonemob = models.CharField(max_length=150, blank=True)
    fax = models.CharField(max_length=150, blank=True)
    lastgradingdate = models.DateTimeField(null=True, blank=True)
    passgradingflag = models.CharField(max_length=12, blank=True)
    gradingemailsent = models.CharField(max_length=12, blank=True)
    gradedpattern = models.IntegerField()
    class Meta:
        db_table = u'member'

class MemberStage(models.Model):
    fullname = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    nickname = models.CharField(max_length=150, blank=True)
    sex = models.CharField(max_length=3)
    age = models.IntegerField()
    yearstraining = models.IntegerField()
    hardstyle = models.CharField(max_length=3, blank=True)
    softstyle = models.CharField(max_length=3, blank=True)
    picfilename = models.CharField(max_length=150, blank=True)
    pattern = models.IntegerField(null=True, blank=True)
    martialachievements = models.TextField(blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    hobbies = models.TextField(blank=True)
    favouritefilm = models.TextField(blank=True)
    trainingexperience = models.TextField(blank=True)
    personalstatement = models.TextField(blank=True)
    link1 = models.CharField(max_length=150, blank=True)
    link2 = models.CharField(max_length=150, blank=True)
    link3 = models.CharField(max_length=150, blank=True)
    link4 = models.CharField(max_length=150, blank=True)
    club = models.CharField(max_length=150, blank=True)
    address1 = models.CharField(max_length=150, blank=True)
    address2 = models.CharField(max_length=150, blank=True)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    email1 = models.CharField(max_length=150, blank=True)
    email2 = models.CharField(max_length=150, blank=True)
    email3 = models.CharField(max_length=150, blank=True)
    phonehome = models.CharField(max_length=150, blank=True)
    phonework = models.CharField(max_length=150, blank=True)
    phonemob = models.CharField(max_length=150, blank=True)
    fax = models.CharField(max_length=150, blank=True)
    lastgradingdate = models.DateTimeField(null=True, blank=True)
    passgradingflag = models.CharField(max_length=12, blank=True)
    gradingemailsent = models.CharField(max_length=12, blank=True)
    stagelevel = models.IntegerField()
    gradedpattern = models.IntegerField()
    originalname = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'member_stage'

class Pattern(models.Model):
    number = models.IntegerField()
    english = models.CharField(max_length=150)
    pinyin = models.CharField(max_length=150)
    class Meta:
        db_table = u'pattern'

class StaticData(models.Model):
    chapter1 = models.CharField(max_length=150)
    chapter2 = models.CharField(max_length=150)
    chapter3 = models.CharField(max_length=600, blank=True)
    class Meta:
        db_table = u'static_data'

