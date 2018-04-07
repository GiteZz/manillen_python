class player:

    def __init__(self, name, id, comm_module, position=None, team=None, game=None, cards=None):
        self.name = name
        self.id = id
        self.team = team
        self.cards = cards
        self.position = position
        self.game = game
        self.comm = comm_module

    def set_game(self, game):
        self.game = game

    def add_team(self, team):
        self.team = team

    def set_cards(self, cards):
        self.cards = cards

    def use_card(self, card):
        self.cards.remove(card)

    def send(self, command, data=None):
        self.comm.send_client(command, self.id, data=data)

    def reset(self):
        self.cards = []


class team:
    def __init__(self, name, position):
        self.name = name
        self.players = []
        self.score = 0
        self.game = None
        self.started = False
        self.cards = []
        self.position = position

    def set_game(self, game):
        self.game = game

    def increase_score(self, amount):
        self.score += amount

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)

    def reset(self):
        self.cards = []
        self.score = 0
        self.started = False



class game:
    def __init__(self, table_name):
        self.table_name = table_name
        self.players = [None] * 4
        self.teams = [None] * 2
        self.troef_chooser_pos = 0
        self.round_start_pos = 1
        self.round_play_offset = 0
        self.troef_choosen = False
        self.troef = None
        self.table_cards = []
        self.cards_played = 0
        self.viewers = []
        self.started = False
        self.removed_players = []

    def add_team(self, team):
        if self.teams[team.position] is None:
            self.teams[team.position] = team

            #players get placed directly in their playing order, add_team sets team as last by append
            for i in range(len(team.players)):
                self.players[team.position + 2*i] = team.players[i]
            return True
        else:
            print("SHOULD NOT HAPPEN, team added when exist")
            return False

    def get_team(self, name):
        for team in self.teams:
            if team is not None and team.name == name:
                return team
        return None

    def add_player(self, player):
        if self.players[player.position] is None:
            self.players[player.position] = player
            return True
        else:
            print("SHOULD NOT HAPPEN, player added when exist")
            return False

    def add_viewer(self, viewer):
        self.viewers.append(viewer)

    def __len__(self):
        amount = 0
        for player in self.players:
            amount += player is not None
        return amount

    def set_default_indices(self):
        self.round_play_offset = 0
        self.round_start_pos = 1

    def remove_viewer(self, viewer):
        self.viewers.remove(viewer)

    def remove_player(self, this_player):
        this_team = None
        for team in self.teams:
            if team is not None:
                for player in team.players:
                    if player is not None and player == this_player:
                        this_team = team

        index_team = this_team.players.index(this_player)
        this_team.players[index_team] = None

        index_game = self.players.index(this_player)
        self.players[index_game] = None

        self.removed_players.append(this_player)

    def reset(self):
        self.troef_chooser_pos = 0
        self.round_start_pos = 1
        self.round_play_offset = 0
        self.troef_choosen = False
        self.troef = None
        self.table_cards = []
        self.cards_played = 0
        self.viewers = []
        self.started = False
        self.removed_players = []

        for team in self.teams:
            if team is not None:
                team.reset()
                for player in team.players:
                    if player is not None:
                        player.reset()



class viewer:
    def __init__(self, id, comm_module):
        self.id = id
        self.comm = comm_module
        self.game = None

    def send(self, command, data=None):
        self.comm.send_client(command, self.id, data=data)

    def set_game(self, game):
        self.game = game