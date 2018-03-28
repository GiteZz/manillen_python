
from manillen_classes import player, team, game

import manillen_const
import cards


class engine:
    def __init__(self, commlayer, testing=False):
        print("created engine")
        self.game_set = {}
        self.id_set_games = {}
        self.id_set_player = {}
        self.game_list = []
        self.testing = testing
        self.commlayer = commlayer

    def start_play(self, game):
        player_cards = cards.getCards({"min": "7", "split_stack": 4, "shuffle": True})
        team_names = [team.name for team in game.teams]
        for i in range(4):
            game.players[i].set_cards(player_cards[i])
            self.commlayer.set_game_info(game.players[i].id, {"cards": player_cards[i], "teams": team_names})

        game.set_default_indices()
        self.play_round(game)

    def play_round(self, game):
        for team in game.teams:
            if team.score > manillen_const.score_end:
                self.end_game(game)
        troef_choser = game.players[game.round_start_pos]
        self.commlayer.choose_troef(troef_choser.id)


    def end_game(self, game):
        a =5

    def add_player(self, player_name, team_name, table_name, position, id):
        this_player = player(player_name, id, position=int(position))
        if table_name in self.game_set:
            this_game = self.game_set[table_name]
        else:
            this_game = game(table_name)
            self.game_set[table_name] = this_game

        this_player.set_game(this_game)

        this_team = this_game.get_team(team_name)
        # team doesn't exist
        if this_team is None:
            this_team = team(team_name)
            this_game.add_team(this_team)
            this_team.set_game(this_game)

        this_team.add_player(this_player)
        this_player.add_team(this_team)
        self.id_set_games[id] = this_game
        this_game.add_player(this_player)

        if len(this_game) == 4:
            self.start_play(this_game)

        self.commlayer.wait_other_players(id)

        return id



