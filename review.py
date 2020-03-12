from google.appengine.ext import ndb

class Review( ndb.Model ):
    body = ndb.StringProperty()
    rating = ndb.IntegerProperty()
    author_name = ndb.StringProperty()
