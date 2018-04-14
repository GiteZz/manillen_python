class test_class:
    def __init__(self, name):
        self.test_vectors = []
        
        with open(name) as f:
            content = f.readlines()

        for i in range(len(content)):
            if len(content[i]) > 0 and content[i][0] != '#':
                self.test_vectors.append(content[i].split(','))

    def give_test_set(self, comm_module=None):
        if len(self.test_vectors) > 0:
            vector = self.test_vectors.pop(0)
            ret_dict = {'game_name': vector[0], 'team_name':vector[1],
                    'player_name': vector[2], 'location_of_team': vector[3][0],
                    "location_in_team": vector[4][0]}
            if comm_module is not None:
                ret_dict["comm_module"] = comm_module
            return ret_dict
        else:
            print("ERROR, no testvector left")
            return None

    def return_vector(self, vector):
        self.test_vectors.insert(0, vector)
