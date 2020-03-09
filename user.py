from google.appengine.ext import ndb
from ev import ElectricVehicle

class User( ndb.Model ):
    firstname = ndb.StringProperty()
    lastname = ndb.StringProperty()
    evs = ndb.StructuredProperty( ElectricVehicle, repeated = True )
