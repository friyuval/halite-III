#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("FRIYUVAL")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


""" <<<Game Loop>>> """
ship_status = {}
ship_priority = {}
ship_target = {}
radius = 1
drop_loc = Position(0, 0)
keep_spawn, make_drop = True, False
size = game.game_map.width
players = 0
for player in game.players:
    players += 1
if players == 2:
    dropoffs_num = 1
else:
    if size < 48:
        dropoffs_num = 0
    else:
        dropoffs_num = 1


def decide_next_move(position, options=(True, True, True, True, True)):
    # Find the cardinal around the given position with the most halite
    # Options variable indicates which moves are not allowed. index 0 - north, 1 - south, 2 - east, 3 west
    # and 4 - stay still.
    around = position.get_surrounding_cardinals()
    halite_around = []
    for i in around:
        halite_around.append(game_map[i].halite_amount)
    halite_around.append(game_map[position].halite_amount)
    # If the amount of halite in the existing location has more or equal to anywhere around - stay in this position.
    if options[4] and (halite_around[4] >= halite_around[0] or not options[0]) and (halite_around[4] >=
            halite_around[1] or not options[1]) and (halite_around[4] >= halite_around[2] or not options[2]) and \
            (halite_around[4] >= halite_around[3] or not options[3]) and halite_around[4] > 0:
        decision = 'o'
    elif options[0] and (halite_around[0] > halite_around[1] or not options[1]) and (halite_around[0] >
            halite_around[2] or not options[2]) and (halite_around[0] > halite_around[3] or not options[3]):
        decision = 'n'
    elif options[1] and (halite_around[1] > halite_around[2] or not options[2]) and (halite_around[1] >
            halite_around[3] or not options[3]):
        decision = 's'
    elif options[2] and (halite_around[2] > halite_around[3] or not options[3]):
        decision = 'e'
    elif options[3]:
        decision = 'w'
    # The only way to get to this part of the code is if all cells around have 0 halite
    elif options[2]:
        decision = 'e'
    elif options[1]:
        decision = 's'
    elif options[0]:
        decision = 'n'
    else:
        decision = 'o'
    return decision


def get_diractional_tuple(command):
    # Some of the functions do not work with string commands of movement, so this function turn a string into a tuple
    # which represents coordination
    if command == 'n':
        direction = (0, -1)
    elif command == 's':
        direction = (0, 1)
    elif command == 'e':
        direction = (1, 0)
    elif command == 'w':
        direction = (-1, 0)
    else:
        direction = (0, 0)
    return direction


def get_diractional_letter(command):
    # For convenience, this function turns commands (like Direction.north) to strings with similar meaning (like 'n')
    if command == Direction.North:
        direction = 'n'
    elif command == Direction.South:
        direction = 's'
    elif command == Direction.East:
        direction = 'e'
    elif command == Direction.West:
        direction = 'w'
    else:
        direction = 'o'
    return direction


def get_index(command):
    if command == 'n':
        return 0
    if command == 's':
        return 1
    if command == 'e':
        return 2
    if command == 'w':
        return 3
    return 4


def is_move_safe(target_move, id):
    global next_move, ship_priority
    if game_map[target_move].is_occupied and game_map[target_move].ship.owner != game.my_id and not \
            target_move == me.shipyard.position:
        return False
    try:
        p = ship_priority[id]
    except:
        p = 10
    check = True
    # Check against ships with lower priorities, or equal priorities that already sent moving commands.
    for ship in me.get_ships():
        if ship.id == id:
            check = False
            continue
        if ship_priority[ship.id] < p or (ship_priority[ship.id] == p and check):
            if target_move == game_map.normalize(ship.position.directional_offset(get_diractional_tuple((next_move[ship.id])))):
                return False
    return True


