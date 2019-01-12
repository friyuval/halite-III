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
import time
import random
import numpy as np

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
# Constants initialization
ship_status = {}
ship_priority = {}
ship_target = {}
drop_loc = Position(0, 0)
min_dis, max_dis = 16, 20
step_factor = 3
keep_spawn, make_drop, temp_sight = True, False, False
size = game.game_map.width

players = 0
for player in game.players:
    players += 1

stop_spawn_turn = 200  # How many turns before the end stop spawning ships
stop_spawn_halite = 60 if players == 2 else 80
# Starting radius sight of ship and the maximum sight radius.
radius, max_radius = 1, 8 if size <= 48 else 7 if size < 64 else 6
logging.info("Maximum radius: {}".format(max_radius))

# This paramater will grow each time the bot shipd build a new dropoff, but will not exceed dropoffs_max
dropoffs_num = 0
# Max number of dropoffs is determined by the number of players, size and avg amount of halite in the game.
# Formula was calculated using reinforcement learning.
if players == 2:
    if size < 48:
        dropoffs_max = 1
    elif size < 64:
        dropoffs_max = 2
    else:
        dropoffs_max = 3
else:
    if size < 48:
        dropoffs_max = 0
    elif size < 64:
        dropoffs_max = 1
    else:
        dropoffs_max = 2
logging.info("Max dropoffs: {}".format(dropoffs_max))
if size == 32:
    min_dis, max_dis = 14, 18

"""""
def decide_next_move(ship):
    # Find the cardinal around the given position with the most halite
    # Options variable indicates which moves are not allowed. index 0 - north, 1 - south, 2 - east, 3 west
    # and 4 - stay still.
    index = 4
    position = ship.position
    mx_halite = game_map[position].halite_amount
    around = position.get_surrounding_cardinals()
    halite_around = []
    for i in around:
        if game_map[i].halite_amount > mx_halite:
            if is_move_safe( game_map.normalize(game_map[loc].ship.position.directional_offset(get_diractional_tuple((next_move[shipid])))):, ship.id)
"""""


def decide_next_move(ship, options=(True, True, True, True, True)):
    # Find the cardinal around the given position with the most halite
    # Options variable indicates which moves are not allowed. index 0 - north, 1 - south, 2 - east, 3 west
    # and 4 - stay still.
    position = ship.position
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
    global next_move, sent_move, safe_mode
    if not safe_mode:
        # Checks if the move is toward enemy structure
        if game_map[target_move].has_structure and game_map[target_move].structure.owner != game.my_id:
            return False
        # Checks if the move is toward enemy ship
        if game_map[target_move].is_occupied and game_map[target_move].ship.owner != game.my_id and not \
                target_move == me.shipyard.position:
            return False
        around = target_move.get_surrounding_cardinals()
        around.append(target_move)
        for loc in around:
            if game_map[loc].is_occupied and game_map[loc].ship.owner == game.my_id:
                shipid = game_map[loc].ship.id
                if shipid != id and sent_move[shipid] and target_move == game_map.normalize(
                        game_map[loc].ship.position.directional_offset(get_diractional_tuple((next_move[shipid])))):
                    return False
        return True
    logging.info("entering to safe mode")
    global grid
    if grid[target_move.x, target_move.y] != 0:
        logging.info("not safe")
        return False
    logging.info("safe")
    return True


def is_move_safe2(target_move):
    global grid
    if grid[target_move.x, target_move.y] != 0:
        logging.info("not safe")
        return False
    logging.info("safe")
    return True


def find_new_exploring_move(ship):
    options = [True, True, True, True, True]
    id = ship.id
    position = ship.position
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
        new_move = decide_next_move(ship, options)
        check = is_move_safe(game_map.normalize(position.directional_offset(get_diractional_tuple(new_move))), id)
        if check:
            return new_move
        else:
            options[get_index(new_move)] = False
    # If there is no other option - try to move to the shipyard.
    options = [True, True, True, True, True]
    while options[0] or options[1] or options[2] or options[3] or options[4]:
        new_move = decide_next_move(ship, options)
        check = is_move_safe(game_map.normalize(position.directional_offset(get_diractional_tuple(new_move))), id)
        if check:
            return new_move
        else:
            options[get_index(new_move)] = False
    return 'o'


