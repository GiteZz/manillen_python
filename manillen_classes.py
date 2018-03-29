class player:

    def __init__(self, name, id, position=None, team=None, game=None, cards=None):
        self.name = name
        self.id = id
        self.team = team
        self.cards = cards
        self.position = position
        self.game = game

    def set_game(self, game):
        self.game = game

    def add_team(self, team):
        self.team = team

    def set_cards(self, cards):
        self.cards = cards

    def use_card(self, card):
        self.cards.remove(card)


class team:
    def __init__(self, name):
        self.name = name
        self.players = []
        self.score = 0
        self.game = None
        self.started = False
        self.cards = []

    def set_game(self, game):
        self.game = game

    def increase_score(self, amount):
        self.score += amount

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)



class game:
    def __init__(self, table_name):
        self.table_name = table_name
        self.players = [None] * 4
        self.teams = []
        self.troef_chooser_pos = 0
        self.round_start_pos = 1
        self.round_play_offset = 0
        self.troef_choosen = False
        self.troef = None
        self.table_cards = []
        self.cards_played = 0

    def add_team(self, team):
        self.teams.append(team)
        #players get placed directly in their playing order, add_team sets team as last by append
        for i in range(len(team.players)):
            self.players[len(self.teams) - 1 + i] = team.players[i]

    def update_team(self, team):
        index = self.teams.index(team)
        for player in team.players:
            self.players[player.position] = player

    def team_exists(self, team_name):
        for team in self.teams:
            if team.name == team_name:
                return team

        return None

    def get_team(self, name):
        for team in self.teams:
            if team.name == name:
                return team
        return None

    def add_player(self, player):
        self.players[player.position] = player

    def __len__(self):
        amount = 0
        for player in self.players:
            amount += player is not None
        return amount

    def set_default_indices(self):
        self.round_play_offset = 1
        self.round_start_pos = 0