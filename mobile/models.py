# python
from datetime import datetime

# django
from django.db import models



class Calendar(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event = models.CharField(max_length=150)
    class Meta:
        db_table = u'calendar'
        
    def one_day(self):
        return self.start_date.strftime('%Y%m%d') == self.end_date.strftime('%Y%m%d')

#class CalendarStage(models.Model):
#    calendar = models.ForeignKey(Calendar, null=True, blank=True)
#    start_date = models.DateTimeField()
#    end_date = models.DateTimeField()
#    event = models.CharField(max_length=150)
#    class Meta:
#        db_table = u'calendar_stage'

class Instructor(models.Model):
    full_name = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    sex = models.CharField(max_length=3, blank=True)
    age = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=75)
    profile = models.CharField(max_length=21000)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    pic_filename1 = models.CharField(max_length=150, blank=True)
    pic_filename2 = models.CharField(max_length=150, blank=True)
    pic_filename3 = models.CharField(max_length=150, blank=True)
    pic_filename4 = models.CharField(max_length=150, blank=True)
    pic_filename5 = models.CharField(max_length=150, blank=True)
    qualifications = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'instructor'

    def get_absolute_url(self):
        return "/instructor/%s" % self.full_name.replace(' ','+')
    
    def __unicode__(self):
        return self.full_name


class Club(models.Model):
    head_instructor = models.ForeignKey(Instructor, null=True, blank=True, related_name='head_instructor')
    assistant_instructor = models.ForeignKey(Instructor, null=True, blank=True, related_name='assistant_instructor')
    name = models.CharField(unique=True, max_length=150)
    description = models.CharField(max_length=600, blank=True)
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
    pic_filename = models.CharField(max_length=150, blank=True)
    history = models.CharField(max_length=3000)
    region = models.CharField(max_length=150)
    status = models.CharField(max_length=3, blank=True)
    class Meta:
        db_table = u'club'
        
    def __repr__(self):
        return '<Club: %r>' % self.name
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        name = self.name.replace(' ','+')
        return '/club/%s/' % name
        
        
class ClubAnnouncement(models.Model):
    club = models.ForeignKey(Club)
    date = models.DateTimeField()
    announcement = models.CharField(max_length=300)
    live = models.CharField(max_length=12, blank=True)
    class Meta:
        db_table = u'club_announcement'

class ClubClass(models.Model):
    club = models.ForeignKey(Club)
    day = models.CharField(max_length=150)
    start_time = models.CharField(max_length=150)
    end_time = models.CharField(max_length=150)
    description1 = models.CharField(max_length=3000)
    description2 = models.CharField(max_length=3000)
    description3 = models.CharField(max_length=3000)
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    address5 = models.CharField(max_length=150, blank=True)
    map_link = models.CharField(max_length=3000)
    directions = models.CharField(max_length=3000)
    style = models.CharField(max_length=150)
    class Meta:
        db_table = u'club_class'

    def get_absolute_url(self, without_time=False):
        url = '/club/%s/%s/' % (self.club.name.replace(' ','+'), self.day)
        if not without_time:
            url += '%s/%s/' % (self.start_time, self.end_time)
        return url
    
    def __unicode__(self):
        return "%s: %s (%s-%s) %s" % \
          (self.club, self.day, self.start_time, self.end_time, self.address2)

    def too_late_today(self):
        
        _hour_start, _min_start = [int(x) for x in self.start_time.split(':')]
        _hour_end, _min_end = [int(x) for x in self.end_time.split(':')]
        _hour = (_hour_start + _hour_end) / 2.0
        _min = (_min_start and _min_start or 60 + _min_end and _min_end or 60) / 2.0
        
        _hour_today, _min_today = [int(x) for x in datetime.now().strftime('%H:%M').split(':')]
        
        if _hour_today > _hour:
            return True
        elif _hour_today == _hour and _min_today > _min:
            return True
        
        return False
        
        

class ClubInstructor(models.Model):
    club = models.ForeignKey(Club)
    instructor = models.ForeignKey(Instructor)
    class Meta:
        db_table = u'club_instructor'