def find_new_exploring_move(position, id):
    options = [True, True, True, True, True]
    global next_move
    # Flag the move that did not pass is_move_safe test, also flag the move if it leads to the shipyard while the ship
    # is in exploring mode.
    if next_move[id] == 'n' or me.shipyard.position == game_map.normalize(position.directional_offset(get_diractional_tuple('n'))):
        options[0] = False
    elif next_move[id] == 's' or me.shipyard.position == game_map.normalize(position.directional_offset(get_diractional_tuple('s'))):
        options[1] = False
    elif next_move[id] == 'e' or me.shipyard.position == game_map.normalize(position.directional_offset(get_diractional_tuple('e'))):
        options[2] = False
    elif next_move[id] == 'w' or me.shipyard.position == game_map.normalize(position.directional_offset(get_diractional_tuple('w'))):
        options[3] = False
    while options[0] or options[1] or options[2] or options[3] or options[4]:
        new_move = decide_next_move(position, options)
        check = is_move_safe(game_map.normalize(position.directional_offset(get_diractional_tuple(new_move))), id)
        if check:
            return new_move
        else:
            options[get_index(new_move)] = False
    # If there is no other option - try to move to the shipyard.
    options = [True, True, True, True, True]
    while options[0] or options[1] or options[2] or options[3] or options[4]:
        new_move = decide_next_move(position, options)
        check = is_move_safe(game_map.normalize(position.directional_offset(get_diractional_tuple(new_move))), id)
        if check:
            return new_move
        else:
            options[get_index(new_move)] = False
    return 'o'


def find_new_way_home(position, id):
    options = [True, True, True, True, True]
    global next_move
    options[get_index(next_move[id])] = False
    try:
        decision = get_diractional_letter(game_map.get_unsafe_moves(position, me.shipyard.position)[1])
        check = is_move_safe(game_map.normalize(position.directional_offset(get_diractional_tuple(decision))), id)
        if check:
            return decision
        else:
            options[get_index(decision)] = False
    except:
        pass
    if is_move_safe(position, id):
        return 'o'
    if options[1] and is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
        return 's'
    if options[3] and is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
        return 'w'
    if options[0] and is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
        return 'n'
    return 'e'


def adjacent_to_basement(position):
    source = find_closest_basement(position)
    if game_map.calculate_distance(position, source) == 1:
            return True
    return False


def coming_back(position, id, radius):
    ship_target[id] = scan(position, radius)
    return go_to_target(position, id)


def scan(position, radius):
    x, y = position.x, position.y
    max_halite = -1
    max_location = Position(x, y)
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if game_map[game_map.normalize(Position(x+i, y+j))].halite_amount > max_halite:
                max_halite = game_map[game_map.normalize(Position(x+i, y+j))].halite_amount
                max_location = game_map.normalize(Position(x+i, y+j))
    return max_location


def go_to_target(position, id):
    # Send ship to the cell with the most amount of halite in the area. If the move(s) is not safe, send the ship to
    # the cell with the most amount of halite around it.
    global ship_target, next_move, collect_value
    temp = game_map.get_unsafe_moves(position, ship_target[id])
    if len(temp) == 0:
        if is_move_safe(position, id):
            return 'o'
        else:
            next_move[id] = 'o'
            return find_new_exploring_move(position, id)
    if len(temp) == 1:
        if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id):
            return get_diractional_letter(temp[0])
        else:
            next_move[id] = temp[0]
            return find_new_exploring_move(position, id)
    if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id) and \
            is_move_safe(game_map.normalize(position.directional_offset(temp[1])), id):
        if game_map[game_map.normalize(position.directional_offset(temp[0]))].halite_amount > game_map[
                game_map.normalize(position.directional_offset(temp[1]))].halite_amount:
            return get_diractional_letter(temp[0])
        return get_diractional_letter(temp[1])
    elif is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id):
        return get_diractional_letter(temp[0])
    elif is_move_safe(game_map.normalize(position.directional_offset(temp[1])), id):
        return get_diractional_letter(temp[1])
    next_move[id] = temp[0]
    return find_new_exploring_move(position, id)


def avg_halite():
    r = game_map.width
    c = game_map.height
    total = 0
    for i in range(r):
        for j in range(c):
            total += game_map[Position(i, j)].halite_amount
    return total / (r*c)


