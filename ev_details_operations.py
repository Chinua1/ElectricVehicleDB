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


JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class EditEVPage( webapp2.RequestHandler ):
    def get( self, ev_key ):
        self.response.headers[ 'Content-Type' ] = 'text/html'

        user = users.get_current_user()
        has_completed_profile = True
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        user_name = logged_user.firstname + ' ' + logged_user.lastname
        url = users.create_logout_url( self.request.uri )
        url_string = 'logout'
        has_params = False
        params_key = ''
        params_value = ''

        try:
            if self.request.params.get('failed') != None:
                has_params = True
                params_key = 'failed'
                params_value = self.request.params.get('failed')
        except:
            pass

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
            'user': user,
            'completed_profile': has_completed_profile,
            'year': datetime.datetime.now().year,
            'user_name': user_name,
            'params_key': params_key,
            'params_value': params_value,
            'has_params': has_params,
            'show_logout': False,
            'ev_key': ev_key,
            'ev': selected_ev
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/edit_ev.html' )
        self.response.write( template.render( template_values ) )

    def post( self, ev_key ):
        self.response.headers[ 'Content-Type' ] = 'text/html'

        # Get form input data
        ev_name = self.request.get( 'ev_name' )
        ev_manufacturer = self.request.get( 'ev_manufacturer' )
        ev_year = self.request.get( 'ev_year' ) if  self.request.get( 'ev_year' ) == '' else int( self.request.get( 'ev_year' ) )
        ev_battery_size = int( self.request.get( 'ev_battery_size' ) )
        ev_wltp_range = int( self.request.get( 'ev_wltp_range' ) )
        ev_cost = float( self.request.get( 'ev_cost' ) )
        ev_power = int( self.request.get( 'ev_power' ) )

        if ev_name == '' or ev_manufacturer == '' or ev_year == '' or ev_battery_size == 0 or ev_cost == 0 or ev_power == 0:
            err_msg = 'Failed to update EV, please complete all required fields"'
            query_string = '?failed="' + err_msg
            url = '/electric-vehicles/' + ev_key + '/edit' + query_string
            self.redirect( url )
            return
        else:
            ev = None
            ev_list = ElectricVehicle.query().fetch( keys_only = True )
            for item in ev_list:
                if str( item.id() ) == ev_key:
                    ev = item.get()
                    break

            ev.name = ev_name
            ev.manufacturer = ev_manufacturer
            ev.year = ev_year
            ev.battery_size = ev_battery_size
            ev.power = ev_power
            ev.wltp_range = ev_wltp_range
            ev.cost = ev_cost
            ev.put()
            query_string = '?success="EV successfully updated."'
            url = '/electric-vehicles/' + ev_key + '' + query_string
            self.redirect( url )

class DeleteEVRequest( webapp2.RequestHandler ):
    def post( self, ev_key ):
        ev = None
        ev_list = ElectricVehicle.query().fetch( keys_only = True )
        for item in ev_list:
            if str( item.id() ) == ev_key:
                ev = item
                break

        ev.delete()
        query_string = '?success="EV successfully deleted."'
        url = '/' + query_string
        self.redirect( url )