def adjacent_to_basement(position):
    if game_map.calculate_distance(position, me.shipyard.position) == 1:
            return True
    for dropoff in me.get_dropoffs():
        if game_map.calculate_distance(position, dropoff.position) == 1:
            return True
    return False


def coming_back(ship, radius):
    global ship_target
    ship_target[ship.id] = find_new_target(ship, radius)
    return go_to_target(ship)


def find_new_target(ship, radius):
    # Find the a "target" cell in the area with the most amount of halite that is not assigned to another ship.
    # The area is determined by the radius sight of the ships.
    position = ship.position
    id = ship.id
    x, y = position.x, position.y
    max_halite = -1
    max_location = Position(x, y)
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if is_target_available(game_map.normalize(Position(x+i, y+j)), id) and \
                    game_map[game_map.normalize(Position(x+i, y+j))].halite_amount > max_halite:
                max_halite = game_map[game_map.normalize(Position(x+i, y+j))].halite_amount
                max_location = game_map.normalize(Position(x+i, y+j))
    return max_location


def is_target_available(target, id):
    global ship_target
    for ship in me.get_ships():
        if ship.id != id:
            try:
                if ship_target[ship.id] == target:
                    return False
            except KeyError:
                pass
    return True


def go_to_target(ship):
    # Send ship to the cell with the most amount of halite in the area. If the move(s) is not safe, send the ship to
    # the cell with the most amount of halite around it.
    id = ship.id
    position = ship.position
    global ship_target, next_move, collect_value
    temp = game_map.get_unsafe_moves(position, ship_target[id])
    if len(temp) == 0:
        if is_move_safe(position, id):
            return 'o'
        else:
            next_move[id] = 'o'
            return find_new_exploring_move(ship)
    if len(temp) == 1:
        if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id):
            return get_diractional_letter(temp[0])
        else:
            next_move[id] = temp[0]
            return find_new_exploring_move(ship)
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
    return find_new_exploring_move(ship)


def go_back_home(ship):
    position = ship.position
    id = ship.id
    global ship_target
    temp = game_map.get_unsafe_moves(position, ship_target[id])
    if len(temp) == 0:
        return 'o'
    if len(temp) == 1:
        if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id):
            return get_diractional_letter(temp[0])
        if game_map[game_map.normalize(position.directional_offset(temp[0]))].has_structure and \
                game_map[game_map.normalize(position.directional_offset(temp[0]))].structure.owner != game.my_id:
            return go_around_enemy(ship, temp[0])
        if game_map[game_map.normalize(position.directional_offset(temp[0]))].is_occupied and \
                game_map[game_map.normalize(position.directional_offset(temp[0]))].ship.owner != game.my_id:
            return go_around_enemy(ship, temp[0])
        if temp[0] == Direction.North:
            if is_move_safe(position, id):
                return 'o'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
                return 'e'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
                return 'w'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
                return 's'
            return 'o'
        if temp[0] == Direction.South:
            if is_move_safe(position, id):
                return 'o'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
                return 'e'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
                return 'w'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
                return 'n'
            return 'o'
        if temp[0] == Direction.East:
            if is_move_safe(position, id):
                return 'o'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
                return 'n'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
                return 's'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
                return 'w'
            return 'o'
        # temp[0] == Direction.West
        if is_move_safe(position, id):
            return 'o'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
            return 'n'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
            return 's'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
            return 'e'
        return 'o'
    # len(temp) == 2
    if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id) and \
            is_move_safe(game_map.normalize(position.directional_offset(temp[1])), id):
        choice = random.choice([temp[0], temp[1]])
        return get_diractional_letter(choice)
    if is_move_safe(game_map.normalize(position.directional_offset(temp[0])), id):
        return get_diractional_letter(temp[0])
    if is_move_safe(game_map.normalize(position.directional_offset(temp[1])), id):
        return get_diractional_letter(temp[1])
    if is_move_safe(position, id):
        return 'o'
    if temp[0] == Direction.East:
        if temp[1] == Direction.North:
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
                return 's'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
                return 'w'
        if temp[1] == Direction.South:
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
                return 'n'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
                return 'w'
    elif temp[0] == Direction.West:
        if temp[1] == Direction.North:
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
                return 's'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
                return 'e'
        if temp[1] == Direction.South:
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
                return 'n'
            if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
                return 'e'
    if game_map[game_map.normalize(position.directional_offset(temp[0]))].has_structure and \
            game_map[game_map.normalize(position.directional_offset(temp[0]))].structure.owner != game.my_id:
        return get_diractional_letter(temp[0])
    elif game_map[game_map.normalize(position.directional_offset(temp[1]))].has_structure and \
            game_map[game_map.normalize(position.directional_offset(temp[1]))].structure.owner != game.my_id:
        return get_diractional_letter(temp[1])
    elif game_map[game_map.normalize(position.directional_offset(temp[0]))].is_occupied and \
            game_map[game_map.normalize(position.directional_offset(temp[0]))].ship.owner != game.my_id:
        return get_diractional_letter(temp[0])
    elif game_map[game_map.normalize(position.directional_offset(temp[1]))].is_occupied and \
            game_map[game_map.normalize(position.directional_offset(temp[1]))].ship.owner != game.my_id:
        return get_diractional_letter(temp[1])
    return 'o'


