Communication module should implement these functions on the client side:
	-restarted_game
	-choose_troef
	-set_game_info
		Gives team names and player cards
	-clear_board
	-play_card
	-valid_card
	-new_table_card
	-invalid_card
	-send_troef
	-invalid_troef
	-allow_viewing
	-wait_other_players
	-reset_game_lost_player
	
These should be read with a send_client(command, id, data=...)
You can give command to server with send_engine(command, id, data=...)


TODO:
-Check if amount teams smaller then 2 and then create new team
-implement system to show small notifications to user (e.g. user joined, ...)
-red and black cards