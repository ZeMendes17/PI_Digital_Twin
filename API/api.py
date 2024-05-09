import threading
from asyncio import sleep
import json
import os
import signal
import subprocess
from flask import Flask, request, jsonify, Response, make_response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import flask_socketio as socketio
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import decode_token, JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = socketio.SocketIO(app, cors_allowed_origins="*")

app.secret_key = 'myawesomesecretkey'
app.config['JWT_SECRET_KEY'] = 'mysecretkey' 

app.config['MONGO_URI'] = 'mongodb://localhost:27017/digitaltwin'
mongo = PyMongo(app)
jwt = JWTManager(app)

SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

process3d = None
process2d = None
processCarla = None

number_of_vehicles = 0
blocked_roundabouts = []

@app.route('/api')
def api():
    return jsonify({'data': 'Hello, World!'})


@app.route('/users', methods=['POST'])
def create_user():
    # Receiving Data
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if username and email and password:
        hashed_password = generate_password_hash(password)
        result = mongo.db.users.insert_one(
            {'username': username, 'email': email, 'password': hashed_password})
        response = jsonify({
            '_id': str(result.inserted_id),
            'username': username,
            'password': password,
            'email': email
        })
        response.status_code = 201
        return response
    else:
        return not_found()


@app.route('/user', methods=['GET'])
def get_user():

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Access Token is missing'}), 401

    token = auth_header.split(' ')[1]
    print(f"Token: {token}")
    try:
        decoded_token = decode_token(token)
        print(f"Decoded Token: {decoded_token}")
        email = decoded_token['sub']
        print(f"Email: {email}")
    except Exception as e:
        return jsonify({'message': 'Invalid token'}), 401

    user = mongo.db.users.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")


@app.route('/api/login', methods=['POST'])
def login():

    email = request.json['email']
    password = request.json['password']

    user = mongo.db.users.find_one({'email': email})

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({'message': 'Incorrect password'}), 401

    access_token = create_access_token(identity=email)
    print(f"Access Token: {access_token}")

    response = make_response(jsonify({'message': 'Login successful', 'username': user['username'], 'token': access_token}), 200)
    response.headers['Authorization'] = f'Bearer {access_token}'
    return response


@app.route('/user', methods=['DELETE'])
def delete_user():

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Access Token is missing'}), 401

    token = auth_header.split(' ')[1]

    try:
        decoded_token = decode_token(token)
        email = decoded_token['sub'] 
    except Exception as e:
        return jsonify({'message': 'Invalid token'}), 401

    user = mongo.db.users.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    mongo.db.users.delete_one({'_id': ObjectId(user['_id'])})
    response = jsonify({'message': 'User ' + email + ' Deleted Successfully'})
    response.status_code = 200
    return response


@app.route('/user', methods=['PUT'])
def update_user():

    username = request.json['username']
    email = request.json['email']

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Access Token is missing'}), 401

    token = auth_header.split(' ')[1]
    print(f"Token: {token}")

    try:
        decoded_token = decode_token(token)
        print(f"Decoded Token: {decoded_token}")

        email = decoded_token['sub'] 
        print(f"Email: {email}")
    except Exception as e:
        return jsonify({'message': 'Invalid token'}), 401

    user = mongo.db.users.find_one({'email': email})
    print(f"User: {user}")
    if not user:
        return jsonify({'message': 'User not found'}), 404

    update_data = {}
    if username:
        update_data['username'] = username
    if email:
        update_data['email'] = email

    mongo.db.users.update_one(
        {'email': email},
        {'$set': update_data}
    )

    return jsonify({'message': 'User updated successfully'}), 200


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response


@app.route('/api/run3D', methods=['POST'])
def run_3D():
    try:
        global processCarla
        processCarla = subprocess.Popen(["./../Adapters/co_simulation/runCarla.sh"])
        sleep(10)

        global process3d
        process3d = subprocess.Popen(["python3", "../Adapters/co_simulation/simulation_3D.py"])
        return jsonify({'message': 'Comando executado com sucesso'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e}), 500

@app.route('/api/runLive3D', methods=['POST'])
def run_Live3D():
    try:
        global processCarla
        processCarla = subprocess.Popen(["./../Adapters/co_simulation/runCarla.sh"])
        sleep(10)

        global process3d
        process3d = subprocess.Popen(["python3", "../Adapters/co_simulation/simulation_3D.py"])
        return jsonify({'message': 'Comando executado com sucesso'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e}), 500

