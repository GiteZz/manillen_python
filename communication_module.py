class communication_module_sio:
    def __init__(self, socketio_server):
        # engine functions
        self.engine_functions = {}
        self.sio = socketio_server

    def send_client(self, command, id, data=None):
        if data is None:
            self.sio.emit(command, room=id)
        else:
            self.sio.emit(command, data, room=id)

    def send_engine(self, command, id, data=None):
        if data is not None:
            self.engine_functions[command](id, data)
        else:
            self.engine_functions[command](id)


    def add_engine_function(self, command, function):
        self.engine_functions[command] = function

    def add_engine_function_dict(self, engine_dict):
        self.engine_functions = engine_dict