def go_around_enemy(ship, direction):
    position = ship.position
    id = ship.id
    logging.info("Go around enemy, ship id: {}".format(id))
    if direction == Direction.North:
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
            return 'e'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
            return 'w'
        if is_move_safe(position, id):
            return 'o'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
            return 's'
        return 'n'
    if direction == Direction.South:
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
            return 'e'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
            return 'w'
        if is_move_safe(position, id):
            return 'o'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
            return 'n'
        return 's'
    if direction == Direction.West:
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
            return 'n'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
            return 's'
        if is_move_safe(position, id):
            return 'o'
        if is_move_safe(game_map.normalize(position.directional_offset(Direction.East)), id):
            return 'e'
        return 'w'
    # East
    if is_move_safe(game_map.normalize(position.directional_offset(Direction.North)), id):
        return 'n'
    if is_move_safe(game_map.normalize(position.directional_offset(Direction.South)), id):
        return 's'
    if is_move_safe(position, id):
        return 'o'
    if is_move_safe(game_map.normalize(position.directional_offset(Direction.West)), id):
        return 'w'
    return 'e'


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
    global dropoffs_num, players
    s = game_map.width
    base_loc = me.shipyard.position
    x = base_loc.x
    y = base_loc.y
    max_amount = -1
    curr_loc = Position(0, 0)
    logging.info("Dropoffs_num = {}".format(dropoffs_num))
    if dropoffs_num == 1:
        imax = range(int(s / 2))
        jmax = range(s) if players == 2 else range(int(s / 2))
        x_add = 0 if x < s / 2 else int(s / 2)
        if players == 2:
            y_add = 0
        else:
            y_add = 0 if y < s / 2 else int(s / 2)
    else:
        imax, jmax, x_add, y_add = range(s), range(s), 0, 0
    logging.info("imax = {}, jmax = {}, x_add = {}, y_add = {}".format(imax, jmax, x_add, y_add))
    for i in imax:
        for j in jmax:
            if game_map[Position(i + x_add, j + y_add)].has_structure:
                continue
            dis = []
            dis.append(game_map.calculate_distance(Position(i + x_add, j + y_add), base_loc))
            for dropoff in me.get_dropoffs():
                dis.append(game_map.calculate_distance(Position(i + x_add, j + y_add), dropoff.position))
            #  Condition for building a new dropoff: must be in a distance grater (or equal) than min_dis from all other
            #  dropoffs (including shipyard) and in a distance smaller than max_dis from one of the other dropoffs.
            check = False
            for x in dis:
                if min_dis <= x <= max_dis:
                    check = True
                elif x < min_dis:
                    check = False
                    break
            if check:
                temp = halite_amount_around(Position(i + x_add, j + y_add), 5)
                if temp > max_amount:
                    curr_loc = Position(i + x_add, j + y_add)
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
    global max_radius
    x, y = position.x, position.y
    radius = prev_radius
    total = 0
    while radius < max_radius:
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