class ClubKeyword(models.Model):
    club = models.ForeignKey(Club)
    keyword = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'club_keyword'





class IdTable(models.Model):
    id_table_id = models.IntegerField(primary_key=True, db_column='ID_TABLE_ID') # Field name made lowercase.
    table_name = models.TextField(unique=True, max_length=765, db_column='TABLE_NAME') # Field name made lowercase.
    next_id = models.IntegerField(db_column='NEXT_ID') # Field name made lowercase.
    quantity = models.IntegerField(db_column='QUANTITY') # Field name made lowercase.
    class Meta:
        db_table = u'id_table'

    
class Article(models.Model):
    headline = models.CharField(max_length=300)
    summary = models.CharField(max_length=3000)
    type = models.CharField(max_length=150)
    content = models.TextField()#models.CharField(max_length=150000)
    author = models.CharField(max_length=300)
    instructor = models.ForeignKey(Instructor)
    date = models.DateTimeField()
    class Meta:
        db_table = u'article'

#class ArticleStage(models.Model):
#    article = models.ForeignKey(Article, null=True, blank=True)
#    headline = models.CharField(max_length=300)
#    summary = models.CharField(max_length=3000)
#    type = models.CharField(max_length=150)
#    content = models.CharField(max_length=150000)
#    author = models.CharField(max_length=300)
#    instructor = models.ForeignKey(Instructor)
#    date = models.DateTimeField()
#    class Meta:
#        db_table = u'article_stage'

    
        
#class InstructorAnnouncement(models.Model):
#    club = models.CharField(max_length=150, db_column='Club', primary_key=True) # Field name made lowercase.
#    date = models.DateTimeField(db_column='Date') # Field name made lowercase.
#    announcement = models.CharField(max_length=300, db_column='Announcement') # Field name made lowercase.
#    live = models.CharField(max_length=12, db_column='Live') # Field name made lowercase.
#    class Meta:
#        db_table = u'instructor_announcement'

#class InstructorStage(models.Model):
#    id = models.IntegerField(primary_key=True)
#    instructor = models.ForeignKey(Instructor, null=True, blank=True)
#    member = models.ForeignKey(Member, null=True, blank=True)
#    full_name = models.CharField(max_length=150)
#    first_name = models.CharField(max_length=150)
#    last_name = models.CharField(max_length=150)
#    sex = models.CharField(max_length=3, blank=True)
#    age = models.IntegerField(null=True, blank=True)
#    type = models.CharField(max_length=75)
#    profile = models.CharField(max_length=21000)
#    email = models.CharField(max_length=150)
#    phone = models.CharField(max_length=150)
#    pic_filename1 = models.CharField(max_length=150)
#    pic_filename2 = models.CharField(max_length=150, blank=True)
#    pic_filename3 = models.CharField(max_length=150, blank=True)
#    pic_filename4 = models.CharField(max_length=150, blank=True)
#    pic_filename5 = models.CharField(max_length=150, blank=True)
#    qualifications = models.CharField(max_length=300, blank=True)
#    class Meta:
#        db_table = u'instructor_stage'

