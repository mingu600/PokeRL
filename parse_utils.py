from random_gen_utils import norm_name
from constants import move_dex, random_sets
from collections import defaultdict

class Move:
    def __init__(self, name):
        self.name = norm_name(name)
        self.max_pp = move_dex[self.name]['pp'] * 8 // 5
        self.current_pp = self.max_pp

class Pokemon:
    def __init__(self, name, form=None, ability=None, item=None, tera_type=None):
        self.name = name
        self.ability = ability
        self.form = form
        self.item = item
        self.moves = {}
        self.volatile_status = None
        self.status = None
        self.tera_type = tera_type
        self.sets = random_sets[norm_name(form)] if norm_name(form) in random_sets else random_sets[norm_name(name)]

class Player:
    def __init__(self, name):
        self.name = name
        self.team = {}
        self.tera = False
        self.tera_blast_role = False

class Side:
    def __init__(self, name, player):
        self.name = name
        self.player = player
        self.hazards = defaultdict(int)
        self.screens = defaultdict(int)

class Field:
    def __init__(self, name):
        self.name = name
        self.weather = None
        self.pseudo_weather = None
        self.terrain = None

def get_nth(text, token, occurrence):
    gen = (i for i, l in enumerate(text) if l == token)
    for _ in range(occurrence - 1):
        next(gen)
    return next(gen)

def get_mon(players, line, op):
    bar_idx = 0
    p_name = line[line[1:].find('|') + 2:][:2]
    player = players[p_name]
    last_bar = line.rfind('|')
    if op == 'ability':
        mon_name = line[8 + len(op):]
        mon_name = mon_name[:mon_name.find('|')]
        return p_name, player, mon_name

    elif op == 'move':
            mon_name = line[11:]
            mon_name = mon_name[:mon_name.find('|')]
            move_name = line[get_nth(line, '|', 3) + 1:]
            move_name = move_name[:move_name.find('|')]
            return p_name, player, mon_name, move_name
        
    elif op == 'switch':
        left_bar = get_nth(line, '|', 3)
        form_name = line[left_bar + 1: last_bar]
        form_name = form_name[:form_name.find(',')]
        mon_name = line[13:left_bar]
        return p_name, player, mon_name, form_name

def print_state(line, players):
    print(line)
    for player_id in players:
        print('Player:', player_id)
        team = players[player_id].team
        for i, mon_name in enumerate(team):
            mon = team[mon_name]
            print('\tPokemon ' + str(i+1) + ':', mon.name)
            print('\t\tAbility:', mon.ability)
            print('\t\tMoves:')
            for move in mon.moves:
                print('\t\t    ' + move, str(mon.moves[move].current_pp) + '/' + str(mon.moves[move].max_pp))
    print('')
