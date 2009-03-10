# python
import re
from pprint import pprint
from datetime import datetime, timedelta

# djano
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings
from django.views.decorators.cache import cache_page, never_cache
from django.core.cache import cache
from django.contrib.sites.models import RequestSite

# app
from mobile.models import Club, ClubClass, Instructor, ClubAnnouncement,\
 Calendar
from settings import DEBUG 
 
## Constants ###################################################################

if DEBUG:
    CACHE_TIMEOUT = 60 # seconds (60*60 = 1 hour, 60*60*24 = 1 day)
else:
    CACHE_TIMEOUT = 60 * 60 * 24 # seconds (60*60 = 1 hour, 60*60*24 = 1 day)



## Utility functions ###########################################################

def _poor_mans_wordelimiter(word):
    return '%s | %s| %s ' % (re.escape(word), re.escape(word), re.escape(word))


def _set_cookie(response, key, value, expire=None):
    # http://www.djangosnippets.org/snippets/40/
    if expire is None:
        max_age = 365*24*60*60  #one year
    else:
        max_age = expire
    if isinstance(value, unicode):
        value = value.encode('utf8')
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, 
        domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

def _render(template, data, request):
    return render_to_response(template, data, 
                              context_instance=RequestContext(request))

_weekdays = [u'Monday', u'Tuesday', u'Wednesday', u'Thursday', u'Friday', u'Saturday', u'Sunday']
def _find_club(name):
    """ return club model object or None """
    name = name.lower().strip()
    name = name.replace('_', ' ').replace('+',' ')
    name = re.sub('\s+',' ', name)
    club = None
    try:
        try:
            return Club.objects.get(name__iexact=name)
        except Club.DoesNotExist:
            if not name.startswith('fwc'):
                try:
                    return Club.objects.get(name__iexact='FWC '+name)
                except Club.DoesNotExist:
                    try:
                        return Club.objects.get(name__istartswith='FWC '+name)
                    except Club.DoesNotExist:
                        pass
            else:
                try:
                    club = Club.objects.get(name__istartswith=name)
                except Club.DoesNotExist:
                    pass
    except Club.MultipleObjectsReturned:
        pass
    
    _and_regex = re.compile(r'\b(and)\b|_(and)_', re.I)
    if _and_regex.findall(name):
        name = _and_regex.sub(' & ', name)
        return _find_club(name)
    
    return None

def clean_cache_key(key):
    return key.replace(' ','')

def cache_result(callable, cache_key, timeout=CACHE_TIMEOUT):
    def inner(*args, **kwargs):
       result = cache.get(clean_cache_key(cache_key))
       if result is None:
           result = callable(*args, **kwargs)
           cache.set(clean_cache_key(cache_key), result, timeout)
       return result
    return inner


## Actual views ################################################################


def _get_class_days(club, use_cache=True):
    if use_cache:
        cache_key = clean_cache_key('club_page_classes__%s' % club.name)
        classes = cache.get(cache_key)
        if classes is None:
            classes = ClubClass.objects.filter(club=club).order_by('start_time')
            cache.set(cache_key, classes, CACHE_TIMEOUT)
    else:
        classes = ClubClass.objects.filter(club=club).order_by('start_time')
    
    def manual_sort(class1, class2):
        i1 = _weekdays.index(class1.day)
        i2 = _weekdays.index(class2.day)
        r = cmp(i1, i2)
        if not r:
            return cmp(class1.start_time, class2.start_time)
        return r
    #classes = sorted(classes, manual_sort)
    
    # lump them by day
    _class_days = {}
    for klass in classes:
        if klass.day in _class_days:
            _class_days[klass.day].append(klass)
        else:
            _class_days[klass.day] = [klass]
            
    def manual_sort(item1, item2):
        i1 = _weekdays.index(item1[0])
        i2 = _weekdays.index(item2[0])
        return cmp(i1, i2)
    
    return [{'day':k, 'classes':v, 'venue':v[0].address2,
             'day_url':v[0].get_absolute_url(without_time=True)}
            for (k,v) in sorted(_class_days.items(), manual_sort)]
    

@never_cache
def club_page(request, clubname):
    club = _find_club(clubname)
    if club is None:
        raise Http404('Could not find the club')
    
    class_days = _get_class_days(club)
    
    instructor = Instructor.objects.get(pk=club.head_instructor.id)
    assistant_instructor = None
    if club.assistant_instructor:
        assistant_instructor = Instructor.objects.get(
                                      pk=club.assistant_instructor.id)

    only_since = datetime.now() - timedelta(days=30)
    announcements = ClubAnnouncement.objects.filter(
                                   date__gte=only_since, club=club,
                                   # LIVE=True???
                                   )

    data = locals()
    data.update(_classes_today(club))

    response = _render('club_page.html', data, request)
    _set_cookie(response, 'last_visited_club', club.name, expire=100*24*60*60)
    
    return response


