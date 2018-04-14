
from manillen_classes import man_player, man_team, man_game, viewer

import manillen_const
import cards
import time
import logging
from manillen_game_logic import card_allowed

class engine:
    def __init__(self, test_module=None):
        logging.basicConfig(level=logging.INFO)
        self.logger_engine = logging.getLogger('engine_working')
        self.logger_game = logging.getLogger('engine_game')

        self.handler = logging.FileHandler('logs/games.log')
        self.handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s ,%(message)s')
        self.handler.setFormatter(formatter)

        self.logger_game.addHandler(self.handler)

        self.logger_engine.info("created engine")

        self.game_set = {}
        self.id_set_games = {}
        self.id_set_player = {}
        self.id_set_viewer = {}

        self.valuedict = {"10": 5, "A": 4, "K": 3, "Q": 2, "J": 1, "9": 0, "8": 0, "7": 0}
        self.comparevalue = {"10": 7, "A": 6, "K": 5, "Q": 4, "J": 3, "9": 2, "8": 1, "7": 0}

        self.function_dict = {"add_player": self.add_player, "answer_troef": self.receive_troef, "answer_card": self.receive_card, "add_viewer": self.add_viewer, "disconnect": self.remove_subscriber, "reset_game": self.reset_game, "keep_waiting" : self.keep_waiting}

        self.test_mod = test_module


    def get_functions(self):
        return self.function_dict

    def restart_play(self, game):
        self.send_all_players("restarted_game", game)
        if game.troef_choosen:
            self.play_cards(game)
        else:
            game.players[game.troef_chooser_pos].send("choose_troef")

    def start_play(self, game):
        if not game.started:
            game.started = True

            team_names = [team.name for team in game.teams]

            game.set_default_indices()

            self.send_all_players("set_teams", game, team_names)

            self.play_round(game)
        else:
            self.logger_engine.error("game should be restarted, not started")

    def play_round(self, game):

        self.distribute_cards(game)

        if game.troef_choosen:
            game.troef_choosen = False
            game.troef_chooser_pos = (game.troef_chooser_pos + 1) % 4
            game.round_start_pos = (game.troef_chooser_pos + 1) % 4
            game.troef = None
            game.cards_played = 0

            score = 0
            for card in game.teams[0].cards:
                score += self.valuedict[card[1:]]

            for team in game.teams:
                team.reset_round()

            if score < 30:
                game.teams[1].add_points(30 - score)
            else:
                game.teams[0].add_points(score - 30)

            self.send_all_players("update_score", game, data={"team0":game.teams[0].prev_scores,"team1":game.teams[1].prev_scores})

            for team in game.teams:
                if team.score > manillen_const.score_end:
                    self.end_game(game)
        troef_chooser = game.players[game.troef_chooser_pos]
        self.logger_engine.info("  " + troef_chooser.name + " was asked for troef")
        troef_chooser.send("choose_troef")

    def distribute_cards(self, game):
        player_cards = cards.getCards({"min": "7", "split_stack": 4, "shuffle": True, "sorted": True})

        for i in range(4):
            game.players[i].set_cards(player_cards[i])

            game.players[i].send("receive_play_cards", data=player_cards[i])

    def play_cards(self, game):
        if game.round_play_offset == 4:
            # see to which team the cards should go
            troef_active = False
            winning_index = 0
            starting_suit = game.table_cards[0][0]
            for i in range(len(game.table_cards)):
                if troef_active:
                    if self.comparevalue[game.table_cards[i][1:]] > self.comparevalue[game.table_cards[winning_index][1:]] and game.table_cards[i][0] == game.troef:
                        winning_index = i
                else:
                    if game.table_cards[i][0] == game.troef:
                        winning_index = i
                        troef_active = True
                    elif game.table_cards[i][0] == starting_suit \
                            and self.comparevalue[game.table_cards[i][1:]] > self.comparevalue[game.table_cards[winning_index][1:]]:
                        winning_index = i
            self.logger_engine.info(" These cards were played: " + str(game.table_cards)
                                    + " and " + str(game.table_cards[winning_index])
                                    + " won, this is player: " + game.players[(game.round_start_pos + winning_index)%4].name)

            game.round_start_pos = (game.round_start_pos + winning_index)%4
            game.players[game.round_start_pos].team.cards.extend(game.table_cards)
            game.table_cards = []
            game.round_play_offset = 0
            game.cards_played += 1

            self.send_all_players("clear_board", game)

        if game.cards_played == 8:
            self.play_round(game)

        else:
            current_player = game.players[(game.round_start_pos + game.round_play_offset) % 4]
            self.logger_engine.info("  " + current_player.name + " was asked to play card")
            current_player.send("play_card")

    def end_game(self, game):
        a = 5

    def send_all_players(self, command, game, data=None, viewer=True):
        for player in game.players:
            if player is not None:
                player.send(command, data=data)

        if viewer:
            for viewer in game.viewers:
                viewer.send(command, data)

    def receive_card(self, id, card):
        # check if valid card and allowed to play
        this_game = self.id_set_games[id]
        this_player = self.id_set_player[id]
        self.logger_engine.info(" received card from: " + this_player.name + " from team: " + this_player.team.name)

        card_from_player = card in this_player.cards
        should_be_index = this_game.players.index(this_player)
        current_index = (this_game.round_start_pos + this_game.round_play_offset)%4
        allowed = should_be_index == current_index

        if allowed and card_from_player and card_allowed(card, this_game.table_cards, this_player.cards, this_game.troef):
            self.logger_engine.info(" card is valid")
            this_player.send("valid_card")
            this_game.table_cards.append(card)

            self.send_all_players("new_table_card", this_game, data= {"card": card, "index": len(this_game.table_cards) - 1})

            this_game.round_play_offset += 1
            this_player.cards.remove(card)

            self.logger_game.info("card;" + str(this_player.position) + ";" + card)

            self.play_cards(this_game)
        else:
            self.logger_engine.info(" card is NOT valid")
            this_player.send("invalid_card")

    def receive_troef(self, id, data):
        # check if players card and allowed to choose troef
        this_game = self.id_set_games[id]
        this_player = self.id_set_player[id]

        # allow for sending full card and only the char
        for card in this_player.cards:
            if data[0] == card[0]:
                card_from_player = True
                break

        allowed = not this_game.troef_choosen and this_game.players.index(this_player) == this_game.troef_chooser_pos

        if card_from_player and allowed:
            self.send_all_players("send_troef", this_game, data=data[0])

            this_game.troef_choosen = True
            this_game.troef = data[0]

            self.logger_game.info("troef;" + str(this_player.position) + ";" + data)

            self.play_cards(this_game)
        else:
            this_player.send("invalid_troef")

    def add_viewer(self, id, data):
        table_name = data["table_name"]
        comm_module = data["comm_module"]

        this_viewer = viewer(id, comm_module)

        if table_name in self.game_set:
            this_game = self.game_set[table_name]
        else:
            this_game = man_game(table_name)
            self.game_set[table_name] = this_game

        this_game.add_viewer(this_viewer)
        self.id_set_viewer[id] = this_viewer
        this_viewer.set_game(this_game)
        this_viewer.send("allow_viewing")

    def add_player(self, id, data):
        table_name = data["game_name"]
        team_name = data["team_name"]
        position_in_team = int(data["location_in_team"])
        position_of_team = int(data["location_of_team"])
        position = position_of_team + 2 * position_in_team
        player_name = data["player_name"]
        comm_module = data["comm_module"]

        if table_name in self.game_set:
            this_game = self.game_set[table_name]
        else:
            this_game = man_game(table_name)
            self.game_set[table_name] = this_game

        if this_game.get_state("rejoin_waiting") or this_game.get_state("wait_decision"):
            this_player = this_game.get_deleted_player(player_name)
            if this_player is not None:
                this_game.reinstate_player(this_player)
                this_player.id = id
                self.id_set_games[id] = this_game
                self.id_set_player[id] = this_player

                team_names = [team.name for team in this_game.teams]

                this_player.send("set_teams", data=team_names)

                this_player.send("receive_play_cards", data=this_player.cards)

                this_player.send("wait_other_players")

                if len(this_game) == 4:
                    self.restart_play(this_game)
        else:
            this_player = man_player(player_name, id, comm_module, position=position)

            this_player.set_game(this_game)

            this_team = this_game.get_team(team_name)
            # team doesn't exist
            if this_team is None:
                this_team = man_team(team_name, position_of_team)
                this_game.add_team(this_team)
                this_team.set_game(this_game)

            this_team.add_player(this_player)
            this_player.add_team(this_team)
            self.id_set_games[id] = this_game
            self.id_set_player[id] = this_player
            this_game.add_player(this_player)

            if len(this_game) == 4:
                if not this_game.started:
                    self.start_play(this_game)


            this_player.send("wait_other_players")

        return id

    def reset_game(self, id):
        this_game = self.id_set_games[id]
        this_game.reset()
        this_game.set_state("not_started")

    def keep_waiting(self, id):
        this_game = self.id_set_games[id]
        this_game.set_state("rejoin_waiting")

    # can be player of viewer
    def remove_subscriber(self, id):
        self.logger_game.info("  player has left game")
        if id in self.id_set_viewer:
            this_viewer = self.id_set_viewer[id]
            this_game = this_viewer.game

            this_game.remove_viewer(this_viewer)
            self.id_set_viewer.pop(id)
        elif id in self.id_set_player:
            this_player = self.id_set_player[id]
            this_game = this_player.game

            this_game.remove_player(this_player)
            self.id_set_player.pop(id)
            self.id_set_games.pop(id)
            self.return_to_test_set(this_player)
            if this_game.started:
                self.send_all_players("reset_game_lost_player", this_game, viewer=False)
                this_game.set_state("wait_decision")

    def return_to_test_set(self, player):
        if self.test_mod is not None:
            table_name = player.game.name
            team_name = player.team.name
            player_name = player.name
            team_location = player.team.position
            in_team_location = player.position // 2

            self.test_mod.return_vector({'game_name': table_name, 'team_name': team_name,
             'player_name': player_name, 'team_location_input': team_location,
             "team_player_location_input": in_team_location})


    def create_player(self, name, id, cards, position, comm):
        return man_player(name, id, comm, position=position, cards=cards)

    def create_team(self, name, position, players):
        this_team = man_team(name, position, players=players)

        for player in players:
            player.set_team(this_team)
        return this_team

    def create_game(self, table_name, teams):
        this_game = man_team(table_name)

        for team in teams:
            this_game.add_team(team)
        return this_game


if __name__ == "__main__":
    print("========== testing engine ==========")
    en = engine()
    print("========== card allowed ==========")
    # card, table cards, player_cards, troef
    # player should play K10
    print(en.card_allowed("KJ", ["K8", "KQ"], ["K10", "H9", "KJ"], 'H') == False)
    # player should buy
    print(en.card_allowed("S10", ["K8", "KQ"], ["S10", "H9", "SJ"], 'H') == False)
    #valid play
    print(en.card_allowed("K10", ["K8", "KQ"], ["S10", "K10", "KJ"], 'H') == True)
    #valid play
    print(en.card_allowed("S10", ["KQ", "K8"], ["S10", "H9", "SJ"], 'H') == True)



