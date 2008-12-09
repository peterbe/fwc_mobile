# python
import unittest
from datetime import datetime, timedelta, date
from pprint import pprint

# django
from django.test.client import Client
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.utils.html import escape

# project
from mobile.models import *
from mobile.views import club_page


class ViewsTestCase(unittest.TestCase):
    """
    Test the views
    """
    
    def test_club_page(self):
        """ test rendering the club page """
        cache.delete('club_page_classes')
        
        # create a club first
        dave = Instructor.objects.create(full_name=u'Dave Courtney Jones',
                                         first_name=u'Dave',
                                         last_name=u'Courtney Jones')
        
        city = Club.objects.create(head_instructor=dave,
                                   name=u'City & Islington',
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
        
        # add another club and it shouldn't be there for this club
        eddie = Instructor.objects.create(full_name=u'Eddie Walsh',
                                         first_name=u'Eddie',
                                         last_name=u'Walsh')
                                         
        ireland = Club.objects.create(head_instructor=dave,
                                   name=u'FWC Ireland',
                                   )
        
        class1 = ClubClass.objects.create(club=city, 
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
        
        
        
        
                                   
                        
