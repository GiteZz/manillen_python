class communication_module:
    def __init__(self, socketio_server):
        # engine functions
        self.engine_functions = {}
        self.sio = socketio_server

    def send_client(self, command, id, data=None):
        if data is None:
            self.sio.emit(command, room=id)
        else:
            self.sio.emit(command, data, room=id)

    def send_engine(self, command, id, data):
        self.engine_functions[command](id, data)

    def add_engine_function(self, command, function):
        self.engine_functions[command] = function