def find_closest_basement(position, check=True):
    location = me.shipyard.position
    min_dis = game_map.calculate_distance(position, location)
    count = 0
    for dropoff in me.get_dropoffs():
        count += 1
        temp = game_map.calculate_distance(position, dropoff.position)
        if check:
            temp = temp - count * 5
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


def erase_collided_ships():
    global ship_priority, ship_status, ship_target
    dl = []
    for id in ship_target:
        # checks every id in the dictionaries if it still exist
        check = True
        for ship in me.get_ships():
            if id == ship.id:  # If the ship exists, do not add it to the dl list
                check = False
                break
        if check:  # Add to dl list the ship in order to erase it from the dictionaries
            dl.append(id)
    for id in dl:  # Delete all ships whose ids are in dl list
        del ship_priority[id]
        del ship_status[id]
        del ship_target[id]
        logging.info("Deleted")


def clear_drop_priority():
    global ship_status, ship_priority
    for ship in me.get_ships():
        try:
            if ship_priority[ship.id] == 5:
                ship_priority[ship.id] = 4
                ship_status[ship.id] = "exploring"
        except KeyError:
            continue


def check_for_better_step(ship, factor):
    global ship_target
    position = ship.position
    id = ship.id
    temp = game_map.get_unsafe_moves(position, ship_target[id])
    halite = game_map[position].halite_amount
    if len(temp) == 1:
        halite0 = game_map[game_map.normalize(position.directional_offset(temp[0]))].halite_amount
        if halite0 > halite * factor and not \
                game_map[game_map.normalize(position.directional_offset(temp[0]))].is_occupied:
            return get_diractional_letter(temp[0])
    elif len(temp) == 2:
        halite0 = game_map[game_map.normalize(position.directional_offset(temp[0]))].halite_amount
        halite1 = game_map[game_map.normalize(position.directional_offset(temp[1]))].halite_amount
        if halite * factor >= halite0 and halite * factor >= halite1:
            return 'o'
        if halite0 > halite1:
            if not game_map[game_map.normalize(position.directional_offset(temp[0]))].is_occupied:
                return get_diractional_letter(temp[0])
        elif not game_map[game_map.normalize(position.directional_offset(temp[1]))].is_occupied:
            return get_diractional_letter(temp[1])
    return 'o'


def is_spawn_possible():
    global next_move
    shipyard_pos = me.shipyard.position
    if game_map[shipyard_pos.directional_offset(Direction.North)].is_occupied and \
            game_map[shipyard_pos.directional_offset(Direction.North)].ship.owner == game.my_id and \
            next_move[game_map[shipyard_pos.directional_offset(Direction.North)].ship.id] == 's':
        return False
    if game_map[shipyard_pos.directional_offset(Direction.South)].is_occupied and \
            game_map[shipyard_pos.directional_offset(Direction.South)].ship.owner == game.my_id and \
            next_move[game_map[shipyard_pos.directional_offset(Direction.South)].ship.id] == 'n':
        return False
    if game_map[shipyard_pos.directional_offset(Direction.East)].is_occupied and \
            game_map[shipyard_pos.directional_offset(Direction.East)].ship.owner == game.my_id and \
            next_move[game_map[shipyard_pos.directional_offset(Direction.East)].ship.id] == 'w':
        return False
    if game_map[shipyard_pos.directional_offset(Direction.West)].is_occupied and \
            game_map[shipyard_pos.directional_offset(Direction.West)].ship.owner == game.my_id and \
            next_move[game_map[shipyard_pos.directional_offset(Direction.West)].ship.id] == 'e':
        return False
    if game_map[shipyard_pos].is_occupied and game_map[shipyard_pos].ship.owner == game.my_id and \
            next_move[game_map[shipyard_pos].ship.id] == 'o':
        return False
    return True