def _classes_today(club):
    """ return a tuple of 'classes_today', 'tonight_or_today' """
    cache_key = clean_cache_key('club_page_classes__%s_%s' %\
      (club.name, datetime.now().strftime('%A')))
    _all_classes_today = cache.get(cache_key)
    if _all_classes_today is None:
        _all_classes_today = ClubClass.objects.filter(club=club, 
                                             day=datetime.now().strftime('%A')
                                             ).order_by('address1','start_time')
        cache.set(cache_key, _all_classes_today, CACHE_TIMEOUT)
        
    # first split them up by address
    classes_today = {}
    
    for each in _all_classes_today:
        if each.address1 in classes_today:
            classes_today[each.address1].append(each)
        else:
            classes_today[each.address1] = [each]
        
    blocks = []
    for classes in classes_today.values():
        #print each.style, each.address1, each.start_time
        block = {'classes_today':classes}
        tonight_or_today = None
        if len(classes):
            block['classes_today_venue'] = classes[0].address2
            block['classes_today_url'] = classes[0].get_absolute_url(without_time=True)
            tonight_or_today = u'tonight'
            H,M = [int(x) for x in classes[0].start_time.split(':')]
            if H < 12:
                tonight_or_today = u'today'
            block['tonight_or_today'] = tonight_or_today
        blocks.append(block)
    #print "BLOCKS"
    #pprint(blocks)
    classes_today = blocks
    return locals()
    
@cache_page(60 * 60 * 12) # 12 hours
def club_class_day_page(request, clubname, day):
    club = _find_club(clubname)
    if club is None:
        raise Http404('Could not find the club')
    
    classes = ClubClass.objects.filter(club=club, day__iexact=day).order_by('start_time')
    try:
        first_class = classes[0]
        instructor = Instructor.objects.get(pk=first_class.club.head_instructor.id)
    except IndexError:
        # if this happens, there are no classes on this day and that can happen
        # if you go to a day that no longer exists (stale URL).
        #return HttpResponseRedirect(club.get_absolute_url())
        first_class = None
    
    
    
    return _render('club_class_day.html', locals(), request)
    

def _find_instructor(name):
    name = name.lower().strip()
    name = name.replace('_', ' ').replace('+',' ')
    name = re.sub('\s+',' ', name)
    instructor = None
    try:
        try:
            return Instructor.objects.get(full_name__iexact=name)
        except Instructor.DoesNotExist:
            try:
                return Instructor.objects.get(first_name__iexact=name)
            except Instructor.DoesNotExist:
                pass
            
    except Instructor.MultipleObjectsReturned:
        pass
    
    return None
            
    
@cache_page(60 * 60 * 24) # 24 hours
def instructor_page(request, fullname):
    instructor = _find_instructor(fullname)
    if instructor is None:
        raise Http404('Could not find the instructor')
    
    if instructor.phone:
        phone_formatted = instructor.phone.replace(' ','')
    
    clubs = Club.objects.filter(head_instructor=instructor)
    if not clubs:
        clubs = Club.objects.filter(assistant_instructor=instructor)
            
    if len(clubs) == 1:
        club = clubs[0]

    return _render('instructor.html', locals(), request)





@never_cache
def home_page(request, template_file='home.html'):
    clubs = cache.get('home_page_clubs')
    if clubs is None:
        clubs = Club.objects.all().order_by('name').select_related('head_instructor')
        cache.set('home_page_clubs', clubs, CACHE_TIMEOUT)
    
    data = locals()
    last_visited_club = request.COOKIES.get('last_visited_club', None)
    if last_visited_club:
        last_visited_club = _find_club(last_visited_club)
        if last_visited_club is not None:
            data['last_visited_club'] = last_visited_club
            data.update(_classes_today(last_visited_club))
            
    return _render(template_file, data, request)

