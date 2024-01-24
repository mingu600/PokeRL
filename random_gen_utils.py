import random
from typing import Set, Optional, Dict, List
from constants import *
import json
from collections import defaultdict
import requests
import random

damage_convert = {0: 0, 1: 1, 2: -1, 3: -10}

def norm_name(name):
    return name\
        .replace(" ", "")\
        .replace("-", "")\
        .replace(".", "")\
        .replace("\'", "")\
        .replace("%", "")\
        .replace("*", "")\
        .replace(":", "")\
        .replace("&#39;", "") \
        .strip()\
        .lower()\
        .encode('ascii', 'ignore')\
        .decode('utf-8')

def get_effectiveness(attack_type, species):
    result = 0
    for mon_type in species['types']:
        result += damage_convert[int(typechart[norm_name(mon_type)]['damageTaken'][attack_type])]
    return result

def get_move_type(move, species, abilities, tera_type) -> str:
    if move['id'] == 'terablast':
        return tera_type
    if move['id'] in ['judgment', 'revelationdance']:
        return species['types'][0]

    if move['name'] == "Raging Bull" and species['name'].startswith("Tauros-Paldea"):
        if species['name'].endswith("Combat"):
            return "Fighting"
        if species['name'].endswith("Blaze"):
            return "Fire"
        if species['name'].endswith("Aqua"):
            return "Water"

    if move['name'] == "Ivy Cudgel" and species['name'].startswith("Ogerpon"):
        if species['name'].endswith("Wellspring"):
            return "Water"
        if species['name'].endswith("Hearthflame"):
            return "Fire"
        if species['name'].endswith("Cornerstone"):
            return "Rock"

    move_type = move['type']
    if move_type == 'Normal':
        if 'Aerilate' in abilities:
            return 'Flying'
        if 'Galvanize' in abilities:
            return 'Electric'
        if 'Pixilate' in abilities:
            return 'Fairy'
        if 'Refrigerate' in abilities:
            return 'Ice'
    return move_type

def serene_grace_benefits(move) -> bool:
    return move['secondary'].get('chance', 0) and 20 < move['secondary']['chance'] < 100

def query_moves(
    moves: Optional[Set[str]],
    species: Dict,
    tera_type: str,
    abilities: Set[str] = set()):
    counter = {
            'damage': 0,
            'technician': 0,
            'skilllink': 0,
            'recoil': 0,
            'drain': 0,
            'stab': 0,
            'stabtera': 0,
            'strongjaw': 0,
            'ironFist': 0,
            'sound': 0,
            'priority': 0,
            'sheerforce': 0,
            'serenegrace': 0,
            'inaccurate': 0,
            'recovery': 0,
            'contrary': 0,
            'physicalsetup': 0,
            'specialsetup': 0,
            'mixedsetup': 0,
            'speedsetup': 0,
            'setup': 0,
            'hazards': 0,
        }
    counter['damaging_moves'] = []
    types = species['types']
    if not moves:
        return counter

    categories = {'Physical': 0, 'Special': 0, 'Status': 0}

    for moveid in moves:
        move = move_dex[moveid]

        move_type = get_move_type(move, species, abilities, tera_type)
        if move.get('damage') or move.get('damageCallback'):
            counter['damage'] += 1
            counter.damaging_moves.add(move)
        else:
            categories[move['category']] += 1

        if moveid == 'lowkick' or (
            move.get('basePower') and move['basePower'] <= 60 and moveid != 'rapidspin'
        ):
            counter['technician'] += 1

        if move.get('multihit') and isinstance(move['multihit'], list) and move['multihit'][1] == 5:
            counter['skilllink'] += 1

        if move.get('recoil') or move.get('hasCrashDamage'):
            counter['recoil'] += 1

        if move.get('drain'):
            counter['drain'] += 1

        if move.get('basePower') or move.get('basePowerCallback'):
            if not moveid in NO_STAB or species['id'] in PRIORITY_POKEMON and move['priority'] > 0:
                if move_type not in counter:
                    counter[move_type] = 0
                counter[move_type] += 1
                if move_type in types:
                    counter['stab'] += 1
                if tera_type == move_type:
                    counter['stabtera'] += 1
                counter['damaging_moves'].append(move)

            if move['flags'].get('bite'):
                counter['strongjaw'] += 1

            if move['flags'].get('punch'):
                counter['ironFist'] += 1

            if move['flags'].get('sound'):
                counter['sound'] += 1

            if move['priority'] > 0 or (
                moveid == 'grassyglide' and 'Grassy Surge' in abilities
            ):
                counter['priority'] += 1

        if move.get('secondary') or move.get('hasSheerForce'):
            counter['sheerforce'] += 1

            if serene_grace_benefits(move):
                counter['serenegrace'] += 1

        if move.get('accuracy') and move['accuracy'] is not True and move['accuracy'] < 90:
            counter['inaccurate'] += 1

        if moveid in RECOVERY_MOVES:
            counter['recovery'] += 1

        if moveid in CONTRARY_MOVES:
            counter['contrary'] += 1

        if moveid in PHYSICAL_SETUP:
            counter['physicalsetup'] += 1

        if moveid in SPECIAL_SETUP:
            counter['specialsetup'] += 1

        if moveid in MIXED_SETUP:
            counter['mixedsetup'] += 1

        if moveid in SPEED_SETUP:
            counter['speedsetup'] += 1

        if moveid in SETUP:
            counter['setup'] += 1

        if moveid in HAZARDS:
            counter['hazards'] += 1

    counter['Physical'] = int(categories['Physical'])
    counter['Special'] = int(categories['Special'])
    counter['Status'] = int(categories['Status'])

    return counter

