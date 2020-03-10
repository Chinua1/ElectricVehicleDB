import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from ev import ElectricVehicle
from add_ev import AddEVPage
from search_result import SearchResultPage
from ev_details import EVDetailsPage
from ev_details_operations import EditEVPage, DeleteEVRequest

from global_variables import global_battery_size, global_cost_range, global_power_range, global_wltp_range

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

print(abs_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class MainPage( webapp2.RequestHandler ):
    def get( self ):
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
            'global_battery_size': global_battery_size,
            'global_cost_range': global_cost_range,
            'global_power_range': global_power_range,
            'global_wltp_range': global_wltp_range,
            'json_evs': json.dumps( [] )
        }

        if user and (not has_completed_profile):
            template = JINJA_ENVIRONMENT.get_template( 'pages/user_info.html' )
            self.response.write( template.render( template_values ) )
            return
        else:
            template = JINJA_ENVIRONMENT.get_template( 'pages/index.html' )
            self.response.write( template.render( template_values ) )
            return


    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        cta_button = self.request.get( 'button' )

        if cta_button == 'Update':
            user = users.get_current_user()
            logged_user_key = ndb.Key( 'User', user.user_id() )
            logged_user = logged_user_key.get()

            logged_user.firstname = self.request.get( 'user_firstname' )
            logged_user.lastname = self.request.get( 'user_lastname' )

            if logged_user.firstname == '' or logged_user.lastname == '':
                self.redirect('/')
                return
            else:
                logged_user.put()
                self.redirect( '/' )
                return

        elif cta_button == 'EV Search':
            pass


app = webapp2.WSGIApplication(
    [
        webapp2.Route( r'/', handler=MainPage, name='home'),
        webapp2.Route( r'/add-electric-vehicle', handler=AddEVPage, name='add-electric-vehicle' ),
        webapp2.Route( r'/search-result', handler=SearchResultPage, name='search-result' ),
        webapp2.Route( r'/electric-vehicles/<ev_key:[^/]+>', handler=EVDetailsPage, name='electric-vehicle-details' ),
        webapp2.Route( r'/electric-vehicles/<ev_key:[^/]+>/edit', handler=EditEVPage, name='edit-electric-vehicle-details' ),
        webapp2.Route( r'/electric-vehicles/<ev_key:[^/]+>/delete', handler=DeleteEVRequest, name='delete-electric-vehicle-record' )
    ], debug = True
)
