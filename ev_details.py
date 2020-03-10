import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from ev import ElectricVehicle

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

print(abs_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class EVDetailsPage( webapp2.RequestHandler ):
    def get( self, ev_key ):
        self.response.headers[ 'Content-Type' ] = 'text/html'

        url = ''
        url_string = ''
        logged_user = None
        user = users.get_current_user()
        has_completed_profile = False
        user_name = ''
        has_params = False
        params_key = ''
        params_value = ''

        try:
            if self.request.params.get('success') != None:
                has_params = True
                params_key = 'success'
                params_value = self.request.params.get('success')
        except:
            pass

        if user:
            url = users.create_logout_url( self.request.uri )
            url_string = 'logout'

            logged_user_key = ndb.Key( 'User', user.user_id() )
            logged_user = logged_user_key.get()

            if logged_user == None:
                logged_user = User( id = user.user_id() )
                logged_user.put()

            else:
                if logged_user.firstname == None:
                    has_completed_profile = False
                else:
                   has_completed_profile = True
                   user_name = logged_user.firstname + ' ' + logged_user.lastname

        else:
            url = users.create_login_url( self.request.uri )
            url_string = 'login'

        selected_ev = None
        ev_list = ElectricVehicle.query().fetch( keys_only = True )
        for item in ev_list:
            if str( item.id() ) == ev_key:
                selected_ev = item.get()
                break

        template_values = {
            'url': url,
            'url_string': url_string,
            'logged_user': logged_user,
            'year': datetime.datetime.now().year,
            'user': user,
            'completed_profile': has_completed_profile,
            'user_name': user_name,
            'params_key': params_key,
            'params_value': params_value,
            'has_params': has_params,
            'show_logout': True,
            'ev_key': ev_key,
            'ev': selected_ev
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/ev_details.html' )
        self.response.write( template.render( template_values ) )
