import random

#function gives cards based on options
#min: defines minimum card, this card is still included
#max: same as min
#allowable_suits: give suits that are allowed, expects array, if not defined all 4 are use
#remove_suits: start with the standard 4/ allowed suits and remove some, array or single el
def getCards(options=None):
    suits = ['H','D','C','S']
    symbols = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]



    card_array = []

    if options == None:
        for sut in range(0,len(suits)):
            for sym in range(0,len(symbols)):
                card_array.append(suits[sut] + symbols[sym])
        return card_array

    else:
        #min card is 2 because Ace gets seen as 14
        min = symbols[0]
        if "min" in options:
            min = options['min']

        #min is included
        symbols = symbols[symbols.index(min):]

        #Ace is 14
        max = symbols[len(symbols) - 1]
        if "max" in options:
            max = options['max']

        symbols = symbols[:symbols.index(max)+1]

        if "allowable_suits" in options:
            suits = options["allowable_suits"]

        if "remove_suits" in options:
            if (type(options["add_symbols"]) is list):
                for i in range(len(options["remove_suits"])):
                    suits.remove(options["remove_suits"][i])
            elif ((type(options["add_symbols"]) is int) or (type(options["add_symbols"]) is str)):
                suits.remove(options["remove_suits"])

        if "add_symbols" in options:
            if(type(options["add_symbols"]) is list):
                for i in range(len(options["add_symbols"])):
                    if str(options["add_symbols"][i]) not in symbols:
                        symbols.append(str(options["add_symbols"][i]))
            elif((type(options["add_symbols"]) is int) or (type(options["add_symbols"]) is str)):
                if str(options["add_symbols"]) not in symbols:
                    symbols.append(str(options["add_symbols"]))

        if "remove_symbols" in options:
            if (type(options["remove_symbols"]) is list):
                for i in range(len(options["remove_symbols"])):
                    if str(options["remove_symbols"][i]) in symbols:
                        symbols.remove(str(options["remove_symbols"][i]))
            elif ((type(options["remove_symbols"]) is int) or (type(options["remove_symbols"]) is str)):
                if str(options["remove_symbols"]) in symbols:
                    symbols.remove(str(options["remove_symbols"]))

        for sut in range(0,len(suits)):
            for sym in range(0,len(symbols)):
                card_array.append(suits[sut] + symbols[sym])

        if "remove_cards" in options:
            if (type(options["remove_cards"]) is list):
                for i in range(len(options["remove_cards"])):
                    if str(options["remove_cards"][i]) in card_array:
                        card_array.remove(str(options["remove_cards"][i]))
            elif ((type(options["remove_cards"]) is int) or (type(options["remove_cards"]) is str)):
                if str(options["remove_cards"]) in card_array:
                    card_array.remove(str(options["remove_cards"]))

        if "add_cards" in options:
            if (type(options["add_cards"]) is list):
                for i in range(len(options["add_cards"])):
                    if str(options["add_cards"][i]) in card_array:
                        card_array.append(str(options["remove_cards"][i]))
            elif ((type(options["add_cards"]) is int) or (type(options["add_cards"]) is str)):
                if str(options["add_cards"]) in card_array:
                    card_array.append(str(options["add_cards"]))

        if "shuffle" in options:
            if options["shuffle"]:
                random.shuffle(card_array)

        if "split_stack" in options:
            amount = options["split_stack"]
            card_array = split_stack(card_array, amount)

        return card_array

#first arrays will have 1 element more if cards%amount != 0
def split_stack(card_list, amount):
    base_size = len(card_list)//amount
    return_list = []
    for i in range(amount):
        return_list.append(card_list[base_size*i:base_size*(i+1)])
    for i in range(len(card_list)-base_size*amount):
        return_list[i].append(card_list[base_size*amount + i])
    return return_list


#(mul_suit*add_sym + mul_sym*add_suit)*mul_tot + add_tot
#not all cards should be defined in the sets
def card_value(card,
               multiplicative_suits=None, addative_suits=None,
               multiplicative_symbols=None, addative_symbols=None,
               multiplicative_total=None, addative_total=None):
    suit = card[0]
    symbol = card[1:]
    total = 0

    try:
        total += addative_suits[suit] * multiplicative_symbols[symbol]
    except:
        try:
            total += addative_suits[suit]
        except:
            pass

    try:
        total += multiplicative_suits[suit] * addative_symbols[symbol]
    except:
        try:
            total += addative_symbols[symbol]
        except:
            pass

    try:
        total *= multiplicative_total
    except:
        pass

    try:
        total += addative_total
    except:
        pass

    return total



def symbol_to_number(symbol):
    try:
        value = int(symbol)
        return value
    except ValueError:
        if(symbol == "J"):
            return 11
        if (symbol == "Q"):
            return 12
        if (symbol == "K"):
            return 13
        if (symbol == "A"):
            return 14
        return -1

def suit_to_index(suit):
    if (suit == "H"):
        return 0
    if (suit == "D"):
        return 1
    if (suit == "C"):
        return 2
    if (suit == "S"):
        return 3
    return -1