# http://www.peterbe.com/plog/nasty-surprise-of-django-cache#c081210hpm1
# By using locmem instead of whatever is in settings we can be certain that 
# the cache is reset when the test run because when you start the testrunner
# you're starting a new python process and that's how locmem cache is reset
from django.conf import settings
settings.CACHE_BACKEND = 'locmem:///'

from test_views import ViewsTestCase