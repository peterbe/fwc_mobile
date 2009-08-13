from django.conf import settings

from geopy import geocoders

class AddressNotFound(Exception):
    pass

def geopy_geocode(address, google_key=settings.GOOGLEMAPS_API_KEY,
                  domain='maps.google.co.uk', exactly_one=True):
    g = geocoders.Google(google_key, domain=domain)
    return g.geocode(address, exactly_one=exactly_one)

def geopy_geocode_yahoo(address, yahoo_key=settings.YAHOO_API_KEY, 
                        exactly_one=True):
    g = geocoders.Yahoo(yahoo_key)
    return g.geocode(address, exactly_one=exactly_one)