def halite_amount_around(position, radius):
    x, y = position.x, position.y
    total = 0
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            total += game_map[game_map.normalize(Position(x + i, y + j))].halite_amount
    return total


def find_drop_location(min_dis, max_dis):
    r = game_map.width
    c = game_map.height
    base_loc = me.shipyard.position
    max_amount = -1
    curr_loc = Position(0, 0)
    for i in range(r):
        for j in range(c):
            dis = game_map.calculate_distance(Position(i, j), base_loc)
            if dis >= min_dis and dis <= max_dis:
                temp = halite_amount_around(Position(i, j), 4)
                if temp > max_amount:
                    curr_loc = Position(i, j)
                    max_amount = temp
    return curr_loc


def find_closest_ship(position):
    min_dis = 100
    id = 0
    for ship in me.get_ships():
        dis = game_map.calculate_distance(ship.position, position)
        if dis < min_dis:
            min_dis = dis
            id = ship.id
    return id


def calculate_radius(position, avg_h, prev_radius):
    x, y = position.x, position.y
    radius = prev_radius
    total = 0
    while radius < 3:
        for i in range(-radius, radius + 1):
            if i == abs(radius):
                for j in range(-radius, radius + 1):
                    total += game_map[game_map.normalize(Position(x + i, y + j))].halite_amount
            else:
                total += game_map[game_map.normalize(Position(x + i, y - radius))].halite_amount
                total += game_map[game_map.normalize(Position(x + i, y + radius))].halite_amount
        total = total / (radius*8)
        if total >= max(avg_h / 2, 50):
            return radius
        radius += 1
    return radius


def find_closest_basement(position):
    location = me.shipyard.position
    min_dis = game_map.calculate_distance(position, location)
    for dropoff in me.get_dropoffs():
        temp = game_map.calculate_distance(position, dropoff.position)
        if temp <= min_dis:
            min_dis = temp
            location = dropoff.position
    return location


def is_in_basement(position):
    if position == me.shipyard.position:
        return True
    for dropoff in me.get_dropoffs():
        if position == dropoff.position:
            return True
    return False


