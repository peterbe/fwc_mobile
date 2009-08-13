# python
import re
import urllib
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
from ukpostcode import valid_uk_postcode, format_uk_postcode
from geo import AddressNotFound, geopy_geocode, geopy_geocode_yahoo

## Constants ###################################################################

if DEBUG:
    CACHE_TIMEOUT = 60 # seconds (60*60 = 1 hour, 60*60*24 = 1 day)
else:
    CACHE_TIMEOUT = 60 * 60 * 24 # seconds (60*60 = 1 hour, 60*60*24 = 1 day)


ONE_HOUR = 60 * 60
ONE_DAY = ONE_HOUR * 24
ONE_WEEK = ONE_DAY * 7
ONE_MONTH = ONE_WEEK * 4

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
        key = "%s %s %s" % (klass.day, klass.address1, klass.address2)
        if key in _class_days:
            _class_days[key].append(klass)
        else:
            _class_days[key] = [klass]
            
    def manual_sort(item1, item2):
        i1 = _weekdays.index(item1[0].split()[0])
        i2 = _weekdays.index(item2[0].split()[0])
        return cmp(i1, i2)
    
    return [{'day':k.split()[0],
             'classes':v, 
             'venue':v[0].address2,
             'day_url': '%s%s/' % (v[0].get_absolute_url(without_time=True), v[0].id)
                                   }
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
            block['classes_today_url'] = classes[0].get_absolute_url(without_time=True)\
              + '%s/' % classes[0].id
            tonight_or_today = u'tonight'
            H,M = [int(x) for x in classes[0].start_time.split(':')]
            if H < 12:
                tonight_or_today = u'today'
            block['tonight_or_today'] = tonight_or_today
        blocks.append(block)
    classes_today = blocks
    return locals()
    
@cache_page(60 * 60 * 12) # 12 hours
def club_class_day_page(request, clubname, day, classid=None):
    club = _find_club(clubname)
    if club is None:
        raise Http404('Could not find the club')
    
    if classid:
        try:
            class_ = ClubClass.objects.get(pk=classid)
        except ClubClass.DoesNotExist:
            # probably a deleted class
            raise Http404("Class by that ID does not exist")
        classes = ClubClass.objects.filter(club=class_.club,
                                           day=class_.day,
                                           address1=class_.address1,
                                           address2=class_.address2)
        
    else:
        # The desperate way of doing it
        classes = ClubClass.objects.filter(club=club, day__iexact=day).order_by('start_time')
            
    try:
        first_class = classes[0]
        instructor = Instructor.objects.get(pk=first_class.club.head_instructor.id)
        address1 = first_class.address1
        address2 = first_class.address2
        address3 = first_class.address3
        address4 = first_class.address4
        address5 = first_class.address5
        
        if valid_uk_postcode(address5.strip()):
            post_code = format_uk_postcode(address5.strip())
        elif address4 == 'Sweden':
            # Gabor
            post_code = "%s, %s" % (address3, address4)
        elif address5 == 'Ireland' or address3.startswith('Dublin'):
            post_code = "%s, %s, Ireland" % (address2, address3)
        elif valid_uk_postcode(address4.strip()): # eg. FWC Kensington & Chelsea
            post_code = format_uk_postcode(address4.strip())
        else:
            post_code = None
            print repr(address1)
            print repr(address2)
            print repr(address3)
            print repr(address4)
            print repr(address5)
            
        if post_code:
            map_link = "%smap/?" % request.build_absolute_uri()
            #print repr(post_code)
            map_link += urllib.urlencode(dict(q=post_code))
        else:
            map_link = first_class.map_link
        
    except IndexError:
        # if this happens, there are no classes on this day and that can happen
        # if you go to a day that no longer exists (stale URL).
        first_class = None
        
        

    return _render('club_class_day.html', locals(), request)
    

@cache_page(60 * 60 * 12) # 12 hours
def club_class_day_map_page(request, clubname, day, classid=None):
    club = _find_club(clubname)
    if club is None:
        raise Http404('Could not find the club')
    
    if classid:
        try:
            class_ = ClubClass.objects.get(pk=classid)
        except ClubClass.DoesNotExist:
            # probably a deleted class
            raise Http404("Class by that ID does not exist")
        classes = ClubClass.objects.filter(club=class_.club,
                                           day=class_.day,
                                           address1=class_.address1,
                                           address2=class_.address2)
        
    else:
        # The desperate way of doing it
        classes = ClubClass.objects.filter(club=club, day__iexact=day).order_by('start_time')
        
    try:
        first_class = classes[0]
    except IndexError:
        first_class = None
        
    if not request.GET.get('q'):
        if first_class:
            return HttpResponseRedirect(first_class.get_absolute_url())
        else:
            return HttpResponseRedirect('/')
        
    q = request.GET['q']
    cache_key = 'marker_search_%s' % q.replace(' ','').lower()
    marker_info = cache.get(cache_key)
    if marker_info is None:
        marker_info = _get_markers_by_search(q)
        cache.set(cache_key, marker_info, ONE_MONTH)
        
    marker, (lat, lng) = marker_info
                  
    size = _get_map_size(request)
    zoom = int(request.GET.get('zoom', 15))
    query_args = dict(markers=marker, size=size, maptype='mobile', 
                      key=settings.GOOGLEMAPS_API_KEY,
                      sensor='false',
                      center='%s,%s' % (lat, lng),
                      zoom=zoom,
                     )
    google_maps_url = 'http://maps.google.com/staticmap?' + urllib.urlencode(query_args)
    
    if zoom < 19:
        zoom_in_url = '?' + urllib.urlencode(dict(q=q, zoom=zoom+2))
    if zoom > 11:
        zoom_out_url = '?' + urllib.urlencode(dict(q=q, zoom=zoom-2))

    return _render('club_class_day_map.html', locals(), request)

def _get_map_size(request):
    rc = RequestContext(request)
    #print rc.get('iphone_version')
    
    return '300x300'

def _get_markers_by_search(q):
    marker = ''
    try:
        #q=q.replace(' ','').strip()
        #print "IN", repr(q)
        #place, (lat, lng) = geopy_geocode(q)
        #print "OUT", place, (lat, lng)
        place, (lat, lng) = geopy_geocode_yahoo(q)
        #print "OUT", place, (lat, lng)
    except ValueError, msg:
        raise AddressNotFound, address_search
    marker = '%s,%s,green' % (lat, lng)
    return marker, (lat, lng)



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


@cache_page(60 * 60 * 0) # 1 hour
def icalendar(request):
    from icalendar import Calendar as iCalendar
    from icalendar import Event
    from datetime import datetime, date
    from icalendar import UTC # timezone
    cal = iCalendar()
    cal.add('prodid', '-//FWC Kung Fu Calendar //m.fwckungfu.com')
    cal.add('version', '2.4')
    cal.add('x-wr-calname', 'FWC Kung Fu Calendar')
    
    yyyy = datetime.today().year
    #filter_ = dict(start_date__year=yyyy, start_date__gte=datetime.today())
    filter_ = dict()
    all_datestrings = set()
    for entry in Calendar.objects.filter(**filter_).order_by('start_date'):
        event = Event()
        #print entry.start_date, entry.event
        event.add('summary', entry.event)
        st = entry.start_date
        event.add('dtstart', date(st.year, st.month, st.day))
        all_datestrings.add(st.strftime('%Y%m%d'))
        #event.add('dtstart', datetime(st.year, st.month, st.day, 0, 0, 0, tzinfo=UTC))
        et = entry.end_date
        event.add('dtend', date(et.year, et.month, et.day))
        all_datestrings.add(et.strftime('%Y%m%d'))
        #event.add('dtend', datetime(et.year, et.month, et.day,0,0,0,tzinfo=UTC))
        #event.add('dtend', 'TZID=UTC;VALUE=DATE:' + et.strftime('%Y%m%d')) # DOESNOT WORK!
                  
        event.add('dtstamp', datetime(st.year, st.month, st.day, 0, 0, 0, tzinfo=UTC))
        event['uid'] = 'fwccalendar2.4-%s' % entry.id
        cal.add_component(event)

    as_string = cal.as_string()
    for datestring in all_datestrings:
        
        as_string = as_string.replace(':%s' % datestring, 
                                      ';TZID=UTC;VALUE=DATE:%s' % datestring)
        
    as_string = as_string.replace("\r","")
    response = HttpResponse(as_string, mimetype='text/calendar')
    response['Content-Disposition']='attachment; filename="%s"' % 'calendar.ics'
    return response
    #return HttpResponse(as_string, content_type='text/calendar;charset=utf-8')
    #return HttpResponse(as_string, content_type='text/plain')