class Member(models.Model):
    full_name = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    nickname = models.CharField(max_length=150, blank=True)
    sex = models.CharField(max_length=3)
    age = models.IntegerField()
    years_training = models.IntegerField()
    hard_style = models.CharField(max_length=3, blank=True)
    soft_style = models.CharField(max_length=3, blank=True)
    pic_filename = models.CharField(max_length=150, blank=True)
    martial_achievements = models.CharField(max_length=9000, blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    hobbies = models.CharField(max_length=9000, blank=True)
    favourite_film = models.CharField(max_length=9000, blank=True)
    training_experience = models.CharField(max_length=9000, blank=True)
    personal_statement = models.CharField(max_length=9000, blank=True)
    link1 = models.CharField(max_length=150, blank=True)
    link2 = models.CharField(max_length=150, blank=True)
    link3 = models.CharField(max_length=150, blank=True)
    link4 = models.CharField(max_length=150, blank=True)
    club = models.ForeignKey(Club, null=True, blank=True)
    address1 = models.CharField(max_length=150, blank=True)
    address2 = models.CharField(max_length=150, blank=True)
    address3 = models.CharField(max_length=150, blank=True)
    address4 = models.CharField(max_length=150, blank=True)
    email1 = models.CharField(max_length=150, blank=True)
    email2 = models.CharField(max_length=150, blank=True)
    email3 = models.CharField(max_length=150, blank=True)
    phone_home = models.CharField(max_length=150, blank=True)
    phone_work = models.CharField(max_length=150, blank=True)
    phone_mob = models.CharField(max_length=150, blank=True)
    fax = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'member'



#class MemberEx(models.Model):
#    id = models.IntegerField(primary_key=True)
#    first_name = models.CharField(max_length=150)
#    last_name = models.CharField(max_length=150)
#    sex = models.CharField(max_length=3)
#    age = models.IntegerField()
#    years_training = models.IntegerField(null=True, blank=True)
#    hard_style = models.CharField(max_length=3, blank=True)
#    soft_style = models.CharField(max_length=3, blank=True)
#    pic_filename = models.CharField(max_length=150, blank=True)
#    club = models.CharField(max_length=150, blank=True)
#    email1 = models.CharField(max_length=150, blank=True)
#    email2 = models.CharField(max_length=150, blank=True)
#    email3 = models.CharField(max_length=150, blank=True)
#    phone_home = models.CharField(max_length=150, blank=True)
#    phone_mob = models.CharField(max_length=150, blank=True)
#    class Meta:
#        db_table = u'member_ex'
#
#class MemberStage(models.Model):
#    id = models.IntegerField(primary_key=True)
#    member = models.ForeignKey(Member, null=True, blank=True)
#    full_name = models.CharField(unique=True, max_length=150)
#    first_name = models.CharField(max_length=150)
#    last_name = models.CharField(max_length=150)
#    nickname = models.CharField(max_length=150, blank=True)
#    sex = models.CharField(max_length=3)
#    age = models.IntegerField()
#    years_training = models.IntegerField()
#    hard_style = models.CharField(max_length=3, blank=True)
#    soft_style = models.CharField(max_length=3, blank=True)
#    pic_filename = models.CharField(max_length=150, blank=True)
#    martial_achievements = models.CharField(max_length=9000, blank=True)
#    occupation = models.CharField(max_length=150, blank=True)
#    hobbies = models.CharField(max_length=9000, blank=True)
#    favourite_film = models.CharField(max_length=9000, blank=True)
#    training_experience = models.CharField(max_length=9000, blank=True)
#    personal_statement = models.CharField(max_length=9000, blank=True)
#    link1 = models.CharField(max_length=150, blank=True)
#    link2 = models.CharField(max_length=150, blank=True)
#    link3 = models.CharField(max_length=150, blank=True)
#    link4 = models.CharField(max_length=150, blank=True)
#    club = models.ForeignKey(Club, null=True, blank=True)
#    address1 = models.CharField(max_length=150, blank=True)
#    address2 = models.CharField(max_length=150, blank=True)
#    address3 = models.CharField(max_length=150, blank=True)
#    address4 = models.CharField(max_length=150, blank=True)
#    email1 = models.CharField(max_length=150, blank=True)
#    email2 = models.CharField(max_length=150, blank=True)
#    email3 = models.CharField(max_length=150, blank=True)
#    phone_home = models.CharField(max_length=150, blank=True)
#    phone_work = models.CharField(max_length=150, blank=True)
#    phone_mob = models.CharField(max_length=150, blank=True)
#    fax = models.CharField(max_length=150, blank=True)
#    class Meta:
#        db_table = u'member_stage'
#


class Pattern(models.Model):
    number = models.IntegerField()
    english = models.CharField(max_length=150)
    pinyin = models.CharField(max_length=150)
    style = models.CharField(max_length=60)
    class Meta:
        db_table = u'pattern'

class StaticData(models.Model):
    chapter1 = models.CharField(unique=True, max_length=150)
    chapter2 = models.CharField(unique=True, max_length=150)
    chapter3 = models.TextField(unique=True, blank=True)
    class Meta:
        db_table = u'static_data'

