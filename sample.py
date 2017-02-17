import random
from math import sqrt

# This is my implementation of "Kraken Universe" game.
# I decided not to use three-dimensional array and use a dictionary instead.
# For random search it is possible that sometimes path won't be found

directions = {"up": 1, "down": -1, "right": 1, "left": -1, "front": 1, "back": -1}
options = {"B", "K", "P"}


# Function that is used to determine tiles that are located around the initial tile from file.
def generate_directions_list(coords):
    up = coords[0] + " " + str(int(coords[1]) + 1) + " " + coords[2]
    down = coords[0] + " " + str(int(coords[1]) - 1) + " " + coords[2]
    front = str(int(coords[0]) + 1) + " " + coords[1] + " " + coords[2]
    back = str(int(coords[0]) - 1) + " " + coords[1] + " " + coords[2]
    right = coords[0] + " " + coords[1] + " " + str(int(coords[2]) + 1)
    left = coords[0] + " " + coords[1] + " " + str(int(coords[2]) - 1)
    return {up, down, front, back, right, left}


# Class Stack will be used in DFS algorithm
class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Map:
    def __init__(self):
        self.field = {}
        self.lines = []
        self.tiles = {}
        self.read_map()

    def read_map(self):
        with open("input.txt") as file:
            lines = file.readlines()
        self.lines = [x.strip() for x in lines]
        self.lines = [x.split() for x in self.lines]

    def build_tile_dictionary(self):
        for x in self.lines:
            key = " ".join(x[1:4])
            self.tiles[key] = x[0]

    def build_full_dictionary(self):
        for x in self.lines:
            key = " ".join(x[1:4])
            self.tiles[key] = x[0]
            coordinates = key.split()
            dirs = generate_directions_list(coordinates)
            for i in dirs:
                if i in self.tiles and not \
                                        self.tiles[key] + "D" in self.tiles[i]:
                    self.tiles[i] += " %s%s" % (self.tiles[key], "D")  # D means "detected"
                else:
                    self.tiles[i] = "%s%s" % (self.tiles[key], "D")  # D means "detected"


# Class spaceship is able to move in given position, save it's current route and launch
# a bomb in given direction
# x - front/back
# y - up/down
# z - right/left
class Spaceship:
    def __init__(self):
        self.x = 0  # length
        self.y = 0  # height
        self.z = 0  # width
        self.has_bomb = True
        self.route = []

    def move_ship(self, move):
        if move == "up" or move == "down":
            self.y += directions[move]
        elif move == "right" or move == "left":
            self.z += directions[move]
        elif move == "front" or move == "back":
            self.x += directions[move]
        self.route.append(self.get_position())

    def get_position(self):
        return "%s %s %s" % (self.x, self.y, self.z)

    def launch_bomb(self, map_field, direction):
        if self.has_bomb:
            x = self.x
            y = self.y
            z = self.z
            if direction == "up" or direction == "down":
                y += directions[direction]
            elif direction == "right" or direction == "left":
                z += directions[direction]
            elif direction == "front" or direction == "back":
                x += directions[direction]
            position = "%s %s %s" % (x, y, z)
            map_field.tiles[position] = "M"
            self.has_bomb = False
            self.route.append("M " + position)

    def bomb_position(self, position):
        if self.has_bomb:
            self.has_bomb = False
            return "M " + position


def choose_random_direction(dirs):
    key, value = random.choice(list(dirs.items()))
    return key


# In some rare cases this algorithm is not able to find a path
# For example, in case when B/K (0, 1, 0) and B/K (1, 0, 0)
# And Planets are far away, for example (45, 60, 90)
def random_search(map_field):
    paths = {}
    for i in range(100):
        spaceship = Spaceship()
        current_tile = ""
        for j in range(50000):  # if you want more accurate search, increase this number
            # checking allowed positions and returning it as an list
            possible_moves = check_allowed_positions(spaceship)

            # choosing random options from allowed
            allowed_move = choose_random_direction(possible_moves)

            # if spaceship has bomb and something is detected nearby, fire the bomb
            # otherwise just move
            if spaceship.has_bomb and spaceship.get_position() in map_field.tiles:
                spaceship.launch_bomb(map_field, allowed_move)
            else:
                spaceship.move_ship(allowed_move)

            # if current position of ship is in a list - break
            current_position = spaceship.get_position()
            if current_position in map_field.tiles:
                current_tile = map_field.tiles[current_position]
            if current_tile in options:
                break

        # spaceship arrived on a planet then save it into dictionary and return
        if current_tile == "P":
            paths[len(spaceship.route)] = spaceship
    return paths