def mark_the_map():
    # Scan the map for ships and structures. Legend: 0 - empty, 1 - my ship, 2 - enemy ship, 3 - my structure,
    # 4 - enemy structure.
    logging.info("Mark the map")
    global size
    grid = np.zeros((size, size), dtype=int)
    logging.info("map size {}".format(grid.shape))
    for player in game.players.values():
        if player.id == game.my_id:
            check = True
        else:
            check = False
        for ship in player.get_ships():
            grid[ship.position.x, ship.position.y] = 1 if check else 2
            logging.info("cell {} is occupied by a ship and marked {}".format(
                (ship.position.x, ship.position.y), 1 if check else 2))
        for dropoff in player.get_dropoffs():
            grid[dropoff.position.x, dropoff.position.y] = 3 if check else 4
            logging.info("cell {} is occupied by a dropoff and marked {}".format(
                (dropoff.position.x, dropoff.position.y), 3 if check else 4))
        grid[player.shipyard.position.x, player.shipyard.position.y] = 3 if check else 4
        logging.info("cell {} is occupied by a shipyard and marked {}".format(
            (player.shipyard.position.x, player.shipyard.position.y), 3 if check else 4))
    return grid


def check_for_collision():
    global size, next_move, ship_status
    grid = np.zeros((size, size), dtype=int)
    for ship in me.get_ships():
        pos = game_map.normalize(ship.position.directional_offset(get_diractional_tuple((next_move[ship.id]))))
        x, y = pos.x, pos.y
        if grid[x, y] == 1 and ship_status[ship.id] != "suicide":
            return True
        grid[x, y] = 1
    return False


def send_command_moves():
    global next_move
    for ship in me.get_ships():
        if next_move[ship.id] != "d":
            command_queue.append(ship.move(next_move[ship.id]))


