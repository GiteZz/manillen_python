class communication_module:
    def __init__(self):
        # engine functions
        self.answer_troef = None
        self.answer_card = None
        self.add_player = None

        # comm functions
        self.choose_troef = None
        self.play_card = None
        self.send_game_info = None
        self.wait_other_players = None