# Method for excluding prohibited directions from allowed moves
def slice_dic(d, s):
    return {k: v for k, v in d.items() if not k.startswith(s)}


# Function is checking current position so that spaceship won't be able to go out of bounds.
def check_allowed_positions(spaceship):
    allowed_moves = directions
    if spaceship.x == 0:
        allowed_moves = slice_dic(allowed_moves, "back")
    if spaceship.x == 99:
        allowed_moves = slice_dic(allowed_moves, "front")
    if spaceship.y == 0:
        allowed_moves = slice_dic(allowed_moves, "down")
    if spaceship.y == 99:
        allowed_moves = slice_dic(allowed_moves, "up")
    if spaceship.z == 0:
        allowed_moves = slice_dic(allowed_moves, "left")
    if spaceship.z == 99:
        allowed_moves = slice_dic(allowed_moves, "right")
    return allowed_moves


def result_for_random_search(result_map):
    result = random_search(result_map)
    if len(result) == 0:
        print("No paths found. Give some more tries.\nIf does not work"
              ", maybe you should increase number of trials?")
    else:
        spaceship_with_smallest_route = result[min(result.keys())]
        trace = spaceship_with_smallest_route.route
        trace_len = len(trace)
        if not spaceship_with_smallest_route.has_bomb:
            trace_len -= 1
        print("The length of trace is " + str(trace_len))
        for i in trace:
            print(i)


# Returns a traceroute
# I decided to use a DFS algorithm for backtraking search
# So, if the spaceship dies, then tile with a Kraken or Black hole
# will not be included in the algorithm.
# This tile will be matched as "dead" tile.
# There will also be no paths found, if tile with Planet
# is surrounded by Black holes/Krakens from
# the lower tile, right, left and back tiles.
# (Because algorithm only runs in three directions)
#
# This algorithm is not supposed to return the smallest trace to Planet.
# Just the first one that appears
def backtracking_search(map_field):
    result_dfs = dfs(map_field)
    current = result_dfs[0]
    parent_map = result_dfs[1]
    trace_stack = Stack()
    if current is None:  # if no path was found
        return "No paths were found."
    while current != "0 0 0":
        trace_stack.push(current)
        current = parent_map[current]
    trace_stack.push("0 0 0")
    return trace_stack


# This function returns "lazy map" of adjacent tiles and
def adjacent_nodes(tile):
    location = tile.split()
    points = [int(a) for a in location]
    x = points[0]
    y = points[1]
    z = points[2]
    front = None
    up = None
    right = None
    if not x + 1 >= 100:
        front = " ".join([str(x + 1), str(y), str(z)])
    if not y + 1 >= 100:
        up = " ".join([str(x), str(y + 1), str(z)])
    if not z + 1 >= 100:
        right = " ".join([str(x), str(y), str(z + 1)])

    results = [front, up, right]
    return map(lambda b: b is not None, results), results


# DFS returns tuple, which is:
# 1. target tile (location of "P", or None, if path was not found)
# 2. parentMap, which is mapping every tile by its "parent" tile
def dfs(map_field):  # map field for "dfs" should only be build using "build_tile_dictionary"
    tile = "0 0 0"  # always str
    visited = set()
    stack = Stack()
    stack.push(tile)
    parent_map = {}
    target = None
    while not stack.is_empty():
        tile = stack.pop()
        if tile not in visited:
            if tile in map_field.tiles:
                visited.add(tile)
                if map_field.tiles[tile] is "P":
                    target = tile
                    break
            else:
                visited.add(tile)
                nodes = adjacent_nodes(tile)
                bool_res, adjacent = list(nodes[0]), nodes[1]
                for i, val in enumerate(adjacent):
                    if bool_res[i]:
                        stack.push(val)
                        parent_map[val] = tile
    return target, parent_map


def result_for_backtraking(trace_stack):
    if type(trace_stack) is str:
        print(trace_stack)
    else:
        print("The length of trace is " + str(trace_stack.size()))
        while not trace_stack.is_empty():
            print(trace_stack.pop())


