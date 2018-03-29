
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
        self.initialise_commlayer()
        self.valuedict = {"10": 5, "A": 4, "K": 3, "Q": 2, "J": 1, "9": 0, "8": 0, "7": 0}
        self.comparevalue = {"10": 7, "A": 6, "K": 5, "Q": 4, "J": 3, "9": 2, "8": 1, "7": 0}


    def initialise_commlayer(self):
        self.commlayer.add_engine_function("add_player", self.add_player)
        self.commlayer.add_engine_function("answer_troef", self.receive_troef)
        self.commlayer.add_engine_function("answer_card", self.receive_card)

    def start_play(self, game):
        player_cards = cards.getCards({"min": "7", "split_stack": 4, "shuffle": True})
        team_names = [team.name for team in game.teams]
        for i in range(4):
            game.players[i].set_cards(player_cards[i])
            self.commlayer.send_client("set_game_info", game.players[i].id, {"cards": player_cards[i], "teams": team_names})

        game.set_default_indices()
        self.play_round(game)

    def play_round(self, game):

        if game.troef_choosen:
            game.troef_choosen = False
            game.troef_chooser_pos = (game.troef_chooser_pos + 1) % 4
            game.round_start_pos = (game.troef_chooser_pos + 1) % 4
            game.troef = None

            score = 0
            for card in game.teams[0].cards:
                score += self.valuedict(card[1:])

            if score < 30:
                game.teams[1].score = 30 - score
            else:
                game.teams[0].score = score - 30

            for team in game.teams:
                if team.score > manillen_const.score_end:
                    self.end_game(game)
        troef_choser = game.players[game.round_start_pos]
        self.commlayer.send_client("choose_troef", troef_choser.id)

    def play_cards(self, game):
        if game.round_play_offset == 5:
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
                    elif game.table_cards[i][0] == starting_suit and self.comparevalue[game.table_cards[i][1:]] > self.comparevalue[game.table_cards[winning_index][1:]]:
                        winning_index = i
            print("engine: These cards were played: " + str(game.table_cards) + " and " + str(game.table_cards[winning_index]) + " won")

            game.round_start_pos = (game.round_start_pos + winning_index)%4
            game.players[game.round_start_pos].team.cards.extend(game.table_cards)
            game.table_cards = []
            game.round_play_offset = 0
            game.cards_played += 1

        if game.cards_played == 8:
            self.play_round(game)

        else:
            print("engine: sended play_card to player")
            self.commlayer.send_client("play_card", game.players[(game.round_start_pos + game.round_play_offset)%4].id)

    def end_game(self, game):
        a =5

    def receive_card(self, id, data):
        print("engine: received card")
        #check if valid card and allowed to play
        this_game = self.id_set_games[id]
        this_player = self.id_set_player[id]

        card_from_player = data in this_player.cards
        should_be_index = this_game.players.index(this_player)
        current_index = (this_game.round_start_pos + this_game.round_play_offset)%4
        allowed = should_be_index == current_index

        if allowed and card_from_player and self.card_allowed(data, this_game, this_player):
            print("engine: card is valid")
            self.commlayer.send_client("valid_card", id)
            this_game.table_cards.append(data)
            for player in this_game.players:
                self.commlayer.send_client("new_table_card", player.id, {"card": data, "index": len(this_game.table_cards)-1})

            this_game.round_play_offset += 1
            self.play_cards(this_game)
        else:
            print("engine: card is NOT valid")
            self.commlayer.send_client("invalid_card", id)

    def card_allowed(self, card, game, player):
        if len(game.table_cards) == 0:
            return True
        else:
            starting_suit = game.table_cards[0][0]
            player_suit = card[0]

            player_has_suit = False
            player_has_troef = False

            player_max_troef = None
            player_max_suit = None

            for player_card in player.cards:
                if player_card[0] == starting_suit:
                    player_has_suit = True

                if player_card[0] == game.troef:
                    player_has_troef = True

                if player_card[0] == game.troef and (player_max_troef is None or self.comparevalue[player_card[1:]] > self.comparevalue[player_max_troef[1:]]):
                    player_max_troef = player_card

                if player_card[0] == starting_suit and (player_max_suit is None or self.comparevalue[player_card[1:]] > self.comparevalue[player_max_suit[1:]]):
                    player_max_suit = player_card

            if starting_suit != player_suit and player_has_suit:
                return False


            # from here the player should not have a card that follows the staring suit
            # if he has a troef he should buy the card

            # check current team owner
            your_team = game.round_play_offset%2
            # get all troef on table
            max_troef_index = None
            all_troef = []
            max_suit_index = None
            all_suits = []

            # find index of highest troef card on the table and the index of the highest starting suit
            for i in range(len(game.table_cards)):
                if game.table_cards[i][0] == game.troef:
                    if max_troef_index is None or self.comparevalue[game.table_cards[i][1:]] > self.comparevalue[game.table_cards[max_troef_index][1:]]:
                        max_troef_index = i
                    all_troef.append(game.table_cards[i])

                if game.table_cards[i][0] == starting_suit:
                    if max_suit_index is None or self.comparevalue[game.table_cards[i][1:]] > self.comparevalue[game.table_cards[max_suit_index][1:]]:
                        max_troef_index = i
                    all_suits.append(game.table_cards[i])

            # check if there's a troef on the table
            if max_troef_index is not None:
                # your team currently has the hand, should not buy
                if max_troef_index%2 == your_team:
                    return True
                else:
                    # check if you have higher troef
                    higher_troefs = []
                    for player_card in player.cards:
                        if player_card[0] == game.troef and self.comparevalue[player_card[1:]] > self.comparevalue[game.table_cards[max_troef_index][1:]]:
                            higher_troefs.append(player_card)

                    # player has no troef that are higher, so allowed to play anything
                    if len(higher_troefs) == 0:
                        return True
                    else:
                        return card in higher_troefs
            elif max_suit_index is not None:
                if max_suit_index%2 == your_team:
                    return True
                else:
                    if player_has_suit:
                        # player should go higher then other team if possible
                        higher_suits = []
                        for player_card in player.cards:
                            if player_card[0] == starting_suit and self.comparevalue[player_card[1:]] > self.comparevalue[game.table_cards[max_suit_index][1:]]:
                                higher_suits.append(player_card)
                        if len(higher_suits) == 0:
                            return True
                        else:
                            return card in higher_suits
                    else:
                        # player should use troef is he has it
                        # player has troef, but doesn't use it
                        if player_has_troef and not card[0] == game.troef:
                            return False
            return True


    def receive_troef(self, id, data):
        #check if players card and allowed to choose troef
        this_game = self.id_set_games[id]
        this_player = self.id_set_player[id]

        card_from_player = data in this_player.cards
        allowed = not this_game.troef_choosen and this_game.players.index(this_player) == this_game.troef_chooser_pos

        if card_from_player and allowed:
            for player in this_game.players:
                self.commlayer.send_client("send_troef", player.id, data[0])
            this_game.troef_choosen = True
            this_game.troef = data[0]
            self.play_cards(this_game)
        else:
            self.commlayer.send_client("invalid_troef", id)

    def add_player(self, id, data):
        table_name = data["table_name"]
        team_name = data["team_name"]
        position = data["table_location"]
        player_name = data["player_name"]

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
        self.id_set_player[id] = this_player
        this_game.add_player(this_player)

        if len(this_game) == 4:
            self.start_play(this_game)

        self.commlayer.send_client("wait_other_players", id)

        return id



