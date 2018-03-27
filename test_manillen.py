class test_class:
    games = []
    teams = []
    players = []
    index = 0

    def __init__(self, name):
        with open(name) as f:
            content = f.readlines()


        for i in range(len(content)):
            if len(content[i]) > 2 and content[i][0] == '\t':
                if content[i][1] == '\t':
                    # player name
                    self.players.append(content[i].replace('\t','').replace('\n',''))
                else:
                    # team name
                    self.teams.append(content[i].replace('\t', '').replace('\n', ''))
            elif len(content[i]) > 0:
                # table name
                self.games.append(content[i].replace('\t', '').replace('\n', ''))

    def give_test_set(self):
        game = self.games[self.index//4]
        team = self.teams[self.index//2]
        player = self.players[self.index]
        position = self.index%4
        if position == 1:
            position = 2
        elif position == 2:
            position = 1
        self.index += 1
        return {'team_name':team, 'game_name': game, 'player_name':player, 'position': str(position)}


