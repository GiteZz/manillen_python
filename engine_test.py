from collections import defaultdict
from manillen_game_logic import card_allowed

class test_comm_module:
    def __init__(self, id, engine_functions=None):
        self.a = 5
        self.engine_functions = engine_functions
        self.troef = None
        self.cards = None
        self.table_cards = []
        self.id = id
        self.command_dict = {}
        self.setup_command_dict()

    def setup_command_dict(self):
        self.command_dict["restarted_game"] = self.restarted_game
        self.command_dict["choose_troef"] = self.choose_troef
        self.command_dict["receive_play_cards"] = self.receive_play_cards
        self.command_dict["set_teams"] = self.set_teams
        self.command_dict["clear_board"] = self.clear_board
        self.command_dict["play_card"] = self.play_card
        self.command_dict["new_table_card"] = self.new_table_card
        self.command_dict["valid_card"] = self.valid_card
        self.command_dict["invalid_card"] = self.invalid_card
        self.command_dict["send_troef"] = self.send_troef
        self.command_dict["invalid_troef"] = self.invalid_troef
        self.command_dict["allow_viewing"] = self.allow_viewing
        self.command_dict["wait_other_players"] = self.wait_other_players
        self.command_dict["reset_game_lost_player"] = self.reset_game_lost_player

    def send_client(self, command, id, data=None):
        if command in self.command_dict:
            if data is None:
                self.command_dict[command]()
            else:
                self.command_dict[command](data)

    def add_engine_function_dict(self, engine_dict):
        self.engine_functions = engine_dict

    def send_engine(self, command, id, data=None):
        if command in self.engine_functions:
            if data is not None:
                self.engine_functions[command](id, data)
            else:
                self.engine_functions[command](id)

    def restarted_game(self):
        pass

    def choose_troef(self):
        amount_dict = {"S": 0, "H": 0, "D": 0, "C": 0}
        for card in self.cards:
            amount_dict[card[0]] += 1

        max_key = None
        for key in amount_dict:
            if max_key is None or amount_dict[key] > amount_dict[max_key]:
                max_key = key
        self.send_engine("answer_troef", self.id, data=max_key)


    def receive_play_cards(self, data):
        self.cards = data

    # gives player cards and team_names
    def set_teams(self, data):
        pass

    def clear_board(self):
        self.table_cards = []

    def play_card(self):
        cards_allowed = []
        for card in self.cards:
            if card_allowed(card, self.table_cards, self.cards, self.troef):
                cards_allowed.append(card)
        self.send_engine("answer_card", self.id, data=cards_allowed[0])

    def new_table_card(self, data):
        self.table_cards.append(data["card"])

    def valid_card(self):
        pass

    def invalid_card(self):
        print("ERROR: AI selected invalid card")

    def send_troef(self, data):
        self.troef = data

    def invalid_troef(self):
        print("ERROR: AI selected invalid troef")

    def allow_viewing(self):
        pass

    def wait_other_players(self):
        pass

    def reset_game_lost_player(self):
        pass

if __name__ == "__main__":
    pass