# A-star searching algorithm
# In A-star spaceship is not allowed to die, so it is based on tactics
# not to go in critical positions
# Bomb is firing in this algorithm, but I had a problems with showing this info
def a_star_search(map_tiles, spaceship):
    start = "0 0 0"  # initial position
    goal = choose_smallest_goal(map_tiles)  # choose shortest trace (in case if there
    # is more that one Planet)
    closed = set()  # set for nodes that were already visited
    opened = set()
    opened.add(start)
    parent_map = {}  # will contain the most efficient previous step
    g_score = {start: 0}  # will contain the cost of going from some node to another
    f_score = {start: cost_estimation(start, goal)}
    while len(opened) != 0:
        current = smallest_node(opened, f_score)
        if current == goal:
            return reconstruct_path(parent_map, current)
        opened.remove(current)
        closed.add(current)
        neighbours = upgraded_adjacent_nodes(current)
        for neighbour in neighbours:
            if neighbour in closed:
                continue
            tentative_g_score = g_score[current] + 1  # 1 is distance between two nodes
            if neighbour not in opened:
                opened.add(neighbour)
            elif tentative_g_score >= g_score[neighbour]:
                continue
            if neighbour in map_tiles:
                if map_tiles[neighbour] != "P":  # if neighbour node is critical, don't go
                    parent_map[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = 100000
                    if map_tiles[neighbour] == "K":
                        if spaceship.has_bomb:
                            spaceship.bomb_position(neighbour)
                            map_tiles.pop(neighbour)
                            g_score[neighbour] = tentative_g_score
                            f_score[neighbour] = g_score[neighbour] + cost_estimation(neighbour, goal)
                else:
                    parent_map[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = g_score[neighbour] + cost_estimation(neighbour, goal)
            else:
                parent_map[neighbour] = current
                g_score[neighbour] = tentative_g_score
                f_score[neighbour] = g_score[neighbour] + cost_estimation(neighbour, goal)
    return "No paths were found."


def choose_smallest_goal(map_tiles):
    least_trace = None
    chosen_tile = ""
    planets = []
    for i in map_tiles:
        if map_tiles[i] == "P":
            planets.append(i)
    for j in planets:
        location = j.split()
        points = [int(a) for a in location]
        if least_trace is None or sum(points) + 1 < least_trace:
            least_trace = sum(points) + 1
            chosen_tile = j
    return chosen_tile


# Function that estimates heuristic value for node
def cost_estimation(start, goal):
    start_location = start.split()
    start_points = [int(a) for a in start_location]
    goal_location = goal.split()
    goal_points = [int(b) for b in goal_location]
    return sqrt((goal_points[0] - start_points[0]) ** 2 +
                (goal_points[1] - start_points[1]) ** 2 +
                (goal_points[2] - start_points[2]) ** 2)


def smallest_node(node_set, f_map):
    smallest = None
    chosen_node = ""
    for i in node_set:
        if smallest is None or f_map[i] < smallest:
            smallest = f_map[i]
            chosen_node = i
    return chosen_node


# Returns all adjacent nodes of given node
def upgraded_adjacent_nodes(tile):
    location = tile.split()
    points = [int(a) for a in location]
    x = points[0]
    y = points[1]
    z = points[2]
    front = None
    back = None
    up = None
    down = None
    right = None
    left = None
    if not x + 1 >= 100:
        front = " ".join([str(x + 1), str(y), str(z)])
    if not x - 1 < 0:
        back = " ".join([str(x - 1), str(y), str(z)])
    if not y + 1 >= 100:
        up = " ".join([str(x), str(y + 1), str(z)])
    if not y - 1 < 0:
        down = " ".join([str(x), str(y - 1), str(z)])
    if not z + 1 >= 100:
        right = " ".join([str(x), str(y), str(z + 1)])
    if not z - 1 < 0:
        left = " ".join([str(x), str(y), str(z - 1)])

    results = [front, back, up, down, right, left]
    bool_list = list(map(lambda b: b is not None, results))
    result_list = []
    for i, val in enumerate(results):
        if bool_list[i]:
            result_list.append(val)
    return result_list


def reconstruct_path(parent_map, current_node):
    total_path = [current_node]
    while current_node in parent_map.keys():
        current_node = parent_map[current_node]
        total_path.append(current_node)
    return total_path


def result_for_a_star(trace_list):
    if type(trace_list) is str:
        print(trace_list)
    else:
        print("The length of trace is " + str(len(trace_list)))
        for i in reversed(trace_list):
            print(i)


# Demonstrations
# Case 1
# Random search
print("Running demonstration for Random search: ")
map_object = Map()
map_object.build_full_dictionary()  # including adjacent tiles
result_for_random_search(map_object)

# Case 2
# Backtracking search
# Trace always will be "P".x + "P".y + "P".x + 1
print("\nRunning demonstration for Backtracking search: ")
new_map = Map()
new_map.build_tile_dictionary()  # not including adjacent tiles
result_bt = backtracking_search(new_map)
result_for_backtraking(result_bt)

# Case 3
# A-star search
print("\nRunning demonstration for A-star searching algorithm: ")
ship = Spaceship()
trace = a_star_search(new_map.tiles, ship)
result_for_a_star(trace)