while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    next_move = {}
    avg_h = avg_halite()
    collect_value = max(avg_h / 4 + game.turn_number / constants.MAX_TURNS * 20,
                        50 - game.turn_number / constants.MAX_TURNS * 25)
    if radius < 3:  # Sight radius of ships
        radius = calculate_radius(me.shipyard.position, avg_h, radius)
    if len(me.get_dropoffs()) == dropoffs_num:
        keep_spawn = True
        make_drop = False
    elif len(me.get_ships()) == 17:     # create first dropoff if the number of ships on the map is equal to 17
        keep_spawn = False
        make_drop = True
        drop_loc = find_drop_location(16, 20)
        id = find_closest_ship(drop_loc)
        ship_status[id] = "generating dropoff"
        ship_priority[id] = 5
    if constants.MAX_TURNS - game.turn_number <= 200:
        keep_spawn = False
    if make_drop:  # check that the assigned ship to become a dropoff is still exist
        try:
            check = me.get_ship(id)
        except:
            drop_loc = find_drop_location(16, 20)
            id = find_closest_ship(drop_loc)
            ship_status[id] = "generating dropoff"
            ship_priority[id] = 5
    for ship in me.get_ships():
        # Assign missions to the ships. The default is "exploring", if the ship is full - change to "returning",
        # if the ship is on a high amount of halite - collect, and if the ship has arrived to the shipyard - change
        # back to "exploring"
        if ship.id not in ship_status:
            ship_status[ship.id] = "coming back"
        elif game_map.calculate_distance(ship.position, find_closest_basement(ship.position)) > \
                (constants.MAX_TURNS - game.turn_number)*0.8 - 3:
            ship_status[ship.id] = "suicide"
        elif ship_status[ship.id] == "coming back":
            ship_status[ship.id] = "exploring"
        elif ship_status[ship.id] == "returning" and is_in_basement(ship.position) and ship_status[ship.id] != "suicide":
            ship_status[ship.id] = "coming back"
        elif ship_status[ship.id] == "exploring" and ship.halite_amount >= constants.MAX_HALITE * 0.97:
            ship_status[ship.id] = "returning"
        # give priorities
        if ship_status[ship.id] == "exploring":
            ship_priority[ship.id] = 4
        elif ship_status[ship.id] == "returning" or ship_status[ship.id] == "suicide":
            ship_priority[ship.id] = 3
        elif ship_status[ship.id] == "coming back":
            ship_priority[ship.id] = 1
        # If the ship has not enough energy to move - command to stay still.
        if ship.halite_amount < game_map[ship.position].halite_amount / 10:
            next_move[ship.id] = 'o'
            ship_priority[ship.id] = 0
        elif ship_status[ship.id] == "exploring":
            if game_map[ship.position].halite_amount < collect_value:
                # The next move is to a neighbor cell with the most amount of halite
                next_move[ship.id] = decide_next_move(ship.position)
            else:
                next_move[ship.id] = 'o'
                ship_priority[ship.id] = 2
        else: # The try/except is for a case where ship.position==me.shipyard.position
            try:
                next_move[ship.id] = get_diractional_letter(game_map.get_unsafe_moves(
                    ship.position, find_closest_basement(ship.position))[0])
            except:
                next_move[ship.id] = 'o'
    # First, give priority to move ships that just dropped halite in shipyard/dropoff
    for i in range(6):
        for ship in me.get_ships():
            if ship_priority[ship.id] == i:
                if i == 0:
                    command_queue.append(ship.move('o'))
                elif i == 1:
                    next_move[ship.id] = coming_back(ship.position, ship.id, radius)
                    command_queue.append(ship.move(next_move[ship.id]))
                elif i == 2:
                    check = True
                    for ship2 in me.get_ships():
                        if ship_status[ship2.id] == "coming back" and ship.position == game_map.normalize(
                                ship2.position.directional_offset(get_diractional_tuple(next_move[ship2.id]))):
                            check = False
                            next_move[ship.id] = decide_next_move(ship.position, [True, True, True, True, False])
                            ship_priority[ship.id] = 4
                            continue
                    if check:
                        command_queue.append(ship.move(next_move[ship.id]))
                elif i == 3:
                    if ship_status[ship.id] == "suicide":
                        if is_in_basement(ship.position):
                            command_queue.append(ship.move('o'))
                            continue
                        if adjacent_to_basement(ship.position):
                            command_queue.append(ship.move(next_move[ship.id]))
                            continue
                    # Check if the move is safe
                    check_move = is_move_safe(game_map.normalize(ship.position.directional_offset(get_diractional_tuple(
                        next_move[ship.id]))), ship.id)
                    if check_move:
                        command_queue.append(ship.move(next_move[ship.id]))
                    else:
                        # If the move is not safe, find alternative direction to move
                        next_move[ship.id] = find_new_way_home(ship.position, ship.id)
                        command_queue.append(ship.move(next_move[ship.id]))
                elif i == 4:
                    ship_target[ship.id] = scan(ship.position, radius)
                    next_move[ship.id] = go_to_target(ship.position, ship.id)
                    command_queue.append(ship.move(next_move[ship.id]))
                elif i == 5:
                    if ship.position == drop_loc:
                        if me.halite_amount + ship.halite_amount + game_map[drop_loc].halite_amount >= \
                                constants.DROPOFF_COST:
                            command_queue.append(ship.make_dropoff())
                        else:
                            next_move[ship.id] = 'o'
                            command_queue.append(ship.move(next_move[ship.id]))
                    else:
                        ship_target[ship.id] = drop_loc
                        next_move[ship.id] = go_to_target(ship.position, ship.id)
                        command_queue.append(ship.move(next_move[ship.id]))

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if keep_spawn and me.halite_amount >= constants.SHIP_COST and is_move_safe(me.shipyard.position, None):
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