def incompatible_moves(moves, move_pool, moves_a, moves_b):

    if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
        return

    move_array_a = moves_a if isinstance(moves_a, list) else [moves_a]
    move_array_b = moves_b if isinstance(moves_b, list) else [moves_b]
    
    for moveid1 in moves:

        if moveid1 in move_array_b:
            for moveid2 in move_array_a:
                if moveid1 != moveid2 and moveid2 in move_pool:
                    move_pool.remove(moveid2)
                    if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
                        return

        if moveid1 in move_array_a:
            for moveid2 in move_array_b:
                if moveid1 != moveid2 and moveid2 in move_pool:
                    move_pool.remove(moveid2)
                    if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
                        return


def cull_move_pool(types: List[str], moves: Set[str], abilities: Set[str], counter,
                move_pool: List[str], team_details, species,tera_type: str, role) -> None:

    MAX_MOVE_COUNT = 4
    if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
        return

    if len(moves) == MAX_MOVE_COUNT - 2:
        unpaired_moves = list(move_pool)
        for pair in MOVE_PAIRS:
            if pair[0] in move_pool and pair[1] in move_pool:
                unpaired_moves.remove(pair[0])
                unpaired_moves.remove(pair[1])
        if len(unpaired_moves) == 1:
            move_pool.remove(unpaired_moves[0])

    if len(moves) == MAX_MOVE_COUNT - 1:
        for pair in MOVE_PAIRS:
            if pair[0] in move_pool and pair[1] in move_pool:
                move_pool.remove(pair[0])
                move_pool.remove(pair[1])

    if team_details.get('screens') and len(move_pool) >= MAX_MOVE_COUNT + 2:
        if 'reflect' in move_pool:
            move_pool.remove('reflect')
        if 'lightscreen' in move_pool:
            move_pool.remove('lightscreen')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    if team_details.get('stickyWeb'):
        if 'stickyweb' in move_pool:
            move_pool.remove('stickyweb')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    if team_details.get('stealthRock'):
        if 'stealthrock' in move_pool:
            move_pool.remove('stealthrock')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    if team_details.get('defog') or team_details.get('rapidSpin'):
        if 'defog' in move_pool:
            move_pool.remove('defog')
        if 'rapidspin' in move_pool:
            move_pool.remove('rapidspin')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    if team_details.get('toxicSpikes') and team_details['toxicSpikes'] >= 2:
        if 'toxicspikes' in move_pool:
            move_pool.remove('toxicspikes')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    if team_details.get('spikes') and team_details['spikes'] >= 2:
        if 'spikes' in move_pool:
            move_pool.remove('spikes')
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            return

    incompatible_pairs = [
        [STATUS_MOVES, ['healingwish', 'switcheroo', 'trick']],
        [SETUP, PIVOT_MOVES],
        [SETUP, HAZARDS],
        [SETUP, ['defog', 'nuzzle', 'toxic', 'waterspout', 'yawn', 'haze']],
        [PHYSICAL_SETUP, PHYSICAL_SETUP],
        [SPECIAL_SETUP, 'thunderwave'],
        ['substitute', PIVOT_MOVES],
        [SPEED_SETUP, ['aquajet', 'rest', 'trickroom']],
        ['curse', ['irondefense', 'rapidspin']],
        ['dragondance', 'dracometeor'],
        [['psychic', 'psychicnoise'], ['psyshock', 'psychicnoise']],
        ['surf', 'hydropump'],
        ['liquidation', 'wavecrash'],
        ['aquajet', 'flipturn'],
        ['gigadrain', 'leafstorm'],
        ['powerwhip', 'hornleech'],
        [['airslash', 'bravebird', 'hurricane'], ['airslash', 'bravebird', 'hurricane']],
        ['knockoff', 'foulplay'],
        ['throatchop', ['crunch', 'lashout']],
        ['doubleedge', ['bodyslam', 'headbutt']],
        ['fireblast', ['fierydance', 'flamethrower']],
        ['lavaplume', 'magmastorm'],
        ['thunderpunch', 'wildcharge'],
        ['gunkshot', ['direclaw', 'poisonjab', 'sludgebomb']],
        ['aurasphere', 'focusblast'],
        ['closecombat', 'drainpunch'],
        ['bugbite', 'pounce'],
        [['dragonpulse', 'spacialrend'], 'dracometeor'],
        ['alluringvoice', 'dazzlinggleam'],
        ['taunt', 'disable'],
        ['toxic', ['willowisp', 'thunderwave']],
        [['thunderwave', 'toxic', 'willowisp'], 'toxicspikes'],
    ]

    for pair in incompatible_pairs:
        incompatible_moves(moves, move_pool, pair[0], pair[1])

    if 'Ice' not in types:
        incompatible_moves(moves, move_pool, 'icebeam', 'icywind')

    incompatible_moves(moves, move_pool, ['taunt', 'strengthsap'], 'encore')

    if 'Dark' not in types and tera_type != 'Dark':
        incompatible_moves(moves, move_pool, 'knockoff', 'suckerpunch')

    if 'Prankster' not in abilities:
        incompatible_moves(moves, move_pool, 'thunderwave', 'yawn')

    if species['id'] == 'luvdisc':
        incompatible_moves(moves, move_pool, ['charm', 'flipturn', 'icebeam'], ['charm', 'flipturn'])

    if species['id'] == "cyclizar":
        incompatible_moves(moves, move_pool, 'taunt', 'knockoff')

    if species['baseSpecies'] == 'Dudunsparce':
        incompatible_moves(moves, move_pool, 'earthpower', 'shadowball')

    if species['id'] == 'mesprit':
        incompatible_moves(moves, move_pool, 'healingwish', 'uturn')

def add_move(move, moves, types, abilities, teamDetails, species, movePool, teraType,role):
    moves.add(move)
    movePool.remove(move)
    counter = query_moves(moves, species, teraType, abilities)
    cull_move_pool(types, moves, abilities, counter, movePool, teamDetails, species, teraType, role)
    return counter

