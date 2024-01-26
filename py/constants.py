import json
import requests
import os

data_dir = '../data'
battle_log_dir = os.path.join(data_dir + '/battle_logs')
random_battle_dir = os.path.join(battle_log_dir + '/random_battle')
game = open(f'{random_battle_dir}/random_battle.txt', 'r').read().splitlines()
move_dex = json.load(open(f'{data_dir}/moves_dex.json'))
# data = json.load(open('data/data.json'))
species_dex = json.load(open(f'{data_dir}/species_dex.json'))
ability_dex = json.load(open(f'{data_dir}/ability_dex.json'))
typechart = json.load(open(f'{data_dir}/typechart_dex.json'))
random_sets = requests.request(
    "GET", 'https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/random-sets.json').json()

MAX_MOVE_COUNT = 4

# Moves that restore HP:
RECOVERY_MOVES = [
    'healorder', 'milkdrink', 'moonlight', 'morningsun', 'recover', 'roost', 'shoreup', 'slackoff', 'softboiled', 'strengthsap', 'synthesis',
]
# Moves that drop stats:
CONTRARY_MOVES = [
    'armorcannon', 'closecombat', 'leafstorm', 'makeitrain', 'overheat', 'spinout', 'superpower', 'vcreate',
]
# Moves that boost Attack:
PHYSICAL_SETUP = [
    'bellydrum', 'bulkup', 'coil', 'curse', 'dragondance', 'honeclaws', 'howl', 'meditate', 'poweruppunch', 'swordsdance', 'tidyup', 'victorydance',
]
# Moves which boost Special Attack:
SPECIAL_SETUP = [
    'calmmind', 'chargebeam', 'geomancy', 'nastyplot', 'quiverdance', 'tailglow', 'torchsong',
]
# Moves that boost Attack AND Special Attack:
MIXED_SETUP = [
    'clangoroussoul', 'growth', 'happyhour', 'holdhands', 'noretreat', 'shellsmash', 'workup',
]
# Some moves that only boost Speed:
SPEED_SETUP = [
    'agility', 'autotomize', 'flamecharge', 'rockpolish', 'trailblaze',
]
# Conglomerate for ease of access
SETUP = [
    'acidarmor', 'agility', 'autotomize', 'bellydrum', 'bulkup', 'calmmind', 'clangoroussoul', 'coil', 'cosmicpower', 'curse',
    'dragondance', 'flamecharge', 'growth', 'honeclaws', 'howl', 'irondefense', 'meditate', 'nastyplot', 'noretreat', 'poweruppunch',
    'quiverdance', 'rockpolish', 'shellsmash', 'shiftgear', 'swordsdance', 'tailglow', 'tidyup', 'trailblaze', 'workup', 'victorydance',
]
SPEED_CONTROL = [
    'electroweb', 'glare', 'icywind', 'lowsweep', 'quash', 'rocktomb', 'stringshot', 'tailwind', 'thunderwave', 'trickroom',
]
# Moves that shouldn't be the only STAB moves:
NO_STAB = [
    'accelerock', 'aquajet', 'bounce', 'breakingswipe', 'bulletpunch', 'chatter', 'chloroblast', 'clearsmog', 'covet',
    'dragontail', 'doomdesire', 'electroweb', 'eruption', 'explosion', 'fakeout', 'feint', 'flamecharge', 'flipturn', 'futuresight',
    'grassyglide', 'iceshard', 'icywind', 'incinerate', 'infestation', 'machpunch', 'meteorbeam', 'mortalspin', 'nuzzle', 'pluck', 'pursuit',
    'quickattack', 'rapidspin', 'reversal', 'selfdestruct', 'shadowsneak', 'skydrop', 'snarl', 'strugglebug', 'suckerpunch', 'uturn',
    'vacuumwave', 'voltswitch', 'watershuriken', 'waterspout',
]
# Hazard-setting moves
HAZARDS = [
    'spikes', 'stealthrock', 'stickyweb', 'toxicspikes',
]
# Protect and its variants
PROTECT_MOVES = [
    'banefulbunker', 'burningbulwark', 'protect', 'silktrap', 'spikyshield',
]
# Moves that switch the user out
PIVOT_MOVES = [
    'chillyreception', 'flipturn', 'partingshot', 'shedtail', 'teleport', 'uturn', 'voltswitch',
]

STATUS_MOVES = [move['id']
                for move in move_dex.values() if move['category'] == 'Status']

# Moves that should be paired together when possible
MOVE_PAIRS = [
    ['lightscreen', 'reflect'],
    ['sleeptalk', 'rest'],
    ['protect', 'wish'],
    ['leechseed', 'protect'],
    ['leechseed', 'substitute'],
]

# Pokemon who always want priority STAB, and are fine with it as its only STAB move of that type
PRIORITY_POKEMON = [
    'breloom', 'brutebonnet', 'honchkrow', 'mimikyu', 'scizor',
]

# Pokemon who should never be in the lead slot
NO_LEAD_POKEMON = [
    'Iron Boulder', 'Slither Wing', 'Zacian', 'Zamazenta',
]
DOUBLES_NO_LEAD_POKEMON = [
    'Basculegion', 'Houndstone', 'Roaring Moon', 'Zacian', 'Zamazenta',
]

DEFENSIVE_TERA_BLAST_USERS = [
    'alcremie', 'bellossom', 'comfey', 'florges',
]
