from pprint import pprint
from geopy import geocoders
from collections import defaultdict

from django.http import HttpResponse
from django.contrib.syndication.feeds import Feed
from django.contrib.gis.feeds import Feed as GeoFeed
from django.contrib.gis.feeds import GeoRSSFeed, GeoAtom1Feed
#from django.contrib.gis.geos.geometries import Point
from django.core.cache import cache
from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.views.decorators.cache import cache_page, never_cache

from models import Club, ClubClass, Instructor
from views import _get_class_days

from ukpostcode import valid_uk_postcode, format_uk_postcode


# If this is true it will only find those with UK postcodes
# This means that the searches are going to be much faster
FIND_ONLY_UK_POSTCODES = True

class AddressNotFound(Exception):
    pass

def geopy_geocode(address, google_key, domain='maps.google.co.uk', exactly_one=True):
    g = geocoders.Google(google_key, domain=domain)
    return g.geocode(address, exactly_one=exactly_one)


def _address_list_to_geopoint(address_bits):
    address_bits = [x.strip() for x in address_bits if x.strip()]
    cache_key = '|'.join([x.replace(' ','') for x in address_bits])
    in_cache = cache.get(cache_key)
    
    if in_cache is None:
        print cache_key, "not in cache"
        # first find out if one of the items is a UK postcode
        address_search = None
        for bit in address_bits:
            if valid_uk_postcode(bit):
                address_search = format_uk_postcode(bit)
                
        if not address_search:
            if FIND_ONLY_UK_POSTCODES:
                raise AddressNotFound, ','.join(address_bits)
            else:
                address_search = ', '.join(address_bits[2:])
            
        try:
            place, (lat, lng) = geopy_geocode(address_search, 
                                              settings.GOOGLEMAPS_API_KEY)
        except ValueError, msg:
            raise AddressNotFound, address_search
        
        in_cache = (lat, lng)
        # save it in cache
        cache.set(cache_key, in_cache, 3600*24) # 1 day, make it a month?
    else:
        print cache_key, "Cached!"
        
    return in_cache

class AllClubsFeed(Feed):
    title = "All FWC Kung fu clubs"
    link = "/"
    description = "Feed of all clubs"

    def items(self):
        return Club.objects.order_by('name')
    
    
class ClubDay(object):
    def __init__(self, club, absolute_url, address, title, description):
        self.club = club
        self.absolute_url = absolute_url
        self.address = address
        self.title = title
        self.description = description
        
    def title(self):
        return self.title
    
    def item_description(self, item):
        return self.description
    
    def get_absolute_url(self):
        return self.absolute_url
    
class AllClubClassesFeed(GeoFeed):
    title = "All FWC Kung fu classes"
    link = "/"
    description = "Feed of all classes"

    def item_geometry(self, obj):
        return _address_list_to_geopoint(obj.address)

    def item_description(self, item):
        return 'xxxxxxx'

    def items(self):
        
        def manual_sort(class1, class2):
            i1 = _weekdays.index(class1.day)
            i2 = _weekdays.index(class2.day)
            r = cmp(i1, i2)
            if not r:
                return cmp(class1.start_time, class2.start_time)
            return r
    
        for club in Club.objects.all():
            # lump the classes together per day
            class_days = _get_class_days(club, use_cache=False)
            for class_day in class_days:
                one_class = class_day['classes'][0]
                address = [one_class.address1,
                        one_class.address2,
                        one_class.address3,
                        one_class.address4,
                        one_class.address5,
                        ]
                address = [x for x in address if x]
                
                title = u'%s (%s)' % (club, class_day['day'])
                description = u'%s at %s ' % (club, class_day['venue'])
                
                clubday = ClubDay(club, class_day['day_url'], address,
                                  title=title,
                                  description=description)
                
                yield clubday
                
                
class AddedGeoRSSFeed(GeoRSSFeed):
    def rss_attributes(self):
        attrs = super(AddedGeoRSSFeed, self).rss_attributes()
        attrs[u'xmlns:geo'] = u'http://www.w3.org/2003/01/geo/wgs84_pos#'
        return attrs
    
    def add_item_elements(self, handler, item):
        super(AddedGeoRSSFeed, self).add_item_elements(handler, item)
        self.add_georss_element(handler, item, w3c_geo=True)
        
    def add_georss_point(self, handler, coords, w3c_geo=False):
        """
        Adds a GeoRSS point with the given coords using the given handler.
        Handles the differences between simple GeoRSS and the more pouplar
        W3C Geo specification.
        """
        if w3c_geo:
            lon, lat = coords[:2]
            handler.addQuickElement(u'geo:lat', u'%f' % lat)
            #handler.addQuickElement(u'geo:lon', u'%f' % lon)
            handler.addQuickElement(u'geo:long', u'%f' % lon)
        else:
            handler.addQuickElement(u'georss:point', self.georss_coords((coords,)))
            
