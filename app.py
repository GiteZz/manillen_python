import socketio
from manillen_classes import player, team, game
import eventlet
import manillen_const
import cards
import eventlet.wsgi
from flask import Flask, render_template
import logging
from test_manillen import test_class

sio = socketio.Server()
app = Flask(__name__)
game_set = {}
game_set_sid = {}
socket_list = []
game_list = []

test = True
if test:
    test_c = test_class("test_database.txt")


@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@sio.on('client_connect', namespace='/')
def client_connect(sid):
    socket_list.append(sid)
    if not test:
        sio.emit('ask_info', room=sid)
    else:
        sio.emit('give_info', test_c.give_test_set(), room=sid)
    print("connected new client, amount of connected clients is: " + str(len(socket_list)))


@sio.on('client_info_send', namespace='/')
def client_send_info(sid, data):
    print("client sent info, adding player")
    table_name = data["table_name"]
    team_name = data["team_name"]
    position = data["table_location"]
    player_name = data["player_name"]

    player_game = create_player(player_name, team_name, table_name, position, sid)

    sio.emit('wait_other_players', room=sid)
    print("Amount of players in this game: " + str(len(player_game)))

    if len(player_game) == 4:
        start_play(player_game)


@sio.on('chat message', namespace='/')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)


@sio.on('disconnect', namespace='/')
def disconnect(sid):
    socket_list.remove(sid)
    print("client left, amount of connected clients is: " + str(len(socket_list)))


def start_play(game):
    player_cards = cards.getCards({"min": "7", "split_stack": 4, "shuffle": True})
    for i in range(4):
        game.players[i].set_cards(player_cards[i])
        sio.emit('set_cards', player_cards[i], room=game.players[i].sid)
    game.set_default_indices()
    play_round(game)


def play_round(game):
    for team in game.teams:
        if team.score > manillen_const.score_end:
            end_game(game)
    troef_choser = game.players[game.round_start_pos]
    game.round_start_pos += 1
    sio.emit('choose_troef', room=troef_choser.sid)
    

def end_game(game):
    a =5


def create_player(player_name, team_name, table_name, position, sid):
    this_player = player(player_name, sid, position=int(position))
    if table_name in game_set:
        this_game = game_set[table_name]
    else:
        this_game = game(table_name)
        game_set[table_name] = this_game

    this_player.set_game(this_game)

    this_team = this_game.get_team(team_name)
    # team doesn't exist
    if this_team is None:
        this_team = team(team_name)
        this_game.add_team(this_team)
        this_team.set_game(this_game)

    this_team.add_player(this_player)
    this_player.add_team(this_team)
    game_set_sid[sid] = this_game
    this_game.add_player(this_player)

    return this_game


if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
