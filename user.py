from google.appengine.ext import ndb

class User( ndb.Model ):
    firstname = ndb.StringProperty()
    lastname = ndb.StringProperty()
