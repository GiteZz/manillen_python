import socketio
from flask import Flask, render_template
import eventlet.wsgi
import eventlet
import game_engine
from communication_module import communication_module
from test_manillen import test_class

sio = socketio.Server()
app = Flask(__name__)
socket_list = []
#connects sid to player id
player_set = {}
#connects player id to sid
sid_set = {}

engine = None

comm_module = None

test_game = True
if test_game:
    test_c = test_class("test_database.txt")


@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@sio.on('client_connect', namespace='/')
def client_connect(sid):
    socket_list.append(sid)
    ask_client_info(sid, testing=False)
    print("connected new client, amount of connected clients is: " + str(len(socket_list)))


def ask_client_info(sid, testing=test_game):
    if not test_game:
        sio.emit('ask_info', room=sid)
    else:
        sio.emit('give_info', test_c.give_test_set(), room=sid)

@sio.on('client_info_send', namespace='/')
def client_send_info(sid, data):
    print("server: client sent info, adding player")

    # sid is considered player id, is used with other thing generate unique id
    comm_module.send_engine("add_player", sid, data)


@sio.on('answer_card', namespace='/')
def client_answer_card(sid, data):
    comm_module.send_engine("answer_card", sid, data)

@sio.on('disconnect', namespace='/')
def disconnect(sid):
    socket_list.remove(sid)
    print("client left, amount of connected clients is: " + str(len(socket_list)))


@sio.on('answer_troef', namespace='/')
def answer_troef(sid, card):
    comm_module.send_engine("answer_troef", sid, card)


def choose_troef(id):
    sio.emit('choose_troef', room=id)


def wait_other_players(id):
    sio.emit('wait_other_players', room=id)

def set_game_info(id, data):
    sio.emit('set_game_info', data, room=id)

if __name__ == '__main__':
    comm_module = communication_module(sio)

    engine = game_engine.engine(comm_module)

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

