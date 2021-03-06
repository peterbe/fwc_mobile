# python
#import unittest
from datetime import datetime, timedelta, date
from pprint import pprint

# django
from django.test.client import Client
from django.test import TestCase
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.utils.html import escape

# project
from mobile.models import *
from mobile.views import club_page


class ViewsTestCase(TestCase):
    """
    Test the views
    """
    
                
    def test_club_page(self):
        """ test rendering the club page """
                       
        dave = Instructor.objects.create(full_name=u'Dave Courtney Jones',
                                         first_name=u'Dave',
                                         last_name=u'Courtney Jones')
        
        city = Club.objects.create(head_instructor=dave,
                                   name=u'FWC City & Islington',
                                   )
                                   
        # and some classes
        class1 = ClubClass.objects.create(club=city, 
                           day=datetime.now().strftime('%A'),
                           start_time='18:00', end_time='19:00',
                           description1='Kung Fu',
                           address1='Clarmont Hall',
                           address2='White Lion Street',
                           style='Kung fu')
        
        client = Client()
        club_url = city.get_absolute_url()
        response = client.get(club_url)
        assert response.status_code==200
        instructor_url = dave.get_absolute_url()
        assert response.content.count(escape(instructor_url))
        class_day_url = class1.get_absolute_url(without_time=True)
        assert response.content.count(escape(class_day_url))
        assert not response.content.count('Sparring') 
        
        
        # If you add a new class and re-render the club page for
        # this club a cache will still only show the one class
        class2 = ClubClass.objects.create(club=city, 
                           day=datetime.now().strftime('%A'),
                           start_time='19:00', end_time='20:00',
                           address1='Clarmont Hall',
                           address2='White Lion Street',
                           style='Sparring')

        response = client.get(club_url)
        assert response.status_code==200
        instructor_url = dave.get_absolute_url()
        assert response.content.count(escape(instructor_url))
        class_day_url = class1.get_absolute_url(without_time=True)
        assert response.content.count(escape(class_day_url))
        
        #print response.content
        # The newly added 'Sparring' class shouldn't be there yet
        # because the page is cached
        assert response.content.find('Sparring') == -1
        
        # add another club and it shouldn't be there for this club
        eddie = Instructor.objects.create(full_name=u'Eddie Walsh',
                                         first_name=u'Eddie',
                                         last_name=u'Walsh')
                                         
        ireland = Club.objects.create(head_instructor=dave,
                                   name=u'FWC Ireland',
                                   )
        
        ireland_class1 = ClubClass.objects.create(club=ireland,
                           day=datetime.now().strftime('%A'),
                           start_time='18:00', end_time='19:00',
                           address1='Elsewhere',
                           address2='Street 2',
                           style='Sparring')
        
        response = client.get(club_url)
        assert response.status_code==200
        
        assert not response.content.count('Eddie')
        assert not response.content.count('Ireland')
        assert not response.content.count('Elsewhere')
        
        
##    def test_feeds(self):
##        """ test publishing the feeds """
##        dave = Instructor.objects.create(full_name=u'Dave Courtney Jones',
##                                         first_name=u'Dave',
##                                         last_name=u'Courtney Jones')
##        
##        city = Club.objects.create(head_instructor=dave,
##                                   name=u'FWC City & Islington',
##                                   )
##                                   
##        # and some classes
##        class1 = ClubClass.objects.create(club=city, 
##                                          day=datetime.now().strftime('%A'),
##                                          start_time='18:00', end_time='19:00',
##                                          description1='Kung Fu',
##                                          address1='Clarmont Hall',
##                                          address2='White Lion Street',
##                                          address3='London',
##                                          address4='N1 9PD',
##                                          style='Kung fu')
##
##        client = Client()
##        res = client.get('/feeds/all-clubs/')
##        assert res.status_code == 200, res.status_code
##        #print res.content.replace('><','>\n<')

    def test_geo_feeds(self):
        """ test publishing the geo feeds """
        dave = Instructor.objects.create(full_name=u'Dave Courtney Jones',
                                         first_name=u'Dave',
                                         last_name=u'Courtney Jones')
        
        assert Club.objects.all().count() == 0
        city = Club.objects.create(head_instructor=dave,
                                   name=u'FWC City & Islington',
                                   )
        
        assert ClubClass.objects.filter(club=city).count() == 0
                                   
        # and some classes
        class1 = ClubClass.objects.create(club=city,
                                          day='Monday',
                                          start_time='18:00', end_time='19:00',
                                          description1='Kung Fu',
                                          address1='Clarmont Halll',
                                          address2='White Lion Street',
                                          address3='London',
                                          address4='N1 9PD',
                                          style='Kung fu')
        class2 = ClubClass.objects.create(club=city, 
                                          day='Monday',
                                          start_time='19:00', end_time='20:00',
                                          description1='Suang Yang',
                                          address1='Clarmont Halll',
                                          address2='White Lion Street',
                                          address3='London',
                                          address4='N1 9PD',
                                          style='Sparring')
        
        class3 = ClubClass.objects.create(club=city, 
                                          day='Friday',
                                          start_time='18:00', end_time='19:00',
                                          description1='Patterns',
                                          address1='Studio 1',
                                          address2='Saddlers Sports Centre',
                                          address3='122 Goswell Road',
                                          address4='London',
                                          address5='',
                                          style='Patterns')

        client = Client()
        res = client.get('/feeds/all-classes/')
        assert res.status_code == 200, res.status_code
        print res.content.replace('><','>\n<')
        
        assert '<georss:point>-0.083693 51.529435</georss:point>' in res.content
        
        
    def test_icalendar(self):
        """test icalendar() """
        
        yyyy = datetime.today().year
        Calendar.objects.create(event='Crete',
                                start_date=datetime(yyyy, 12, 30),
                                end_date=datetime(yyyy, 12, 31))
        
        Calendar.objects.create(event='KF Camp',
                                start_date=datetime(yyyy, 12, 29),
                                end_date=datetime(yyyy, 12, 29))
        
        # add an even that happened yesterday
        yesterday = datetime.today() - timedelta(days=1)
        Calendar.objects.create(event='Dinner',
                                start_date=yesterday,
                                end_date=yesterday)

        client = Client()
        res = client.get('/icalendar.ics')
        print res.content
        
        assert '%s1229' % yyyy in res.content
        assert '%s1231' % yyyy in res.content
        assert 'Crete' in res.content
        assert 'KF Camp' in res.content
        
        # order is so that youngest first
        assert res.content.find('KF Camp') < res.content.find('Crete')
        
        assert 'Dinner' not in res.content # because it's too old
        

        


                        