while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    start = time.perf_counter()
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    next_move = {}
    sent_move = {}
    erase_collided_ships()  # Erase from dictionaries all ships that not longer exist
    safe_mode = False
    avg_h = avg_halite()
    temp_sight = False
    ship_amount = len(me.get_ships())
    if ship_amount >= 30:
        temp_sight = True
        temp_radius = 6
        if ship_amount >= 40:
            temp_radius = 5
            if ship_amount >= 60:
                temp_radius = 4
    collect_value = max(avg_h / 4 + game.turn_number / constants.MAX_TURNS * 20,
                        50 - game.turn_number / constants.MAX_TURNS * 25)
    if radius < max_radius:  # Calculate the sight radius of ships
        radius = calculate_radius(me.shipyard.position, avg_h, radius)

    if make_drop:
        if len(me.get_dropoffs()) >= dropoffs_num:
            logging.info("OK")
            make_drop = False
        elif game_map[drop_loc].has_structure:  # Check that the assigned place for a dropoff is not taken by another.
            logging.info("has structure in {}".format(drop_loc))
            clear_drop_priority()
            temp_sight = True
            temp_radius = 3
            drop_loc = find_drop_location(min_dis, max_dis)
            id = find_closest_ship(drop_loc)
            ship_status[id] = "generating dropoff"
            ship_priority[id] = 5
    elif len(me.get_ships()) == 17 and len(me.get_dropoffs()) < 1 <= dropoffs_max:
        dropoffs_num = 1
        logging.info("Make dropoff!")
        temp_sight = True
        temp_radius = 3
        make_drop = True
        drop_loc = find_drop_location(min_dis, max_dis)
        logging.info("at loc {}".format(drop_loc))
        id = find_closest_ship(drop_loc)
        ship_status[id] = "generating dropoff"
        ship_priority[id] = 5
    elif len(me.get_ships()) == 32 and len(me.get_dropoffs()) < 2 <= dropoffs_max:
        dropoffs_num = 2
        logging.info("Make dropoff!")
        temp_sight = True
        temp_radius = 3
        make_drop = True
        drop_loc = find_drop_location(min_dis, max_dis + 3)
        logging.info("at loc {}".format(drop_loc))
        id = find_closest_ship(drop_loc)
        ship_status[id] = "generating dropoff"
        ship_priority[id] = 5
    elif len(me.get_ships()) == 45 and len(me.get_dropoffs()) < 3 <= dropoffs_max:
        dropoffs_num = 3
        logging.info("Make dropoff!")
        temp_sight = True
        temp_radius = 3
        make_drop = True
        drop_loc = find_drop_location(min_dis, max_dis + 6)
        logging.info("at loc {}".format(drop_loc))
        id = find_closest_ship(drop_loc)
        ship_status[id] = "generating dropoff"
        ship_priority[id] = 5
    if constants.MAX_TURNS - game.turn_number <= stop_spawn_turn or avg_halite() <= stop_spawn_halite:
        logging.info("Stop producing ships")
        logging.info("average halite: {}".format(avg_halite()))
        keep_spawn = False
    if make_drop:  # check that the assigned ship to become a dropoff is still exist
        try:
            check = me.get_ship(id)
        except:
            logging.info("Ship {} does not exist anymore".format(id))
            temp_sight = True
            drop_loc = find_drop_location(16, 20)
            clear_drop_priority()
            id = find_closest_ship(drop_loc)
            ship_status[id] = "generating dropoff"
            ship_priority[id] = 5

    for ship in me.get_ships():
        # Assign missions to the ships
        sent_move[ship.id] = False
        if ship.id not in ship_status:
            ship_status[ship.id] = "coming back"
        elif game_map.calculate_distance(ship.position, find_closest_basement(ship.position, False)) > \
                (constants.MAX_TURNS - game.turn_number)*0.8 - 3:
            ship_status[ship.id] = "suicide"
        elif ship_status[ship.id] == "coming back":
            ship_status[ship.id] = "exploring"
        elif ship_status[ship.id] == "returning" and is_in_basement(ship.position) and ship_status[ship.id] != "suicide":
            ship_status[ship.id] = "coming back"
        elif ship_status[ship.id] == "exploring" and ship.halite_amount >= constants.MAX_HALITE * 0.97:
            ship_status[ship.id] = "returning"

        # Give priorities
        if ship_status[ship.id] == "exploring":
            ship_priority[ship.id] = 4
        elif ship_status[ship.id] == "returning" or ship_status[ship.id] == "suicide":
            ship_priority[ship.id] = 3
        elif ship_status[ship.id] == "coming back":
            ship_priority[ship.id] = 1
        elif ship_status[ship.id] == "generating dropoff":
            ship_priority[ship.id] = 5

        # If the ship has not enough energy to move - command to stay still.
        if ship.halite_amount < game_map[ship.position].halite_amount / 10:
            ship_priority[ship.id] = 0
        elif ship_status[ship.id] == "exploring":
            if game_map[ship.position].halite_amount < collect_value:
                # The next move is to a neighbor cell with the most amount of halite
                next_move[ship.id] = decide_next_move(ship)
            else:
                next_move[ship.id] = 'o'
                ship_priority[ship.id] = 2
        else:
            ship_target[ship.id] = find_closest_basement(ship.position)
            temp = game_map.get_unsafe_moves(ship.position, ship_target[ship.id])
            if len(temp) == 1 or len(temp) == 2:
                next_move[ship.id] = get_diractional_letter(temp[0])
            else:
                next_move[ship.id] = 'o'

    # send moving commands ordered by priority
    for i in range(6):
        for ship in me.get_ships():
            if ship_priority[ship.id] == i:
                if i == 0:
                    next_move[ship.id] = 'o'
                    sent_move[ship.id] = True
                elif i == 1:
                    next_move[ship.id] = coming_back(ship, radius)
                    sent_move[ship.id] = True
                elif i == 2:
                    next_move[ship.id] = check_for_better_step(ship, step_factor)
                    if next_move[ship.id] == 'o':
                        if is_move_safe(ship.position, ship):
                            sent_move[ship.id] = True
                        else:
                            ship_priority[ship.id] = 4
                    else:
                        ship_priority[ship.id] = 4
                elif i == 3:
                    if ship_status[ship.id] == "suicide":
                        if is_in_basement(ship.position):
                            next_move[ship.id] = 'o'
                            sent_move[ship.id] = True
                            continue
                        if adjacent_to_basement(ship.position):
                            sent_move[ship.id] = True
                            continue
                    next_move[ship.id] = go_back_home(ship)
                    sent_move[ship.id] = True
                elif i == 4:
                    ship_target[ship.id] = find_new_target(ship, temp_radius if temp_sight else radius)
                    next_move[ship.id] = go_to_target(ship)
                    sent_move[ship.id] = True
                elif i == 5:
                    if ship.position == drop_loc:
                        if me.halite_amount + ship.halite_amount + game_map[drop_loc].halite_amount >= \
                                constants.DROPOFF_COST:
                            next_move[ship.id] = 'd'
                            command_queue.append(ship.make_dropoff())
                            logging.info("making drop at {}".format(drop_loc))
                        else:
                            next_move[ship.id] = 'o'
                            sent_move[ship.id] = True
                            logging.info("Waiting to have enough money at {}".format(drop_loc))
                    else:
                        ship_target[ship.id] = drop_loc
                        logging.info("Go to drop loc at at {}".format(drop_loc))
                        next_move[ship.id] = go_to_target(ship)
                        sent_move[ship.id] = True

    if check_for_collision():
        logging.info("collision ahead!!")
        safe_mode = True
        grid = mark_the_map()  # Mark all ships, dropoffs and shipyards on the map
        # send moving commands ordered by priority
        for ship in me.get_ships():
            sent_move[ship.id] = False
        for i in range(6):
            for ship in me.get_ships():
                if sent_move[ship.id]:
                    continue
                if ship_priority[ship.id] == i:
                    if i == 0:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        next_move[ship.id] = 'o'
                        command_queue.append(ship.move('o'))
                        sent_move[ship.id] = True
                        logging.info("ship {} does not have enough energy - so stay".format(ship.id))
                    elif i == 1:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        next_move[ship.id] = coming_back(ship, radius)
                        command_queue.append(ship.move(next_move[ship.id]))
                        grid[ship.position.x, ship.position.y] = 3
                        logging.info("changing grid at {} to 3".format((ship.position.x, ship.position.y)))
                        new_loc = game_map.normalize(ship.position.directional_offset(get_diractional_tuple((next_move[ship.id]))))
                        grid[new_loc.x, new_loc.y] = 1
                        logging.info("changing grid at {} to 1".format((new_loc.x, new_loc.y)))
                        sent_move[ship.id] = True
                        logging.info("ship {} is coming back, the move is: {}".format(ship.id, next_move[ship.id]))
                    elif i == 2:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        logging.info("ship {} is trying to collect money".format(ship.id))
                        next_move[ship.id] = check_for_better_step(ship, step_factor)
                        if next_move[ship.id] == 'o':
                            command_queue.append(ship.move('o'))
                            sent_move[ship.id] = True
                            logging.info("ship {} is collecting money".format(ship.id))
                        else:
                            ship_priority[ship.id] = 4
                    elif i == 3:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        if ship_status[ship.id] == "suicide":
                            if is_in_basement(ship.position):
                                command_queue.append(ship.move('o'))
                                sent_move[ship.id] = True
                                continue
                            if adjacent_to_basement(ship.position):
                                command_queue.append(ship.move(next_move[ship.id]))
                                sent_move[ship.id] = True
                                grid[ship.position.x, ship.position.y] = 0
                                logging.info("changing grid at {} to 0".format((ship.position.x, ship.position.y)))
                                logging.info("ship {} is suiciding, the move is: {}".format(ship.id, next_move[ship.id]))
                                continue
                        next_move[ship.id] = go_back_home(ship)
                        command_queue.append(ship.move(next_move[ship.id]))
                        sent_move[ship.id] = True
                        grid[ship.position.x, ship.position.y] = 0
                        logging.info("changing grid at {} to 0".format((ship.position.x, ship.position.y)))
                        new_loc = game_map.normalize(ship.position.directional_offset(get_diractional_tuple((next_move[ship.id]))))
                        grid[new_loc.x, new_loc.y] = 1
                        logging.info("ship {} is returning, the move is: {}".format(ship.id, next_move[ship.id]))
                        logging.info("changing grid at {} to 1".format((new_loc.x, new_loc.y)))
                    elif i == 4:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        ship_target[ship.id] = find_new_target(ship, temp_radius if temp_sight else radius)
                        next_move[ship.id] = go_to_target(ship)
                        command_queue.append(ship.move(next_move[ship.id]))
                        sent_move[ship.id] = True
                        grid[ship.position.x, ship.position.y] = 0
                        logging.info("changing grid at {} to 0".format((ship.position.x, ship.position.y)))
                        new_loc = game_map.normalize(ship.position.directional_offset(get_diractional_tuple((next_move[ship.id]))))
                        grid[new_loc.x, new_loc.y] = 1
                        logging.info("ship {} is exploring, the move is: {}".format(ship.id, next_move[ship.id]))
                        logging.info("changing grid at {} to 1".format((new_loc.x, new_loc.y)))
                    elif i == 5:
                        logging.info("Ship {} has priority {}".format(ship.id, ship_priority[ship.id]))
                        if ship.position == drop_loc:
                            if me.halite_amount + ship.halite_amount + game_map[drop_loc].halite_amount >= \
                                    constants.DROPOFF_COST:
                                command_queue.append(ship.make_dropoff())
                                grid[ship.position.x, ship.position.y] = 3
                                logging.info("changing grid at {} to 3".format((ship.position.x, ship.position.y)))
                                logging.info("making drop at {}".format(drop_loc))
                            else:
                                next_move[ship.id] = 'o'
                                command_queue.append(ship.move(next_move[ship.id]))
                                sent_move[ship.id] = True
                                logging.info("Ship {} is waiting to have enough money at {}".format(ship.id, drop_loc))
                        else:
                            ship_target[ship.id] = drop_loc
                            logging.info("Go to drop loc at at {}".format(drop_loc))
                            next_move[ship.id] = go_to_target(ship)
                            command_queue.append(ship.move(next_move[ship.id]))
                            sent_move[ship.id] = True
                            grid[ship.position.x, ship.position.y] = 0
                            logging.info("changing grid at {} to 0".format((ship.position.x, ship.position.y)))
                            new_loc = game_map.normalize(
                                ship.position.directional_offset(get_diractional_tuple((next_move[ship.id]))))
                            grid[new_loc.x, new_loc.y] = 1
                            logging.info("ship {} is moving towards dropoff location, the move is: {}".format(ship.id, next_move[ship.id]))
                            logging.info("changing grid at {} to 1".format((new_loc.x, new_loc.y)))

    else:
        logging.info("no collision")
        send_command_moves()

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if not make_drop:
        if keep_spawn and me.halite_amount >= constants.SHIP_COST and is_spawn_possible():
            command_queue.append(me.shipyard.spawn())
    else:
        if keep_spawn and me.halite_amount >= constants.SHIP_COST + constants.DROPOFF_COST and is_spawn_possible():
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
    end = time.perf_counter()
    logging.info("Number of ships: {}".format(len(me.get_ships())))
    logging.info("Time taken: {} ms".format((end-start)*1000))