def random_moveset(types: List[str], abilities: Set[str], team_details: Dict, species: Dict, move_pool: List[str], tera_type: str, role: str) -> Set[str]:
    moves = set()
    counter = query_moves(moves, species, tera_type, abilities)
    cull_move_pool(types, moves, abilities, counter, move_pool, team_details, species, tera_type, role)

    # If there are only four moves, add all moves and return early
    if len(move_pool) <= MAX_MOVE_COUNT:
        moves.update(move_pool)
        return moves

    def move_enforcement_checker(pokemon_type, move_pool, moves, abilities, types, counter, species, team_details):
        if pokemon_type == 'Bug':
            return 'megahorn' in move_pool or 'xscissor' in move_pool or (not counter.get('Bug') and 'Electric' in types)
        elif pokemon_type == 'Dark':
            return not counter.get('Dark')
        elif pokemon_type == 'Dragon':
            return not counter.get('Dragon')
        elif pokemon_type == 'Electric':
            return not counter.get('Electric')
        elif pokemon_type == 'Fairy':
            return not counter.get('Fairy')
        elif pokemon_type == 'Fighting':
            return not counter.get('Fighting')
        elif pokemon_type == 'Fire':
            return not counter.get('Fire')
        elif pokemon_type == 'Flying':
            return not counter.get('Flying')
        elif pokemon_type == 'Ghost':
            return not counter.get('Ghost')
        elif pokemon_type == 'Grass':
            return not counter.get('Grass') and ('leafstorm' in move_pool or species['baseStats']['atk'] >= 100 or 'Electric' in types or 'Seed Sower' in abilities)
        elif pokemon_type == 'Ground':
            return not counter.get('Ground')
        elif pokemon_type == 'Ice':
            return 'freezedry' in move_pool or 'blizzard' in move_pool or not counter.get('Ice')
        elif pokemon_type == 'Normal':
            return 'boomburst' in move_pool or 'hypervoice' in move_pool
        elif pokemon_type == 'Poison':
            if 'Ground' in types:
                return False
            return not counter.get('Poison')
        elif pokemon_type == 'Psychic':
            if counter.get('Psychic'):
                return False
            if 'calmmind' in move_pool or 'Strong Jaw' in abilities:
                return True
            return 'Psychic Surge' in abilities or any(m in types for m in ['Electric', 'Fighting', 'Fire', 'Grass', 'Poison'])
        elif pokemon_type == 'Rock':
            return not counter.get('Rock') and species.baseStats.atk >= 80
        elif pokemon_type == 'Steel':
            return not counter.get('Steel') and (species.baseStats.atk >= 90 or 'gigatonhammer' in move_pool or 'makeitrain' in move_pool)
        elif pokemon_type == 'Water':
            return not counter.get('Water') and 'Ground' not in types
        else:
            return False  # Handle other types or return a default value

    if role == 'Tera Blast user':
        counter = add_move('terablast', moves, types, abilities, team_details, species, 
                                move_pool, tera_type, role)
    # Add required move (e.g., Relic Song for Meloetta-P)
    if species.get('requiredMove'):
        move = move_dex.get(species['requiredMove'])['id']
        counter = add_move(move, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Add other moves you really want to have, e.g., STAB, recovery, setup.

    # Enforce Facade if Guts is a possible ability
    if 'facade' in move_pool and 'Guts' in abilities:
        counter = add_move('facade', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Night Shade, Revelation Dance, Revival Blessing, and Sticky Web
    for moveid in ['nightshade', 'revelationdance', 'revivalblessing', 'stickyweb']:
        if moveid in move_pool:
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Trick Room on Doubles Wallbreaker
    if 'trickroom' in move_pool and role == 'Doubles Wallbreaker':
        counter = add_move('trickroom', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce hazard removal on Bulky Support if the team doesn't already have it
    if role == 'Bulky Support' and not team_details.get('defog') and not team_details.get('rapidSpin'):
        if 'rapidspin' in move_pool:
            counter = add_move('rapidspin', moves, types, abilities, team_details, species, move_pool, tera_type, role)
        if 'defog' in move_pool:
            counter = add_move('defog', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Knock Off on pure Normal- and Fighting-types in singles
    if len(types) == 1 and ('Normal' in types or 'Fighting' in types):
        if 'knockoff' in move_pool:
            counter = add_move('knockoff', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Flip Turn on pure Water-type Wallbreakers
    if len(types) == 1 and 'Water' in types and role == 'Wallbreaker':
        if 'flipturn' in move_pool:
            counter = add_move('flipturn', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Spore on Smeargle
    if species.get('id') == 'smeargle':
        if 'spore' in move_pool:
            counter = add_move('spore', moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce STAB priority
    if role in ['Bulky Attacker', 'Bulky Setup', 'Wallbreaker', 'Doubles Wallbreaker'] or \
            species['id'] in PRIORITY_POKEMON:
        priority_moves = []
        for moveid in move_pool:
            move = move_dex.get(moveid)
            move_type = get_move_type(move, species, abilities, tera_type)
            if types and move_type in types and (move.get('priority', 0) > 0 or
                                                    (moveid == 'grassyglide' and 'Grassy Surge' in abilities)) and (
                    move.get('basePower') or move.get('basePowerCallback')):
                priority_moves.append(moveid)
        if priority_moves:
            moveid = random.choice(priority_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce STAB
    for move_type in types:
        # Check if a STAB move of that type should be required
        stab_moves = [moveid for moveid in move_pool if not moveid in NO_STAB and
                        (move_dex.get(moveid).get('basePower') or
                        move_dex.get(moveid).get('basePowerCallback')) and
                        get_move_type(move_dex.get(moveid), species, abilities, tera_type) == move_type]
        while move_enforcement_checker(move_type, move_pool, moves, abilities, types, counter, species, team_details):
            if not stab_moves:
                break
            random.shuffle(stab_moves)
            moveid = stab_moves.pop()
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Tera STAB
    if not counter.get('stabtera') and role not in ['Bulky Support', 'Doubles Support']:
        stab_moves = [moveid for moveid in move_pool if not moveid in NO_STAB and
                        (move_dex.get(moveid).get('basePower') or
                        move_dex.get(moveid).get('basePowerCallback')) and
                        get_move_type(move_dex.get(moveid), species, abilities, tera_type) == tera_type]
        if stab_moves:
            moveid = random.choice(stab_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # If no STAB move was added, add a STAB move
    if not counter.get('stab'):
        stab_moves = [moveid for moveid in move_pool if not moveid in NO_STAB and
                        (move_dex.get(moveid).get('basePower') or
                        move_dex.get(moveid).get('basePowerCallback')) and
                        get_move_type(move_dex.get(moveid), species, abilities, tera_type) in types]
        if stab_moves:
            moveid = random.choice(stab_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce recovery
    if role in ['Bulky Support', 'Bulky Attacker', 'Bulky Setup']:
        recovery_moves = [moveid for moveid in move_pool if moveid in RECOVERY_MOVES]
        if recovery_moves:
            moveid = random.choice(recovery_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce setup
    if role and ('Setup' in role or role == 'Tera Blast user'):
        # First, try to add a non-Speed setup move
        non_speed_setup_moves = [moveid for moveid in move_pool if moveid in SETUP and moveid not in SPEED_SETUP]
        if non_speed_setup_moves:
            moveid = random.choice(non_speed_setup_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)
        else:
            # No non-Speed setup moves, so add any (Speed) setup move
            setup_moves = [moveid for moveid in move_pool if moveid in SETUP]
            if setup_moves:
                moveid = random.choice(setup_moves)
                counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce Protect
    if 'Protect' in role:
        protect_moves = [moveid for moveid in move_pool if moveid in PROTECT_MOVES]
        if protect_moves:
            moveid = random.choice(protect_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce a move not on the noSTAB list
    if not counter.get('damaging_moves'):
        # Choose an attacking move
        attacking_moves = [moveid for moveid in move_pool if not moveid in NO_STAB and
                            (move_dex.get(moveid).get('category') != 'Status')]
        if attacking_moves:
            moveid = random.choice(attacking_moves)
            counter = add_move(moveid, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Enforce coverage move
    if role not in ['AV Pivot', 'Fast Support', 'Bulky Support', 'Bulky Protect', 'Doubles Support']:
        if len(counter['damaging_moves']) == 1:
            # Find the type of the current attacking move
            current_attack_type = list(counter['damaging_moves'])[0]['type']
            # Choose an attacking move that is of a different type than the current single attack
            coverage_moves = []
            for move_id in move_pool:
                move = move_dex.get(move_id)
                move_type = get_move_type(move, species, abilities, tera_type)
                if move_id not in NO_STAB and (move.get('basePower') or move.get('basePowerCallback')):
                    if current_attack_type != move_type:
                        coverage_moves.append(move_id)
            if coverage_moves:
                move_id = random.choice(coverage_moves)
                counter = add_move(move_id, moves, types, abilities, team_details, species, move_pool, tera_type, role)

    # Add (len(moves) < self.MAX_MOVE_COUNT) as a condition if moves is getting larger than 4 moves.
    # If you want moves to be favored but not required, add something like "and self.random_chance(1, 2)" to your condition.

    # Choose remaining moves randomly from movepool and add them to moves list:
    while len(moves) < MAX_MOVE_COUNT and move_pool:
        if len(moves) + len(move_pool) <= MAX_MOVE_COUNT:
            moves.update(move_pool)
            break
        move_id = random.choice(move_pool)
        counter = add_move(move_id, moves, types, abilities, team_details, species, move_pool, tera_type, role)
        for pair in MOVE_PAIRS:
            if move_id == pair[0] and pair[1] in move_pool:
                counter = add_move(pair[1], moves, types, abilities, team_details, species, move_pool, tera_type, role)
            elif move_id == pair[1] and pair[0] in move_pool:
                counter = add_move(pair[0], moves, types, abilities, team_details, species, move_pool, tera_type, role)

    return moves


def should_cull_ability(ability, types, moves, abilities, counter, team_details, species, tera_type, role):
    if ability in ['Armor Tail', 'Battle Bond', 'Early Bird', 'Flare Boost', 'Galvanize', 'Gluttony', 'Harvest', 'Hydration', 'Ice Body', 'Immunity',
                   'Liquid Voice', 'Marvel Scale', 'Misty Surge', 'Moody', 'Pressure', 'Quick Feet', 'Rain Dish', 'Sand Veil', 'Shed Skin',
                   'Sniper', 'Snow Cloak', 'Steadfast', 'Steam Engine', 'Sweet Veil']:
        return True

    # Abilities which are primarily useful for certain moves
    if ability in ['Contrary', 'Serene Grace', 'Skill Link', 'Strong Jaw']:
        return not counter.get(norm_name(ability))
    elif ability == 'Chlorophyll':
        return not ('sunnyday' in moves or team_details.sun or species['id'] == 'lilligant')
    elif ability == 'Cloud Nine':
        return species['id'] != 'golduck'
    elif ability == 'Competitive':
        return species['id'] == 'kilowattrel'
    elif ability in ['Compound Eyes', 'No Guard']:
        return not counter.get('inaccurate')
    elif ability == 'Cursed Body':
        return 'Infiltrator' in abilities
    elif ability == 'Defiant':
        return not counter.get('Physical') or ('Prankster' in abilities and ('thunderwave' in moves or 'taunt' in moves))
    elif ability == 'Flame Body':
        return species['id'] == 'magcargo' and 'shellsmash' in moves
    elif ability == 'Flash Fire':
        return any(ability in abilities for ability in ['Drought', 'Flame Body', 'Intimidate', 'Rock Head', 'Weak Armor']) and get_effectiveness('Fire', species) < 0
    elif ability == 'Guts':
        return 'facade' not in moves and 'sleeptalk' not in moves
    elif ability == 'Hustle':
        # Some of this is just for Delibird in singles/doubles
        return not counter.get('Physical') or 'fakeout' in moves or 'rapidspin' in moves
    elif ability == 'Insomnia':
        return role == 'Wallbreaker'
    elif ability == 'Intimidate':
        if 'Hustle' in abilities:
            return True
        if 'Sheer Force' in abilities and counter.get('sheerforce'):
            return True
        if species['id'] == 'hitmontop' and 'tripleaxel' in moves:
            return True
        return 'Stakeout' in abilities
    elif ability == 'Iron Fist':
        return not counter.ironfist or 'dynamicpunch' in moves
    elif ability == 'Justified':
        return not counter.get('Physical')
    elif ability in ['Libero', 'Protean']:
        return role == 'Offensive Protect' or (species['id'] == 'meowscarada' and role == 'Fast Attacker')
    elif ability == 'Lightning Rod':
        return species['id'] == 'rhyperior'
    elif ability == 'Mold Breaker':
        return any(ability in abilities for ability in ['Pickpocket', 'Sharpness', 'Sheer Force', 'Unburden'])
    elif ability == 'Moxie':
        return not counter.get('Physical') or 'stealthrock' in moves
    elif ability == 'Natural Cure':
        return species['id'] == 'pawmot'
    elif ability == 'Neutralizing Gas':
        return True
    elif ability == 'Overcoat':
        return 'Grass' in types
    elif ability == 'Overgrow':
        return not counter.get('Grass')
    elif ability == 'Own Tempo':
        return True
    elif ability == 'Prankster':
        return not counter.get('Status') or (species['id'] == 'grafaiai' and role == 'Setup Sweeper')
    elif ability == 'Reckless':
        return not counter.get('recoil')
    elif ability == 'Regenerator':
        return species['id'] == 'mienshao' and role == 'Wallbreaker'
    elif ability == 'Rock Head':
        return not counter.get('recoil')
    elif ability in ['Sand Force', 'Sand Rush']:
        return not team_details.sand
    elif ability == 'Sap Sipper':
        return species['id'] == 'wyrdeer'
    elif ability == 'Seed Sower':
        return role == 'Bulky Support'
    elif ability == 'Sheer Force':
        braviary_case = species['id'] == 'braviaryhisui' and (role == 'Wallbreaker' or role == 'Bulky Protect')
        abilities_case = 'Guts' in abilities or 'Sharpness' in abilities
        moves_case = 'bellydrum' in moves or 'flamecharge' in moves
        return not counter.get('sheerforce') or braviary_case or abilities_case or moves_case
    elif ability == 'Slush Rush':
        return not team_details['snow']
    elif ability == 'Solar Power':
        return not team_details['sun'] or not counter.get('Special')
    elif ability == 'Speed Boost':
        return species['id'] == 'yanmega' and 'protect' not in moves
    elif ability == 'Sticky Hold':
        return species['id'] == 'muk'
    elif ability == 'Sturdy':
        return counter.get('recoil') and species['id'] != 'skarmory'
    elif ability == 'Swarm':
        return not counter.get('Bug') or counter.get('recovery')
    elif ability == 'Swift Swim':
        return 'Intimidate' in abilities or ('raindance' not in moves and not team_details['rain'])
    elif ability == 'Synchronize':
        return species['id'] not in ['umbreon', 'rabsca']
    elif ability == 'Technician':
        return not counter.get('technician') or 'Punk Rock' in abilities or 'Fur Coat' in abilities
    elif ability == 'Tinted Lens':
        hbraviary_case = species['id'] == 'braviaryhisui' and (role == 'Setup Sweeper' or role == 'Doubles Wallbreaker')
        yanmega_case = species['id'] == 'yanmega' and 'protect' in moves
        return yanmega_case or hbraviary_case or species['id'] == 'illumise'
    elif ability == 'Unaware':
        return species['id'] == 'clefable' and role != 'Bulky Support'
    elif ability == 'Unburden':
        return 'Prankster' in abilities or not counter.get('setup') or species['id'] == 'sceptile'
    elif ability == 'Volt Absorb':
        if 'Iron Fist' in abilities and counter.get('ironfist') >= 2:
            return True
        return get_effectiveness('Electric', species) < -1
    elif ability == 'Water Absorb':
        return species['id'] in ['lanturn', 'politoed', 'quagsire'] or 'raindance' in moves
    elif ability == 'Weak Armor':
        return 'shellsmash' in moves and species['id'] != 'magcargo'

    return False


def get_ability(types: List[str], moves: Set[str], abilities: Set[str], counter, team_details, species, tera_type, role):
    ability_data = [ability_dex.get(norm_name(a)) for a in abilities]
    ability_data.sort(key=lambda abil: -abil['rating'])

    if len(ability_data) <= 1:
        return ability_data[0]['name']

    # Hard-code abilities here
    if species['id'] == 'florges':
        return 'Flower Veil'
    if species['id'] == 'bombirdier' and not counter.get('Rock'):
        return 'Big Pecks'
    if species['id'] == 'scovillain':
        return 'Chlorophyll'
    if species['id'] == 'empoleon':
        return 'Competitive'
    if species['id'] == 'swampert' and not counter.get('Water') and 'flipturn' not in moves:
        return 'Damp'
    if species['id'] == 'dodrio':
        return 'Early Bird'
    if species['id'] == 'chandelure':
        return 'Flash Fire'
    if species['id'] == 'golemalola' and 'doubleedge' in moves:
        return 'Galvanize'
    if 'Guts' in abilities and ('facade' in moves or 'sleeptalk' in moves or species['id'] == 'gurdurr'):
        return 'Guts'
    if species['id'] == 'copperajah' and 'heavyslam' in moves:
        return 'Heavy Metal'
    if species['id'] == 'jumpluff':
        return 'Infiltrator'
    if species['id'] == 'toucannon' and not counter.get('skilllink'):
        return 'Keen Eye'
    if species['id'] == 'reuniclus':
        return 'Magic Guard'
    if species['id'] == 'smeargle' and not counter.get('technician'):
        return 'Own Tempo'
    # If Ambipom doesn't qualify for Technician, Skill Link is useless on it
    if species['id'] == 'ambipom' and not counter.get('technician'):
        return 'Pickup'
    if species['id'] == 'zebstrika':
        return 'Sap Sipper' if 'wildcharge' in moves else 'Lightning Rod'
    if species['id'] == 'sandaconda' or (species['id'] == 'scrafty' and 'rest' in moves):
        return 'Shed Skin'
    if species['id'] == 'cetitan' and (role == 'Wallbreaker'):
        return 'Sheer Force'
    if species['id'] == 'cinccino':
        return 'Skill Link' if role == 'Wallbreaker' else 'Technician'
    if species['id'] == 'dipplin':
        return 'Sticky Hold'
    if species['id'] == 'breloom':
        return 'Technician'
    if species['id'] == 'shiftry' and 'tailwind' in moves:
        return 'Wind Rider'

    # Singles
    if species['id'] == 'hypno':
        return 'Insomnia'
    if species['id'] == 'staraptor':
        return 'Reckless'
    if species['id'] == 'arcaninehisui':
        return 'Rock Head'
    if species['id'] in ['raikou', 'suicune', 'vespiquen']:
        return 'Pressure'
    if species['id'] == 'enamorus' and 'calmmind' in moves:
        return 'Cute Charm'
    if species['id'] == 'klawf' and role == 'Setup Sweeper':
        return 'Anger Shell'
    if 'Cud Chew' in abilities and 'substitute' in moves:
        return 'Cud Chew'
    if 'Harvest' in abilities and ('protect' in moves or 'substitute' in moves):
        return 'Harvest'
    if 'Serene Grace' in abilities and 'headbutt' in moves:
        return 'Serene Grace'
    if 'Own Tempo' in abilities and 'petaldance' in moves:
        return 'Own Tempo'
    if 'Slush Rush' in abilities and 'snowscape' in moves:
        return 'Slush Rush'
    if 'Soundproof' in abilities and ('substitute' in moves or counter.get('setup')):
            return 'Soundproof'

    ability_allowed = []
    # Obtain a list of abilities that are allowed (not culled)
    for ability in ability_data:
        if ability['rating'] >= 1 and not should_cull_ability(
            ability['name'], types, moves, abilities, counter, team_details, species, tera_type, role
        ):
            ability_allowed.append(ability)

    # If all abilities are rejected, re-allow all abilities
    if not ability_allowed:
        for ability in ability_data:
            if ability['rating'] > 0:
                ability_allowed.append(ability)
        if not ability_allowed:
            ability_allowed = ability_data

    if len(ability_allowed) == 1:
        return ability_allowed[0]['name']

    # Sort abilities by rating with an element of randomness
    # All three abilities can be chosen
    if len(ability_allowed) == 3 and ability_allowed[0]['rating'] - 0.5 <= ability_allowed[2]['rating']:
        if ability_allowed[1]['rating'] <= ability_allowed[2]['rating']:
            if random.random() < 1/2:
                ability_allowed[1], ability_allowed[2] = ability_allowed[2], ability_allowed[1]
        else:
            if random.random() < 1/3:
                ability_allowed[1], ability_allowed[2] = ability_allowed[2], ability_allowed[1]
        if ability_allowed[0]['rating'] <= ability_allowed[1]['rating']:
            if random.random() < 2/3:
                ability_allowed[0], ability_allowed[1] = ability_allowed[1], ability_allowed[0]
        else:
            if random.random() < 1/2:
                ability_allowed[0], ability_allowed[1] = ability_allowed[1], ability_allowed[0]
    else:
        # Third ability cannot be chosen
        if ability_allowed[0]['rating'] <= ability_allowed[1]['rating']:
            if random.random() < 1/2:
                ability_allowed[0], ability_allowed[1] = ability_allowed[1], ability_allowed[0]
        elif ability_allowed[0]['rating'] - 0.5 <= ability_allowed[1]['rating']:
            if random.random() < 1/3:
                ability_allowed[0], ability_allowed[1] = ability_allowed[1], ability_allowed[0]

    # After sorting, choose the first ability
    return ability_allowed[0]['name']


import random

def get_priority_item(ability, types, moves, counter, team_details, species, tera_type, role):
    def sample(items):
        return random.choice(items)

    if role == 'Bulky Setup' and (ability == 'Quark Drive' or ability == 'Protosynthesis'):
        return 'Booster Energy'
    if species['id'] == 'lokix':
        return 'Silver Powder' if role == 'Fast Attacker' else 'Life Orb'

    if 'requiredItems' in species:
        # Z-Crystals aren't available in Gen 9, so require Plates
        if species['baseSpecies'] == 'Arceus':
            return species['requiredItems'][0]
        return sample(species['requiredItems'])

    if role == 'AV Pivot':
        return 'Assault Vest'
    if species['id'] == 'pikachu':
        return 'Light Ball'
    if species['id'] == 'regieleki':
        return 'Magnet'
    if species['id'] == 'smeargle':
        return 'Focus Sash'
    if species['id'] == 'froslass':
        return 'Wide Lens'
    if moves.intersection({'clangoroussoul', 'shiftgear'}):
        return 'Throat Spray'
    if moves.intersection({'lastrespects', 'dragonenergy'}):
        return 'Choice Scarf'
    if ability == 'Imposter' or \
            (species['id'] == 'magnezone' and moves.intersection({'bodypress'})):
        return 'Choice Scarf'
    if species['id'] == 'rampardos' and (role == 'Fast Attacker'):
        return 'Choice Scarf'
    if species['id'] == 'reuniclus':
        return 'Life Orb'
    if species['id'] == 'luvdisc' and 'substitute' in moves:
        return 'Heavy-Duty Boots'
    if moves.intersection({'bellydrum', 'substitute'}):
        return 'Salac Berry'
    if ability in {'Cheek Pouch', 'Cud Chew', 'Harvest', 'Ripen'} or \
            moves.intersection({'bellydrum', 'filletaway'}):
        return 'Sitrus Berry'
    if moves.intersection({'healingwish', 'switcheroo', 'trick'}):
        if 60 <= species['baseStats']['spe'] <= 108 and \
                role not in {'Wallbreaker', 'Doubles Wallbreaker'} and not counter.get('priority'):
            return 'Choice Scarf'
        else:
            return 'Choice Band' if counter.get('Physical') > counter.get('Special') else 'Choice Specs'
    if species['id'] == 'scyther':
        return 'Eviolite' if 'uturn' not in moves else 'Heavy-Duty Boots'
    if species['nfe']:
        return 'Eviolite'
    if ability == 'Poison Heal':
        return 'Toxic Orb'
    if (ability == 'Guts' or 'facade' in moves) and 'sleeptalk' not in moves:
        return 'Toxic Orb' if 'Fire' in types or ability == 'Toxic Boost' else 'Flame Orb'
    if ability == 'Sheer Force' and counter.get('sheerforce'):
        return 'Life Orb'
    if ability == 'Anger Shell':
        return sample(['Rindo Berry', 'Passho Berry', 'Scope Lens', 'Sitrus Berry'])
    if 'courtchange' in moves:
        return 'Heavy-Duty Boots'
    if 'populationbomb' in moves:
        return 'Wide Lens'
    if (moves.intersection({'scaleshot'}) or
            (species['id'] == 'torterra') or
            (species['id'] == 'cinccino' and role != 'Wallbreaker')):
        return 'Loaded Dice'
    if ability == 'Unburden':
        return 'White Herb' if moves.intersection({'closecombat', 'leafstorm'}) else 'Sitrus Berry'
    if moves.intersection({'shellsmash'}) and ability != 'Weak Armor':
        return 'White Herb'
    if moves.intersection({'meteorbeam'}) or (moves.intersection({'electroshot'}) and not team_details['rain']):
        return 'Power Herb'
    if moves.intersection({'acrobatics'}) and ability != 'Protosynthesis':
        return ''
    if moves.intersection({'auroraveil'}) or (moves.intersection({'lightscreen'}) and moves.intersection({'reflect'})):
        return 'Light Clay'
    if ability == 'Gluttony':
        return f'{sample(["Aguav", "Figy", "Iapapa", "Mago", "Wiki"])} Berry'
    if ('rest' in moves) and ('sleeptalk' not in moves) and \
            ability not in {'Natural Cure', 'Shed Skin'}:
        return 'Chesto Berry'
    if species['id'] != 'yanmega' and \
            get_effectiveness('Rock', species) >= 2 and \
            ('Flying' not in types):
        return 'Heavy-Duty Boots'


import random

def get_item(ability, types, moves, counter, team_details, species, tera_type, role):
    def random_chance(numerator, denominator):
        return random.random() < numerator / denominator

    if 'Normal' in types and 'fakeout' in moves:
        return 'Silk Scarf'

    if species['id'] != 'jirachi' and counter.get('Physical') >= 4 and all(m not in moves for m in
                                                                         ['fakeout', 'firstimpression', 'flamecharge', 'rapidspin', 'ruination', 'superfang']):
        scarf_reqs = (
                role != 'Wallbreaker' and
                (species['baseStats']['atk'] >= 100 or ability == 'Huge Power' or ability == 'Pure Power') and
                60 <= species['baseStats']['spe'] <= 108 and
                ability != 'Speed Boost' and not counter.get('priority') and 'aquastep' not in moves
        )
        return 'Choice Scarf' if scarf_reqs and random_chance(1, 2) else 'Choice Band'

    if counter.get('Special') >= 4 or (counter.get('Special') >= 3 and any(m in moves for m in ['flipturn', 'partingshot', 'uturn'])):
        scarf_reqs = (
                role != 'Wallbreaker' and
                species['baseStats']['spa'] >= 100 and
                60 <= species['baseStats']['spe'] <= 108 and
                ability != 'Speed Boost' and ability != 'Tinted Lens' and not counter.get('Physical')
        )
        return 'Choice Scarf' if scarf_reqs and random_chance(1, 2) else 'Choice Specs'

    if counter.get('speedsetup') and role == 'Bulky Setup':
        return 'Weakness Policy'

    if not counter.get('Status') and ('rapidspin' in moves or role not in ['Fast Attacker', 'Wallbreaker', 'Tera Blast user']):
        return 'Assault Vest'

    if species['id'] == 'golem':
        return 'Weakness Policy' if counter.get('speedsetup') else 'Custap Berry'

    if species['id'] == 'urshifurapidstrike':
        return 'Punching Glove'

    if species['id'] == 'palkia':
        return 'Lustrous Orb'

    if 'substitute' in moves:
        return 'Leftovers'

    if 'stickyweb' in moves and species['id'] != 'araquanid':
        return 'Focus Sash'

    if get_effectiveness('Rock', species) >= 1:
        return 'Heavy-Duty Boots'

    if ('chillyreception' in moves or (
            role == 'Fast Support' and
            any(m in moves for m in PIVOT_MOVES + ['defog', 'mortalspin', 'rapidspin']) and
            'Flying' not in types and ability != 'Levitate'
    )):
        return 'Heavy-Duty Boots'

    # Low Priority
    if (
            (species['id'] == 'garchomp' and role == 'Fast Support') or (
            ability == 'Regenerator' and (role == 'Bulky Support' or role == 'Bulky Attacker') and
            (species['baseStats']['hp'] + species['baseStats']['def']) >= 180 and random_chance(1, 2)
    )):
        return 'Rocky Helmet'

    if 'outrage' in moves:
        return 'Lum Berry'

    if 'protect' in moves:
        return 'Leftovers'

    if role == 'Fast Support' and \
            not counter.get('recovery') and not counter.get('recoil') and \
            (species['baseStats']['hp'] + species['baseStats']['def'] + species['baseStats']['spd']) < 258:
        return 'Focus Sash'

    if (
            role not in ['Fast Attacker', 'Wallbreaker', 'Tera Blast user'] and
            ability != 'Levitate' and
            get_effectiveness('Ground', species) >= 2
    ):
        return 'Air Balloon'

    if role in ['Bulky Attacker', 'Bulky Support', 'Bulky Setup']:
        return 'Leftovers'

    if species['id'] == 'pawmot' and 'nuzzle' in moves:
        return 'Leppa Berry'

    if (
            role in ['Fast Bulky Setup', 'Fast Attacker', 'Setup Sweeper', 'Wallbreaker'] and
            'Dark' in types and 'suckerpunch' in moves and
            species['id'] not in PRIORITY_POKEMON and
            counter.get('physicalsetup') and 'Dark' in counter
    ):
        return 'Black Glasses'

    if role in ['Fast Support', 'Fast Bulky Setup']:
        return 'Life Orb' if counter.get('Physical') + counter.get('Special') >= 3 and 'nuzzle' not in moves else 'Leftovers'

    if role == 'Tera Blast user' and species['id'] in DEFENSIVE_TERA_BLAST_USERS:
        return 'Leftovers'

    if (
            all(m not in moves for m in ['flamecharge', 'rapidspin', 'trailblaze']) and
            role in ['Fast Attacker', 'Setup Sweeper', 'Tera Blast user', 'Wallbreaker']
    ):
        return 'Life Orb'

    return 'Leftovers'



def random_set(mon, team_details):
    s, f = norm_name(mon.name), norm_name(mon.form)
    species = species_dex[f if f in species_dex else s]

    sets = random_sets[species['id']]['sets']
    possible_sets = []

    for moveset in sets:
        # Prevent Tera Blast user if the team already has one, or if Terastallizion is prevented.
        if team_details.get('teraBlast') and moveset["role"] == 'Tera Blast user':
            continue
        possible_sets.append(moveset)

    moveset = random.choice(possible_sets)
    role = moveset["role"]
    move_pool = [norm_name(movename) for movename in moveset["movepool"]]
    tera_types = moveset["teraTypes"]
    tera_type = random.choice(tera_types)

    ability = ''
    item = None

    evs = {'hp': 85, 'atk': 85, 'def': 85, 'spa': 85, 'spd': 85, 'spe': 85}
    ivs = {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}

    types = species['types']
    abilities = set(species['abilities'].values())
    if species.get('unreleased_hidden'):
        abilities.remove(species['abilities']['H'])

    # Get moves
    moves = random_moveset(types, abilities, team_details, species, move_pool, tera_type, role)
    counter = query_moves(moves, species, tera_type, abilities)

    # Get ability
    ability = get_ability(types, moves, abilities, counter, team_details, species, tera_type, role)

    # Get items
    # First, the priority items
    item = get_priority_item(ability, types, moves, counter, team_details, species, tera_type, role)
    if item is None:
        item = get_item(ability, types, moves, counter, team_details, species, tera_type, role)

    # Shuffle moves to add more randomness to camomons
    shuffled_moves = list(moves)
    random.shuffle(shuffled_moves)

    return {
        'name': species['name'],
        'form': mon.form,
        'moves': shuffled_moves,
        'ability': ability,
        'item': item,
        'teraType': tera_type,
        'role': role
    }

def random_team(team):
    pokemon = []

    team_details = {}


    for mon in team:
        moveset = random_set(team[mon], team_details)
        pokemon.append(moveset)

        if moveset['ability'] == 'Drizzle' or 'raindance' in moveset['moves']:
            team_details['rain'] = 1
        if moveset['ability'] == 'Drought' or moveset['ability'] == 'Orichalcum Pulse' or 'sunnyday' in moveset['moves']:
            team_details['sun'] = 1
        if moveset['ability'] == 'Sand Stream':
            team_details['sand'] = 1
        if moveset['ability'] == 'Snow Warning' or 'snowscape' in moveset['moves'] or 'chillyreception' in moveset['moves']:
            team_details['snow'] = 1
        if 'spikes' in moveset['moves'] or 'ceaselessedge' in moveset['moves']:
            team_details['spikes'] = team_details.get('spikes', 0) + 1
        if 'toxicspikes' in moveset['moves'] or moveset['ability'] == 'Toxic Debris':
            team_details['toxicSpikes'] = team_details.get('toxicSpikes', 0) + 1
        if 'stealthrock' in moveset['moves'] or 'stoneaxe' in moveset['moves']:
            team_details['stealthRock'] = 1
        if 'stickyweb' in moveset['moves']:
            team_details['stickyWeb'] = 1
        if 'defog' in moveset['moves']:
            team_details['defog'] = 1
        if 'rapidspin' in moveset['moves'] or 'mortalspin' in moveset['moves']:
            team_details['rapidSpin'] = 1
        if 'auroraveil' in moveset['moves'] or ('reflect' in moveset['moves'] and 'lightscreen' in moveset['moves']):
            team_details['screens'] = 1
        if moveset['role'] == 'Tera Blast user' or species_dex[norm_name(mon)]['baseSpecies'] in ["Ogerpon", "Terapagos"]:
            team_details['teraBlast'] = 1
    return pokemon
