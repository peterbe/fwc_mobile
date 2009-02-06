from django.conf.urls.defaults import *

from feeds import AllClubsFeed, AllClubClassesFeed
#feeds = {
#         'all-clubs': AllClubsFeed,
#         'all-classes': AllClubClassesFeed,
#         }
from feeds import club_classes_geo_feed

urlpatterns = patterns('',

    (r'^instructor/(?P<fullname>[\w \-\+]+)/$',
     'fwc_mobile.mobile.views.instructor_page'),

    (r'^club/(?P<clubname>[\w \-&\(\)\+,]+)/$',
     'fwc_mobile.mobile.views.club_page'),
     
    (r'^club/(?P<clubname>[\w \-&\(\)\+,]+)/(?P<day>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)/$',
     'fwc_mobile.mobile.views.club_class_day_page'),     

    (r'^clubs/$',
     'fwc_mobile.mobile.views.clubs_page'),

    (r'^calendar/(?P<calendar_year>\d{4})/$',
     'fwc_mobile.mobile.views.calendar_page'),

    (r'^calendar/$',
     'fwc_mobile.mobile.views.calendar_page'),
     
    (r'^search/$',
     'fwc_mobile.mobile.views.search_page'),
     
    (r'^/?$',
     'fwc_mobile.mobile.views.home_page'),
     
    (r'^p/$',
     'fwc_mobile.mobile.views.home_page', dict(template_file='home2.html')),
     
    (r'^paginated/$',
     'fwc_mobile.mobile.views.home_page', dict(template_file='home2.html')),
                       
    #(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    #  {'feed_dict': feeds}),
    (r'^feeds/all-classes/', club_classes_geo_feed),
                       
    (r'map/all-classes/', 'fwc_mobile.mobile.views.all_classes_map'),
                       
)