@app.route('/api/run2D', methods=['POST'])
def run_2D():
    try:
        global process2d
        process2d = subprocess.Popen(["python3", "../Adapters/co_simulation/simulation_2D.py"])
        global blocked_roundabouts
        blocked_roundabouts = []
        return jsonify({'message': 'Comando iniciado com sucesso'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e}), 500

@app.route('/api/runLive2D', methods=['POST'])
def run_Live2D():
    try:
        global process2d
        process2d = subprocess.Popen(["python3", "../Adapters/co_simulation/live_simulation2D.py"])
        global blocked_roundabouts
        blocked_roundabouts = []
        return jsonify({'message': 'Comando iniciado com sucesso'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e}), 500

@app.route('/api/addRandomTraffic', methods=['POST'])
def add_random_traffic():
    qtd = request.args.get('qtd')
    if qtd is None:
        return jsonify({'error': 'Parâmetro "qtd" é obrigatório na URL'}), 400

    try:
        publish.single("/addRandomTraffic", payload=f'{qtd}', hostname="localhost", port=1883)
        return jsonify({'message': f'Tráfego aleatório adicionado para {qtd} veículos'}), 200
    except Exception as e:
        return jsonify({'error': e}), 500

    # curl -X POST -d "" "http://localhost:5000/api/addRandomTraffic?qtd=500"

@app.route('/api/addRandomPedestrian', methods=['POST'])
def add_random_pedestrian():
    qtd = request.args.get('qtd')
    if qtd is None:
        return jsonify({'error': 'Parâmetro "qtd" é obrigatório na URL'}), 400

    try:
        publish.single("/addRandomPedestrian", payload=f'{qtd}', hostname="localhost", port=1883)
        return jsonify({'message': f'Pedestres aleatórios adicionados para {qtd} pedestres'}), 200
    except Exception as e:
        return jsonify({'error': e}), 500

    # curl -X POST -d "" "http://localhost:5000/api/addRandomTraffic?qtd=500"


@app.route('/api/addRandomMotorcycle', methods=['POST'])
def add_random_motorcycle():
    qtd = request.args.get('qtd')
    if qtd is None:
        return jsonify({'error': 'Parâmetro "qtd" é obrigatório na URL'}), 400

    try:
        publish.single("/addRandomMotorcycle", payload=f'{qtd}', hostname="localhost", port=1883)
        return jsonify({'message': f'Motocicletas aleatórias adicionadas para {qtd} motocicletas'}), 200
    except Exception as e:
        return jsonify({'error': e}), 500


@app.route('/api/addRandomBike', methods=['POST'])
def add_random_bike():
    qtd = request.args.get('qtd')
    if qtd is None:
        return jsonify({'error': 'Parâmetro "qtd" é obrigatório na URL'}), 400

    try:
        publish.single("/addRandomBike", payload=f'{qtd}', hostname="localhost", port=1883)
        return jsonify({'message': f'Motocicletas aleatórias adicionadas para {qtd} motocicletas'}), 200
    except Exception as e:
        return jsonify({'error': e}), 500


