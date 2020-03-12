from google.appengine.ext import ndb
from review import Review

class ElectricVehicle( ndb.Model ):
    name = ndb.StringProperty()
    manufacturer = ndb.StringProperty()
    year = ndb.IntegerProperty()
    battery_size = ndb.IntegerProperty()
    wltp_range = ndb.IntegerProperty()
    cost = ndb.FloatProperty()
    power = ndb.IntegerProperty()
    reviews = ndb.StructuredProperty( Review, repeated = True )