@never_cache
def search_page(request):
    q = request.GET.get('q', u'')
    if len(q) == 1:
        # not allowed
        q = u''
        
    if q:
        # construct the search results
        searchresults = []
        qset = (
           Q(name__iexact=q) |
           Q(name__iregex=q) |
           Q(region__iexact=q) 
        )
        for club in Club.objects.filter(qset).distinct().select_related('head_instructor'):
            description = u"Head instructor %s" % club.head_instructor.full_name
            if club.assistant_instructor:
                description += ", Assistant instructor %s" % club.assistant_instructor.full_name
            if club.region:
                description += ". Region %s" % club.region
            searchresults.append(
              dict(title=club.name,
                   url=club.get_absolute_url(),
                   description=description,
                   type="Club",
                   )
            )

        qset = (
           Q(full_name__iexact=q) |
           Q(first_name__iexact=q) |
           Q(last_name__iexact=q) |
           Q(email__iexact=q)
        )
        for instructor in Instructor.objects.filter(qset).distinct():
            head_clubs = list(Club.objects.filter(head_instructor=instructor))
            assistant_clubs = list(Club.objects.filter(assistant_instructor=instructor))
            description = u""
            if head_clubs:
                description += u'Head instructor of %s.' % \
                  ', '.join(['<a href="%s">%s</a>' % (x.get_absolute_url(), x.name) for x in head_clubs])
            if assistant_clubs:
                description += u'Assistant instructor of %s.' % \
                  ', '.join(['<a href="%s">%s</a>' % (x.get_absolute_url(), x.name) for x in assistant_clubs])
                
            searchresults.append(
              dict(title=instructor.full_name,
                   url=instructor.get_absolute_url(),
                   description=description,
                   type=instructor.type,
                   )
            )            
            
        qset = (
           Q(address1__iexact=q) |
           Q(address2__iexact=q) |
           Q(address3__iexact=q) |
           Q(address4__iexact=q) |
           Q(style__iregex=q) |
           Q(day__iexact=q) 
        )
        for klass in ClubClass.objects.filter(qset).distinct().select_related():
            instructor = Instructor.objects.get(pk=klass.club.head_instructor.id)
            description = u'With club <a href="%s">%s</a> and instructor %s.' % \
              (klass.club.get_absolute_url(), klass.club.name, instructor.full_name)
            description += u"<br/>%s, %s, %s" % (klass.address1, klass.address2, klass.address3)
            title = u"%s %s - %s" % (klass.style, klass.start_time, klass.end_time)
            searchresults.append(
              dict(title=title,
                   url=klass.club.get_absolute_url()+'#'+klass.day,
                   type=u'Class',
                   description=description
                   )
            )
            
        count_results = len(searchresults)
            
    return _render('search.html', locals(), request)
        

                                                    

@cache_page(60 * 60 * 24) # 24 hours
def calendar_page(request, calendar_year=None):
    
    if calendar_year is not None:
        _filter = dict(start_date__year=int(calendar_year),
                       start_date__lte=datetime(int(calendar_year)+1,1,1))
        whole_year = True
        
    else:
        _filter = dict(end_date__gte=datetime.now())
        whole_year = False

        _first_year = int(Calendar.objects.all().order_by('start_date')[0].start_date.strftime('%Y'))
        _this_year = int(datetime.now().strftime('%Y'))
        whole_year_options = range(_first_year, _this_year + 1)
        
    events = Calendar.objects.filter(**_filter).order_by('start_date')
    
    eventmonths = []
    month_events = []
    month = None
    for event in events:
        if calendar_year is None:
            calendar_year = event.start_date.strftime('%Y')
            
        if month is None:
            month = event.start_date.strftime('%B')
            month_events.append(event)
        elif event.start_date.strftime('%B') != month:
            eventmonths.append(dict(month=month, events=month_events))
            month_events = [event]
            month = event.start_date.strftime('%B')
        else:
            month_events.append(event)
            
    if month_events:
        eventmonths.append(dict(month=month, events=month_events))
    
    return _render('calendar.html', locals(), request)


def all_classes_map(request):
    google_key = settings.GOOGLEMAPS_API_KEY
    current_site = RequestSite(request)
    geo_xml_url = 'http://%s/feeds/all-classes/' % current_site.domain
    return _render('geomap.html', locals(), request)


def icalendar(request):
    from icalendar import Calendar as iCalendar
    from icalendar import Event
    from datetime import datetime, date
    from icalendar import UTC # timezone
    cal = iCalendar()
    cal.add('prodid', '-//FWC Kung Fu Calendar //m.fwckungfu.com')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'FWC Kung Fu Calendar')
    
    yyyy = datetime.today().year
    filter_ = dict(start_date__year=yyyy, start_date__gte=datetime.today())
    for entry in Calendar.objects.filter(**filter_).order_by('start_date'):
        event = Event()
        #print entry.start_date, entry.event
        event.add('summary', entry.event)
        st = entry.start_date
        #event.add('dtstart', date(st.year, st.month, st.day))
        event.add('dtstart', datetime(st.year, st.month, st.day, 0, 0, 0, tzinfo=UTC))
        et = entry.end_date
        #event.add('dtend', date(et.year, et.month, et.day))
        event.add('dtend', datetime(et.year, et.month, et.day,0,0,0,tzinfo=UTC))
        event.add('dtstamp', datetime(st.year, st.month, st.day, 0,0,0,tzinfo=UTC))
        event['uid'] = 'fwccalendar-%s' % entry.id
        cal.add_component(event)
    
    
    
    return HttpResponse(cal.as_string(), content_type='text/calendar;charset=utf-8')