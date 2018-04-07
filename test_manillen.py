class test_class:
    def __init__(self, name):
        self.test_vectors = []
        self.index = -1
        with open(name) as f:
            content = f.readlines()

        for i in range(len(content)):
            if len(content[i]) > 0 and content[i][0] != '#':
                self.test_vectors.append(content[i].split(','))

    def give_test_set(self):

        self.index += 1
        return {'game_name': self.test_vectors[self.index][0], 'team_name':self.test_vectors[self.index][1],
                'player_name':self.test_vectors[self.index][2], 'team_location_input': self.test_vectors[self.index][3][0],
                "team_player_location_input":self.test_vectors[self.index][4][0]}