class MyGeoAtom1Feed(GeoAtom1Feed):
    
    def root_attributes(self):
        attrs = super(MyGeoAtom1Feed, self).root_attributes()
        attrs[u'xmlns:georss'] = u'http://www.georss.org/georss'
        attrs[u'xmlns:geo'] = u'http://www.w3.org/2003/01/geo/wgs84_pos#'
        return attrs
        

class SimplePoint(object):
    def __init__(self, (x,y)):
        self.coords = (x,y)
        self.geom_type = 'Point'
    
WEEKDAYS = [u'Monday', u'Tuesday', u'Wednesday', u'Thursday', u'Friday', u'Saturday', u'Sunday']


@cache_page(60 * 60 * 0.1) # 0.1 hour
def club_classes_geo_feed(request, club=None):
    
    current_site = RequestSite(request)
    #feed = AddedGeoRSSFeed(title=u"FWC Kung Fu classes", 
    #                  link='http://%s/' % current_site.domain,
    #                  description=u"GeoRSS Feed of all FWC Kung fu venues",
    #                  language=u"en")
    feed = MyGeoAtom1Feed(title=u"FWC Kung Fu classes", 
                      link='http://%s/' % current_site.domain,
                      description=u"GeoRSS Feed of all FWC Kung fu venues",
                      language=u"en")
    
    
    def day_class_sorter(class1, class2):
        i1 = WEEKDAYS.index(class1.day)
        i2 = WEEKDAYS.index(class2.day)
        return cmp(i1, i2)
    
    all_clubs = cache.get('all_clubs')
    if all_clubs is None:
        all_clubs = Club.objects.all()
        cache.set('all_clubs', all_clubs, 3600)
        
    for club in all_clubs:
        # now lump the classes together per venue
        club_classes_cache_key = '%s_clubclasses_ordered_by_start_time' % club.name
        club_classes_cache_key.replace(' ','').lower()
        classes = cache.get(club_classes_cache_key)
        if classes is None:
            classes = ClubClass.objects.filter(club=club).order_by('start_time')
            cache.set(club_classes_cache_key, classes)
        
        venues = defaultdict(list)
        for class_ in sorted(classes, day_class_sorter):
            addresses = [class_.address1, class_.address2, class_.address3,
                         class_.address4, class_.address5]
            venue = '|'.join([x for x in addresses if x])
            venues[venue].append(class_)
            
        # now the classes are lumped per venue, lets add them to the feed
        for venue_string, classes in venues.items():
            venue = venue_string.split('|')
            venue_name = u', '.join(venue[:2])
            
            content_lines = []
            try:
                first_class = classes[0]
                instructor = Instructor.objects.get(pk=first_class.club.head_instructor.id)
            except IndexError:
                instructor = None
            
            if instructor:
                line = u"<strong>Instructor:</strong> "\
                        '<a href="http://%s%s">%s</a>' % \
                         (current_site.domain,
                          instructor.get_absolute_url(),
                          instructor.full_name)
                content_lines.append(line)
            for class_ in classes:
                content_lines.append(u'<strong>%s</strong> %s - %s' % \
                  (class_.style, class_.start_time, class_.end_time))
                
            content = '<br/>\n'.join(content_lines)
            
            try:
                point = _address_list_to_geopoint(venue)
                p = SimplePoint(point)
                feed.add_item(title=u"%s at %s" % (club.name, venue_name),
                              link='http://%s%s' % (current_site.domain, club.get_absolute_url()),
                              description=content,
                              geometry=point,
                              author_name=club.name,
                              author_email=u"",
                              author_link=u"http://%s%s" % (current_site.domain, club.get_absolute_url())
                              )
            except AddressNotFound, msg:
                print "PROBLEMS WITH"
                pprint(venue)
                print
                import warnings
                warnings.warn("Unable to find the address for %s" % msg)
    
    return HttpResponse(feed.writeString('UTF-8'), mimetype='application/atom+xml')