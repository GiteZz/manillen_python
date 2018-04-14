def card_allowed(card, table_cards, player_cards, troef):
    if len(table_cards) == 0:
        return True
    else:
        comparevalue = {"10": 7, "A": 6, "K": 5, "Q": 4, "J": 3, "9": 2, "8": 1, "7":0}

        starting_suit = table_cards[0][0]
        player_suit = card[0]

        player_has_suit = False
        player_has_troef = False

        player_max_troef = None
        player_max_suit = None

        for player_card in player_cards:
            if player_card[0] == starting_suit:
                player_has_suit = True

            if player_card[0] == troef:
                player_has_troef = True

            if player_card[0] == troef and (player_max_troef is None or comparevalue[player_card[1:]] > comparevalue[player_max_troef[1:]]):
                player_max_troef = player_card

            if player_card[0] == starting_suit \
                    and (player_max_suit is None
                    or comparevalue[player_card[1:]] > comparevalue[player_max_suit[1:]]):
                player_max_suit = player_card

        if starting_suit != player_suit and player_has_suit:
            return False

        # from here the player should not have a card that follows the staring suit
        # if he has a troef he should buy the card

        # check current team owner
        your_team = len(table_cards) % 2
        # get all troef on table
        max_troef_index = None
        all_troef = []
        max_suit_index = None
        all_suits = []

        # find index of highest troef card on the table and the index of the highest starting suit
        for i in range(len(table_cards)):
            if table_cards[i][0] == troef:
                if max_troef_index is None \
                        or comparevalue[table_cards[i][1:]] > comparevalue[table_cards[max_troef_index][1:]]:
                    max_troef_index = i
                all_troef.append(table_cards[i])

            if table_cards[i][0] == starting_suit:
                if max_suit_index is None \
                        or comparevalue[table_cards[i][1:]] > comparevalue[table_cards[max_suit_index][1:]]:
                    max_suit_index = i
                all_suits.append(table_cards[i])
        # check if there's a troef on the table
        if max_troef_index is not None and max_suit_index is None:
            # your team currently has the hand, should not buy
            if max_troef_index % 2 == your_team:
                return True
            else:
                # check if you have higher troef
                higher_troefs = []
                for player_card in player_cards:
                    if player_card[0] == troef \
                            and comparevalue[player_card[1:]] > comparevalue[table_cards[max_troef_index][1:]]:
                        higher_troefs.append(player_card)

                # player has no troef that are higher, so allowed to play anything
                if len(higher_troefs) == 0:
                    return True
                else:
                    return card in higher_troefs
        if max_suit_index is not None and max_troef_index is None:
            if max_suit_index % 2 == your_team:
                return True
            else:
                if player_has_suit:
                    # player should go higher then other team if possible
                    higher_suits = []
                    for player_card in player_cards:
                        if player_card[0] == starting_suit and comparevalue[player_card[1:]] > comparevalue[table_cards[max_suit_index][1:]]:
                            higher_suits.append(player_card)
                    if len(higher_suits) == 0:
                        return True
                    else:
                        return card in higher_suits
                else:
                    # player should use troef is he has it
                    # player has troef, but doesn't use it
                    if player_has_troef and not card[0] == troef:
                        return False
        return True