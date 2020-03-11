import webapp2
import jinja2
import os
import datetime
import json

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

class CompareEVsPage( webapp2.RequestHandler ):
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
            if self.request.params.get('failed') != None:
                has_params = True
                params_key = 'failed'
                params_value = self.request.params.get('failed')
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
            'json_evs': json.dumps( [ dict(ev.to_dict(), **dict(id=ev.key.id())) for ev in  ElectricVehicle.query().fetch() ] )
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/compare_evs.html' )
        self.response.write( template.render( template_values ) )


    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'application/json'
        str_key= self.request.body
        keys = str_key.split('-')
        keys.pop(0)
        unique_key = list(set(keys))
        response_dict = {}

        if len( unique_key ) <= 1:
            response_dict['status'] = 'error'
            response_dict['code'] = 400
            response_dict['message'] = 'You CANNOT compare same EV. Please select different EVs.'
            response_dict['responseData'] = []
            self.response.write( json.dumps( response_dict ) )
            return
        else:
            evs_to_compare = []
            ev_list = ElectricVehicle.query().fetch( keys_only = True )
            for item in ev_list:
                for key in keys:
                    if str( item.id() ) == key:
                        evs_to_compare.append(item.get())
                        break

            name = [ self.getMaxValue(evs_to_compare, 'name'), self.getMinValue(evs_to_compare, 'name')]
            manufacturer = [ self.getMaxValue(evs_to_compare, 'manufacturer'), self.getMinValue(evs_to_compare, 'manufacturer')]
            year = [ self.getMaxValue(evs_to_compare, 'year'), self.getMinValue(evs_to_compare, 'year')]
            power = [ self.getMaxValue(evs_to_compare, 'power'), self.getMinValue(evs_to_compare, 'power')]
            wltp_range = [ self.getMaxValue(evs_to_compare, 'wltp_range'), self.getMinValue(evs_to_compare, 'wltp_range')]
            battery_size = [ self.getMaxValue(evs_to_compare, 'battery_size'), self.getMinValue(evs_to_compare, 'battery_size')]
            cost = [ self.getMaxValue(evs_to_compare, 'cost'), self.getMinValue(evs_to_compare, 'cost')]

            response_dict['status'] = 'success'
            response_dict['code'] = 200
            response_dict['message'] = 'API query successful'
            response_dict['responseData'] = {
                'name': name,
                'manufacturer': manufacturer,
                'year': year,
                'power': power,
                'wltp_range': wltp_range,
                'battery_size': battery_size,
                'cost': cost
            },
            response_dict['unique_keys'] = unique_key
            self.response.write( json.dumps( response_dict ) )
            return

    def getMaxValue(self, evs_to_compare, props):
        max = None

        if props == 'name':
            return ''
        elif props == 'manufacturer':
            return ''
        elif props == 'year':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    max = 0
                else:
                    if evs_to_compare[max].year < evs_to_compare[n].year:
                        max = n
            return str(evs_to_compare[max].key.id())
        elif props == 'power':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    max = 0
                else:
                    if evs_to_compare[max].power < evs_to_compare[n].power:
                        max = n
            return str(evs_to_compare[max].key.id())
        elif props == 'wltp_range':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    max = 0
                else:
                    if evs_to_compare[max].wltp_range < evs_to_compare[n].wltp_range:
                        max = n
            return str(evs_to_compare[max].key.id())
        elif props == 'battery_size':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    max = 0
                else:
                    if evs_to_compare[max].battery_size < evs_to_compare[n].battery_size:
                        max = n
            return str(evs_to_compare[max].key.id())
        elif props == 'cost':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    max = 0
                else:
                    if evs_to_compare[max].cost < evs_to_compare[n].cost:
                        max = n
            return str(evs_to_compare[max].key.id())

    def getMinValue(self, evs_to_compare, props):
        min = None

        if props == 'name':
            return ''
        elif props == 'manufacturer':
            return ''
        elif props == 'year':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    min = 0
                else:
                    if evs_to_compare[min].year > evs_to_compare[n].year:
                        min = n
            return str(evs_to_compare[min].key.id())
        elif props == 'power':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    min = 0
                else:
                    if evs_to_compare[min].power > evs_to_compare[n].power:
                        min = n
            return str(evs_to_compare[min].key.id())
        elif props == 'wltp_range':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    min = 0
                else:
                    if evs_to_compare[min].wltp_range > evs_to_compare[n].wltp_range:
                        min = n
            return str(evs_to_compare[min].key.id())
        elif props == 'battery_size':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    min = 0
                else:
                    if evs_to_compare[min].battery_size > evs_to_compare[n].battery_size:
                        min = n
            return str(evs_to_compare[min].key.id())
        elif props == 'cost':
            for n in range(0, len(evs_to_compare)):
                if n == 0:
                    min = 0
                else:
                    if evs_to_compare[min].cost > evs_to_compare[n].cost:
                        min = n
            return str(evs_to_compare[min].key.id())
