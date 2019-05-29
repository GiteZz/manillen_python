# Manillen

This is a further advancement for my previous manillen game written in nodejs. This one is writter in python. Game logic is done and the game should be looking good on desktop. AI agents can be easily implemented by creating a custom communication module and implementing the desired functions.

Communication module should implement these functions on the client side:
* restarted_game
* choose_troef
* set_game_info
* clear_board
* play_card
* valid_card
* new_table_card
* invalid_card
* send_troef
* invalid_troef
* allow_viewing
* wait_other_players
* reset_game_lost_player
	
These should be read with a send_client(command, id, data=...)
You can give command to server with send_engine(command, id, data=...)

![Alt text](login.png?raw=true "Login screen")

![Alt text](play.png?raw=true "Play screen")
