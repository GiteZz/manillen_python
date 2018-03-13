import socketio
from manillen_classes import player,team, game
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
import logging


sio = socketio.Server()
app = Flask(__name__)
gameset = {}
socket_list = []
game_list = []

@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@sio.on('client_connect', namespace='/')
def client_connect(sid):
    socket_list.append(sid)
    print("connected new client, amount of connected clients is: " + str(len(socket_list)))


@sio.on('client_info_send', namespace='/')
def client_send_info(sid, data):
    table_name = data["table_name"]
    team_name = data["team_name"]
    position = data["position"]
    player_name = data["player_name"]

    this_player = player(player_name, sid)
    if table_name in game_set:
        this_game = game_set[table_name]
        team = this_game.team_exists(team_name)
        if team is None:
            this_team = team(team_name)


@sio.on('chat message', namespace='/')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)


@sio.on('disconnect', namespace='/')
def disconnect(sid):
    socket_list.remove(sid)
    remove_player(sid)
    print("client left, amount of connected clients is: " + str(len(socket_list)))


def play(table_name):
    if table_set[table_name]["troef"] is None:
        #troef should be chosen
        sio.emit('server_ask_troef', room=table_set[table_name]["players_sid"][table_set[table_name]["troef_choser"]])


def add_player_to_table(table_name, player_name, pos, sid):
    if table_name in table_set:
        if table_set[table_name]["players"][pos] is None:
            table_set[table_name]["players_name"][pos] =  player_name
            table_set[table_name]["players_sid"][pos] = sid
            table_set[table_name]["amount_players"] += 1
            player_set[sid] = {"player_name":player_name, "table_name":table_name}
        else:
            print("add_player_to_table: position already chosen")
    else:
        add_new_table(table_name)
        add_player_to_table(table_name, player_name, pos, sid)


def remove_player(sid):
    #check if socket was player or not
    if sid in player_set:
        table_name = player_set[sid]["table_name"]
        player_name = player_set[sid]["player_name"]
        remove_player_table(table_name, player_name)


def remove_player_table(table_name, player_name):
    table_set[table_name]["amount_players"] -= 1
    table_position = table_set[table_name]["players_name"].index(player_name)
    table_set[table_name]["players_name"][table_position] = None
    table_set[table_name]["players_sid"][table_position] = None


def add_new_table(name):
    table_set[name]={"players_name":[None]*4, "players_sid":[None]*4,
                     "score":[0,0], "troef_choser":0, "troef": None,"cards_on_table":[],
                     "round_starting_pos":1, "round_play_offset":0, "amount_players":0}


if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('',5000)), app)
