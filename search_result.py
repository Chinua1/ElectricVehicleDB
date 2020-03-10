import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from ev import ElectricVehicle

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

class SearchResultPage( webapp2.RequestHandler ):
    def get( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        cta_button = self.request.get( 'button' )

        url = ''
        url_string = ''
        logged_user = None
        user = users.get_current_user()
        has_completed_profile = False
        user_name = ''
        params_key = ''
        params_value = ''
        search_params = {}
        search_list = []

        test = None

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

        if cta_button == 'Update':
            pass

        elif cta_button == 'EV Search':
            search_params['name'] = self.getRequestParams('ev_name')
            search_params['manufacturer'] = self.getRequestParams('ev_manufacturer')
            search_params['year'] = self.getRequestParams('ev_year')
            search_params['battery_size'] = [ self.getRequestParams('ev_battery_size_lower'), self.getRequestParams('ev_battery_size_upper') ]
            search_params['wltp_range'] = [ self.getRequestParams('ev_wltp_range_lower'), self.getRequestParams('ev_wltp_range_upper') ]
            search_params['cost'] = [ self.getRequestParams('ev_cost_lower'), self.getRequestParams('ev_cost_upper') ]
            search_params['power'] = [ self.getRequestParams('ev_power_lower'), self.getRequestParams('ev_power_upper') ]

            query_list = []
            item_on_single_query = []

            if self.queryHasSearchParams(search_params):
                for key in search_params.keys():
                    if type(search_params[key]) == type([]):
                        if search_params[key][0] or search_params[key][1]:
                            if key == 'battery_size':
                                query_list.append( ElectricVehicle.query( ndb.AND( ElectricVehicle.battery_size >= search_params[key][0], ElectricVehicle.battery_size <= search_params[key][1] )  ).fetch( keys_only = True ) )
                            elif key == 'wltp_range':
                                query_list.append( ElectricVehicle.query( ndb.AND( ElectricVehicle.wltp_range >= search_params[key][0], ElectricVehicle.wltp_range <= search_params[key][1] ) ).fetch( keys_only = True ) )
                            elif key == 'cost':
                                query_list.append( ElectricVehicle.query( ndb.AND( ElectricVehicle.cost >= search_params[key][0], ElectricVehicle.cost <= search_params[key][1] ) ).fetch( keys_only = True ) )
                            elif key == 'power':
                                query_list.append( ElectricVehicle.query( ndb.AND( ElectricVehicle.power >= search_params[key][0], ElectricVehicle.power <= search_params[key][1] ) ).fetch( keys_only = True ) )
                    else:
                         if search_params[key]:
                            if key == 'name':
                                query_list.append( ElectricVehicle.query( ElectricVehicle.name == search_params[key] ).fetch( keys_only = True ) )
                            elif key == 'manufacturer':
                                query_list.append( ElectricVehicle.query( ElectricVehicle.manufacturer == search_params[key] ).fetch( keys_only = True ) )
                            elif key == 'year':
                                query_list.append( ElectricVehicle.query( ElectricVehicle.year == search_params[key] ).fetch( keys_only = True ) )


            if len(query_list) == 0:
                search_list = []

            elif len(query_list) == 1:
                compound_query = query_list[0]
                for ev in compound_query:
                    search_list.append( ev.get() )

            elif len(query_list) == 2:
                compound_query = ndb.get_multi( set( query_list[0] ).intersection( query_list[1] ) )
                for ev in compound_query:
                    search_list.append( ev )
            else:
                compound_query_list = []
                for i in range( 1, len(query_list) ):
                    if query_list[i-1] and query_list[i]:
                        compound_query_list.append(ndb.get_multi( set( query_list[i-1] ).intersection( query_list[i] ) ))
                    else:
                        if query_list[i-1]:
                            for ev in query_list[i-1]:
                                item_on_single_query.append(ev.get())
                        elif query_list[i]:
                            for ev in query_list[i]:
                                item_on_single_query.append(ev.get())

                seen = set()
                for ev_model in compound_query_list:
                    for ev in ev_model:
                        if ev.key.id in seen:
                            pass
                        else:
                            if not ev.name:
                                seen.add(ev.get())

                search_list = list( seen )

            if len(item_on_single_query) > 0:
                for item in item_on_single_query:
                    if self.itemSatisfiedQuery(search_params, item):
                        index = 0
                        try:
                            if search_list.index(item) >= 0:
                                index = search_list.index(item)
                            else:
                                index = -1
                        except:
                            index = -1

                        if index < 0:
                            search_list.append(item)
                    else:
                        pass


            if not self.queryHasSearchParams( search_params ):
                search_list = ElectricVehicle.query().fetch()

            search_factor = None
            for key in search_params.keys():
                if search_params[key]:
                    search_factor = search_params[key]
                    if search_factor:
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
                'show_logout': True,
                'has_params': self.queryHasSearchParams( search_params ),
                'search_params': search_params,
                'search_list': search_list,
                'search_list_length': len( search_list ),
                'global_battery_size': global_battery_size,
                'global_cost_range': global_cost_range,
                'global_power_range': global_power_range,
                'global_wltp_range': global_wltp_range
            }

            template = JINJA_ENVIRONMENT.get_template( 'pages/search_result.html' )
            self.response.write( template.render( template_values ) )
            return

    def getRequestParams( self, input_name ):
        try:
            if self.request.params.get( input_name ) == '':
                return self.request.params.get( input_name )
            elif self.request.params.get( input_name ) != '':
                try:
                    if input_name == 'ev_cost':
                        return float( self.request.params.get( input_name ) )
                    elif input_name == 'ev_year':
                        return int( self.request.params.get( input_name ) ) if self.request.params.get( input_name ) else 0
                    else:
                        return int( self.request.params.get( input_name ) )
                except:
                    return self.request.params.get( input_name )
            else:
                return ''
        except:
            return None

    def queryHasSearchParams(self, search_params_dict):
        hasParams = False
        for key in search_params_dict.keys():
            if type(search_params_dict[key]) == type([]):
                for item in search_params_dict[key]:
                    if item:
                        hasParams = True
            else:
                if search_params_dict[key]:
                    hasParams = True
        return hasParams

    def itemSatisfiedQuery(self, search_params_dict, item):
        is_valid = True
        for key in search_params_dict.keys():
            if type(search_params_dict[key]) == type([]):
                if search_params_dict[key][0] or search_params_dict[key][1]:
                    if key == 'battery_size':
                        if not ((item.battery_size >= search_params_dict[key][0]  and item.battery_size <= search_params_dict[key][1])):
                            is_valid = False
                    elif key == 'wltp_range':
                        if not ((item.wltp_range >= search_params_dict[key][0]  and item.wltp_range <= search_params_dict[key][1])):
                            is_valid = False
                    elif key == 'cost':
                        if not ((item.cost >= search_params_dict[key][0]  and item.cost <= search_params_dict[key][1])):
                            is_valid = False
                    elif key == 'power':
                        if ((item.power >= search_params_dict[key][0]  and item.power <= search_params_dict[key][1])):
                            is_valid = False
            else:
                if search_params_dict[key]:
                    if key == 'name':
                        if not search_params_dict[key] == item.name:
                            is_valid = False
                    elif key == 'manufacturer':
                        if not search_params_dict[key] == item.manufacturer:
                            is_valid = False
                    elif key == 'year':
                        if not search_params_dict[key] == item.year:
                            is_valid = False
        return is_valid
