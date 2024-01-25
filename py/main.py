import json
from random_gen_utils import random_team
from constants import *
from parse_utils import Move, Pokemon, Player, Side, Field, get_nth, get_mon, print_state


if __name__ == '__main__':

    # [p1 rating, p2 rating, tier]
    game_metadata = []
    player_names = {}
    players = {}

    for lin_num, line in enumerate(game):
        # Add player ratings and players
        if line[:3] == '|pl':
            game_metadata.append(int(line[-4:]))
            player_names[line[11: line[:-5].rfind('|')]] = line[8:10]
            players[line[8:10]] = Player(line[8:10])
        # Add tier
        elif line[:3] == '|ti':
            game_metadata.append(line[6:])

        # If switch action
        elif line[:3] == '|sw':
            _, player, mon_name, form_name = get_mon(players, line, 'switch')
            if mon_name not in player.team:
                player.team[mon_name] = Pokemon(name=mon_name, form=form_name)

        # Ability
        elif line[:4] == '|-ab':
            p_name, player, mon_name = get_mon(players, line, 'ability')
            player.team[mon_name].ability = line[line.rfind('|') + 1:]

        # Move
        elif line[:3] == '|mo':
            p_name, player, mon_name, move_name = get_mon(
                players, line, 'move')
            mon = player.team[mon_name]
            if move_name not in mon.moves:
                mon.moves[move_name] = Move(move_name)
            mon.moves[move_name].current_pp -= 1
        # # Print for debug
        # elif line[:3] == '|tu':
        #     print_state(line, players)

    print(random_team(players['p1'].team))
