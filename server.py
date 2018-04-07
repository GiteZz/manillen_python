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
        test_set = test_c.give_test_set()
        if test_set is not None:
            sio.emit('give_info',test_set , room=sid)
        else:
            sio.emit('ask_info', room=sid)

@sio.on('player_info_send', namespace='/')
def client_send_info(sid, data):
    print("server: client sent info, adding player")
    data["comm_module"] = comm_module
    # sid is considered player id, is used with other thing generate unique id
    comm_module.send_engine("add_player", sid, data=data)

@sio.on('viewer_info_send', namespace='/')
def client_send_info(sid, data):
    print("server: client sent info, adding viewer")
    data["comm_module"] = comm_module
    # sid is considered player id, is used with other thing generate unique id
    comm_module.send_engine("add_viewer", sid, data=data)

@sio.on('reset_game', namespace='/')
def client_send_info(sid):
    print("server, players asked to reset")
    # sid is considered player id, is used with other thing generate unique id
    comm_module.send_engine("reset_game", sid)

@sio.on('keep_waiting', namespace='/')
def client_send_info(sid):
    print("server, players asked to reset")
    # sid is considered player id, is used with other thing generate unique id
    comm_module.send_engine("keep_waiting", sid)


@sio.on('answer_card', namespace='/')
def client_answer_card(sid, data):
    comm_module.send_engine("answer_card", sid, data=data)

@sio.on('disconnect', namespace='/')
def disconnect(sid):
    comm_module.send_engine("disconnect", sid)
    socket_list.remove(sid)
    print("client left, amount of connected clients is: " + str(len(socket_list)))


@sio.on('answer_troef', namespace='/')
def answer_troef(sid, card):
    comm_module.send_engine("answer_troef", sid, data=card)


def choose_troef(id):
    sio.emit('choose_troef', room=id)


def wait_other_players(id):
    sio.emit('wait_other_players', room=id)

def set_game_info(id, data):
    sio.emit('set_game_info', data, room=id)

if __name__ == '__main__':
    comm_module = communication_module(sio)

    engine = game_engine.engine()

    comm_module.add_engine_function_dict(engine.get_functions())

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

