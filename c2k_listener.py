#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
import datetime, requests, os

### Setup Flask App and Authentication ###
app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()

### Import Environment Variables ###
c2k_msgbroker = os.getenv("c2k_msgbroker")
c2k_msgbroker_app_key = os.getenv("c2k_msgbroker_app_key")

### Authentication for future feature ###
@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


### Error Handling ###
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


### Bus Array for temporary storage of bus information.
busses = [
    {
        'id': 1,
        'name': u'bus0001',
        'route': u'Chicago North 5',
        'status': u'offline',
        'last_location': u'12345',
        'last_checkin': u'06:05:00'
    }
]


### Present Bus objects to API requests
def make_public_bus(bus):
    new_bus = {}
    for field in bus:
        new_bus[field] = bus[field]
    new_bus['uri'] = url_for('get_bus', bus_name=bus['name'], _external=True)
    return new_bus


### Get List of Busses ###
### This function is utilized to return a list of all busses and their data
@app.route('/api/v1.0/busses', methods = ['GET'])
#@auth.login_required
def get_busses():
    return jsonify( { 'busses': map(make_public_bus, busses) } )


### Get Specifc Bus Data ###
### This function is utilized to return the data for a single bus
@app.route('/api/v1.0/busses/<bus_name>', methods = ['GET'])
#@auth.login_required
def get_bus(bus_name):
    bus = filter(lambda t: t['name'] == bus_name, busses)
    if len(bus) == 0:
        abort(404)
    return jsonify( { 'bus': make_public_bus(bus[0]) } )


### Create Bus ###
### This function is utilized to create a new bus
@app.route('/api/v1.0/busses', methods = ['POST'])
#@auth.login_required
def create_bus():
    if not request.json or not 'name' in request.json:
        abort(400)
    # Determine Bus Id
    if len(busses) == 0:
        bus_id = 1
    else:
        bus_id = busses[-1]['id'] + 1

    bus = {
        'id': bus_id,
        'name': request.json['name'],
        'route': request.json['route'],
        'status': request.json['status'],
        'last_location': request.json['last_location'],
        'last_checkin': request.json['last_checkin']
    }
    busses.append(bus)
    return jsonify( { 'bus': make_public_bus(bus) } ), 201


### Update Bus ###
### This function is utilized by the remote C2K IOx service to update specifc bus data such as status, GPS coordinates, kid data, etc.
@app.route('/api/v1.0/busses/<bus_name>', methods = ['PUT'])
#@auth.login_required
def update_bus(bus_name):
    # Find a single bus by name
    bus = filter(lambda t: t['name'] == bus_name, busses)

    # Validate JSON data
    if len(bus) == 0:
        abort(404)
    if not request.json:
        abort(404)
    if 'route' in request.json and type(request.json['route']) != unicode:
        abort(400)
    if 'status' in request.json and type(request.json['status']) is not unicode:
        abort(400)
    if 'last_location' in request.json and type(request.json['last_location']) is not unicode:
        abort(400)
    if 'last_checkin' in request.json and type(request.json['last_checkin']) is not unicode:
        abort(400)

    # Update basic bus data
    bus[0]['route'] = request.json.get('route', bus[0]['route'])
    bus[0]['last_location'] = request.json.get('last_location', bus[0]['last_location'])
    bus[0]['last_checkin'] = datetime.datetime.now().isoformat()

    # If bus is previously online, any status update will trigger the bus into an online state and send a spark notification
    if bus[0]['status'] == "offline":
        bus[0]['status'] = "online"
        headers = {'content-type': 'application/json'}
        json_data = '{"appKey":"bus-01-gPHtqNh9Ua","message":"The following bus is online: '+bus_name+'"}'
        r = requests.post("http://"+c2k_msgbroker+"/c2k",json_data, headers=headers)
    elif request.json.get('status', bus[0]['status']) == "offline":
        bus[0]['status'] = "offline"
        headers = {'content-type': 'application/json'}
        json_data = '{"appKey":"'+c2k_msgbroker_app_key+'","message":"The following bus is offline: ' + bus_name + '"}'
        r = requests.post("http://" + c2k_msgbroker + "/c2k", json_data, headers=headers)
    else:
        bus[0]['status'] = request.json.get('status', bus[0]['status'])
    return jsonify( { 'bus': make_public_bus(bus[0]) } )


### Delete Bus ###
### This function is used to delete a bus by its bus name.
@app.route('/api/v1.0/busses/<bus_name>', methods = ['DELETE'])
#@auth.login_required
def delete_bus(bus_name):
    bus = filter(lambda t: t['name'] == bus_name, busses)
    if len(bus) == 0:
        abort(404)
    busses.remove(bus[0])
    return jsonify( { 'result': True } )


####################
### Main Function###
####################
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=int("5000"))