@app.route('/api/testaddRealCar', methods=['POST'])
def test_add_real_car():
    try:
        data = request.json  # Acessa o JSON enviado no corpo da solicitação
        # Aqui você pode manipular os dados como desejar
        print("Dados recebidos:", data)

        # Exemplo: extrair o ID do veículo do JSON recebido
        vehicle_id = data.get('objectID')
        if vehicle_id is not None:
            # Faça algo com o ID do veículo, como publicá-lo em um tópico MQTT
            publish.single("/realDatateste", payload=json.dumps(data), hostname="localhost", port=1883)

        return jsonify({'message': 'Veículo adicionado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # curl - X POST - H "Content-Type: application/json" -d '{
    #"acceleration": 0.0,
    #"classification": 5,
    #"cloudPersist": false,
    #"confidence": 100,
    #"heading": -25.311,
    #"latitude": 40.635327506990194,
    #"length": 5.6000000000000005,
    #"longitude": -8.660106693274248,
    #"objectID": 1015,
    #"receiverID": 1,
    #"speed": 10.9,
    #"test": {},
    #"timestamp": 1710954013.329629 }'   http://localhost:5000/api/testaddRealCar


@app.route('/api/addSimulatedCar', methods=['POST'])
def add_car():
    try:
        data = request.json  # Acessa o JSON enviado no corpo da solicitação
        # Aqui você pode manipular os dados como desejar
        print("Dados recebidos:", data)
        publish.single("/addSimulatedCar", payload=json.dumps(data), hostname="localhost", port=1883)
        return jsonify({'message': 'Veículo adicionado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    #curl -X POST -H "Content-Type: application/json" -d '{
    #"end": {"lng": "-8.655386132941464", "lat": "40.63525392116133"},
    #"start": {"lng": "-8.660106693274248", "lat": "40.635327506990194"}
    #}' http://localhost:5000/api/addSimulatedCar


@app.route('/api/endSimulation', methods=['POST'])
def end_simulation():
    try:
        publish.single("/endSimulation", payload="", hostname="localhost", port=1883)
        if process2d is not None:
            process2d.kill()

        if process3d is not None:
            process3d.kill()

        if processCarla is not None:
            processCarla.send_signal(signal.SIGINT)

        return jsonify({'message': 'Simulação finalizada com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # curl -X POST -d "" "http://localhost:5000/api/endSimulation"


@app.route('/api/cars', methods=['POST'])
def cars():
    try:
        data = request.json
        print("Dados recebidos:", data)
        return jsonify({'message': 'Veículo adicionado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clearSimulation', methods=['GET'])
def clear_simulation():
    try:
        publish.single("/clearSimulation", payload="", hostname="localhost", port=1883)
        return jsonify({'message': 'Simulação finalizada com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # curl -X GET "http://localhost:5000/api/clearSimulation"

@app.route('/api/blockRoundabout', methods=['POST'])
def block_roundabout():
    roundabout_id = request.args.get('id')
    if roundabout_id is None:
        return jsonify({'error': 'Parâmetro "id" é obrigatório na URL'}), 400
    
    try:
        publish.single("/blockRoundabout", payload=roundabout_id, hostname="localhost", port=1883)
        return jsonify({'message': f'Rotunda {roundabout_id} bloqueada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # curl -X POST -d "" "http://localhost:5000/api/blockRoundabout?id=1"

@app.route('/api/unblockRoundabout', methods=['POST'])
def unblock_roundabout():
    roundabout_id = request.args.get('id')
    if roundabout_id is None:
        return jsonify({'error': 'Parâmetro "id" é obrigatório na URL'}), 400
    
    try:
        publish.single("/unblockRoundabout", payload=roundabout_id, hostname="localhost", port=1883)
        return jsonify({'message': f'Rotunda {roundabout_id} desbloqueada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # curl -X POST -d "" "http://localhost:5000/api/unblockRoundabout?id=1"

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    return jsonify({'quantity': number_of_vehicles})

    # curl -X GET "http://localhost:5000/api/vehicles"

@app.route('/api/blockedRoundabouts', methods=['GET'])
def get_blocked_roundabouts():
    return jsonify({'blocked_roundabouts': blocked_roundabouts})

    # curl -X GET "http://localhost:5000/api/blockedRoundabouts"

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso (api)")


def on_message(client, userdata, msg):
    topic = msg.topic

    if topic == '/cars':
        ## usar socketio para enviar a mensagem para o front
        socketio.emit('cars', msg.payload)
        vehicle_data = json.loads(msg.payload)
        global number_of_vehicles
        number_of_vehicles = int(vehicle_data['vehicle']['quantity'])

    if topic == '/blocked_rounds':
        socketio.emit('blocked_roundabouts', msg.payload)
        blocked_roundabouts_data = json.loads(msg.payload)
        global blocked_roundabouts
        for roundabout in blocked_roundabouts_data['blocked_roundabouts'].keys():
            if roundabout not in blocked_roundabouts:
                blocked_roundabouts.append(roundabout)

def start_mqtt_connection():
    # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.subscribe("/cars")
    mqtt_client.subscribe("/blocked_rounds")


    mqtt_client.loop_forever()  # Use loop_forever() para manter a conexão MQTT em execução indefinidamente

def start_flask():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    # Inicie a conexão MQTT em uma nova thread
    mqtt_thread = threading.Thread(target=start_mqtt_connection)
    mqtt_thread.start()

    # Inicie o Flask em uma nova thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()
