import os
import subprocess
import asyncio
import poke_env
from dataclasses import dataclass
from typing import Dict, List, Optional
from poke_env.battle import AbstractBattle, Battle, Field, SideCondition, Weather
from poke_env.player import RandomPlayer, Player
from poke_env.player.battle_order import BattleOrder
from poke_env import AccountConfiguration
from poke_env import ServerConfiguration
from funcs import basicFunctionUtil
from funcs import serverLoad
import random
import math

botToFight = ""
botInfo = None
bot = None


#fuck if i know what this means. this is taken from https://github.com/hsahovic/poke-env/blob/master/examples/tracking_observations.py
@dataclass
class TurnSnapshot:
    turn: int
    active_pokemon: Optional[str]
    opponent_active_pokemon: Optional[str]
    team_hp: Dict[str, float]
    opponent_team_hp: Dict[str, float]
    weather: Dict[Weather, int]
    fields: Dict[Field, int]
    side_conditions: Dict[SideCondition, int]
    opponent_side_conditions: Dict[SideCondition, int]

    @classmethod
    def from_battle(cls, battle: Battle):
        return cls(
            turn=battle.turn,
            active_pokemon=(
                battle.active_pokemon.species if battle.active_pokemon else None
            ),
            opponent_active_pokemon=(
                battle.opponent_active_pokemon.species
                if battle.opponent_active_pokemon
                else None
            ),
            team_hp={
                mon.species: mon.current_hp_fraction for mon in battle.team.values()
            },
            opponent_team_hp={
                mon.species: mon.current_hp_fraction
                for mon in battle.opponent_team.values()
            },
            weather=dict(battle.weather),
            fields=dict(battle.fields),
            side_conditions=dict(battle.side_conditions),
            opponent_side_conditions=dict(battle.opponent_side_conditions),
        )
    


#modified base class from that same github
class ObservationTrackingPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observations: Dict[str, List[TurnSnapshot]] = {}

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        assert isinstance(battle, Battle)
        history = self.observations.setdefault(battle.battle_tag, [])
        snapshot = TurnSnapshot.from_battle(battle)
        history.append(snapshot)

        our_hp = snapshot.team_hp[snapshot.active_pokemon]
        opp_hp = snapshot.opponent_team_hp[snapshot.opponent_active_pokemon]
        currentWeather = snapshot.weather
        currentOpponentStatus = snapshot.opponent_side_conditions


        print(
            f"  Turn {snapshot.turn}: "
            f"{snapshot.active_pokemon} ({our_hp:.0%}) vs "
            f"{snapshot.opponent_active_pokemon} ({opp_hp:.0%})"
            )
        


        opponent_mon = battle.opponent_active_pokemon
        active_mon = battle.active_pokemon
        opponentType1Mult = 1.0
        opponentType2Mult = 0.0
        if opponent_mon and active_mon:
            opponentType1Mult = active_mon.damage_multiplier(opponent_mon.type_1)
            if opponent_mon.type_2:
                opponentType2Mult = active_mon.damage_multiplier(opponent_mon.type_2)
            else:
                opponentType2Mult = 0.0


        def chooseBestSwitch():
            switchScores = {}

            for switch_mon in battle.available_switches:
                switchScore = 10.0

                if switch_mon.current_hp_fraction < 0.33:
                    switchScore = 0
                    continue

                #find opponent damage multiplier
                if opponent_mon:
                    opponentType1MultVSwitch = switch_mon.damage_multiplier(opponent_mon.type_1)
                    if opponent_mon.type_2:
                        opponentType2MultVSwitch = switch_mon.damage_multiplier(opponent_mon.type_2)
                    else:
                        opponentType2MultVSwitch = 0

                    #math stuff
                    switchScore = switch_mon.current_hp_fraction * math.floor(5-(max(opponentType1MultVSwitch, opponentType2MultVSwitch) * 0.5))

                    switchScores[switch_mon] = switchScore


            scores = switchScores
            if scores:
                highestSwitchScore = max(scores.values())

                bestSwitches = [mon for mon, score in scores.items() if score == highestSwitchScore]
                chosenSwitch = random.choice(bestSwitches)

                #return best switch
                return chosenSwitch

        #cautious trait code
        if "cautious" in botInfo["personalityChunks"] and active_mon:
            if active_mon.current_hp_fraction <= 0.3 and battle.available_switches:

                chosenSwitch = chooseBestSwitch()

                if chosenSwitch:
                    print(f"We're switching to {chosenSwitch.species}. (Cautious Switch)")
                    return self.create_order(chosenSwitch)
                

        #switches if 4x weakness
        if not "stupid" in botInfo["personalityChunks"] and active_mon and battle.available_switches:
            if max(opponentType1Mult, opponentType2Mult) >= 4:
                chosenSwitch = chooseBestSwitch()

                if chosenSwitch:
                    print(f"We're switching to {chosenSwitch.species}. (4x Switch)")
                    return self.create_order(chosenSwitch)
                

            if active_mon.current_hp_fraction <= 0.4:
                chosenSwitch = chooseBestSwitch()

                #1/3 chance to switch at low HP to avoid infinite roost-offs and the sort
                if chosenSwitch and random.randint(1,3) == 3:
                    print(f"We're switching to {chosenSwitch.species}. (Low Health Switch)")
                    return self.create_order(chosenSwitch)



        #erratic gives a 20% chance to try to switch at random

        if "erratic" in botInfo["personalityChunks"] and active_mon and battle.available_switches:
            if random.randint(1,5) == 5:

                #a further 1/2 chance to make a completely random switch instead of the best possible one
                if random.randint(1,2) == 1:
                    chosenSwitch = chooseBestSwitch()
                    if chosenSwitch:
                        print(f"We're switching to {chosenSwitch.species}. (Erratic Switch, Smart)")
                        return self.create_order(chosenSwitch)

                else:
                    chosenSwitch =  random.choice(battle.available_switches)
                    print(f"We're switching to {chosenSwitch.species}. (Erratic Switch, Random)")
                    return self.create_order(chosenSwitch)
                    



        if not battle.available_moves:
            return self.choose_random_move(battle)
        
        if "random" in botInfo["personalityChunks"]:
            return self.choose_random_move(battle)
        


        #put all the moves in a data w/ scores
        moveScores = {}



        #the actual logic determining their choices
        for move in battle.available_moves:
            score = 10.0



            # unless the bot is marked as stupid
            if "stupid" not in botInfo["personalityChunks"]:
                #

                if opponent_mon and move.type and move.base_power > 0 and "knowledgeable" in botInfo["personalityChunks"]:
                    multiplier = opponent_mon.damage_multiplier(move)
                    if multiplier > 1:
                        #+1 for 2x effective, +4 for 4x
                        score += (multiplier * 0.5) ** 2
                    #if not effective, disregard
                    elif multiplier <= 0.5:
                        score -= 3

                    
                #if immune, disregard attacks
                if opponent_mon and move.type:
                    if opponent_mon.damage_multiplier(move) == 0:
                        score -= 20


                #if opponent is statused, don't do status moves
                if move.status is not None:
                    if opponent_mon and opponent_mon.status is not None:
                        score -= 20


                #disregard self destructing moves at high health, prioritize at low health
                if move.self_destruct and active_mon:
                    if active_mon.current_hp_fraction >= 0.25:
                        score -= 7
                    elif active_mon.current_hp_fraction <= 0.15:
                        score += 5
                
                if move.heal > 0 and active_mon.current_hp_fraction <= 0.4:
                    score += 3

                if move.heal > 0 and active_mon.current_hp_fraction >= 0.7:
                    score -= 10

                if "setup" in botInfo["personalityChunks"]:
                    #slightly prioritizes status moves at high health
                    if move.base_power <= 0 and active_mon.current_hp_fraction >= 0.8:
                        score += 3
                    moveScores[move] = score

                if move.base_power <= 0 and active_mon.current_hp_fraction >= 1:
                    score += 1.5

                if move.base_power <= 0 and active_mon.current_hp_fraction <= 0.75:
                    score -= 2


            #slight negative bias towards low-power offensive moves
            if 0 < move.base_power <= 70 and move.priority < 1:
                score -= 1

            #espeed good
            if move.base_power <= 70 and move.priority >= 1:
                score += 1
            
            #add slight bonus for base power
                score += move.base_power * 0.015


            if "aggressive" in botInfo["personalityChunks"]:
                if move.base_power > 0:
                    score += 1
                if move.base_power > 95:
                    score += 2



            if "worrywart" in botInfo["personalityChunks"]:
                if move.heal > 0 and active_mon.current_hp_fraction <= 0.5:
                    score += 2
                if move.heal > 0 and active_mon.current_hp_fraction <= 0.3:
                    score += 2


            if "erratic" in botInfo["personalityChunks"]:
                score += random.randint(-1, 1)
            

            if "opportunist" in botInfo["personalityChunks"]:
                if move.priority >= 1 and opponent_mon.current_hp_fraction <= 0.2:
                    score += 5


            if "setup" in botInfo["personalityChunks"]:
                #slightly prioritizes status moves at high health
                if move.base_power <= 0 and active_mon.current_hp_fraction >= 0.8:
                    score += 3

            moveScores[move] = score

        
        highestScore = max(moveScores.values())

        # which is the highest scorer?
        bestMoves = [move for move, score in moveScores.items() if score == highestScore]

        # debug print to see what the bot is thinking
        print(f"Move scores: {[f'{m.id}: {s}' for m, s in moveScores.items()]}")
        print(f"Choosing from best options: {[m.id for m in bestMoves]}")


        #pick the best one and send that back
        
        chosenMove = random.choice(bestMoves)
        return self.create_order(chosenMove)

  
        

    def _battle_finished_callback(self, battle: AbstractBattle):
        history = self.observations.pop(battle.battle_tag, [])
        print(f"{battle.battle_tag}: {len(history)} turns recorded")
        for snapshot in history:
            if not snapshot.active_pokemon or not snapshot.opponent_active_pokemon:
                continue
            our_hp = snapshot.team_hp[snapshot.active_pokemon]
            opp_hp = snapshot.opponent_team_hp[snapshot.opponent_active_pokemon]
            print(
                f"  Turn {snapshot.turn}: "
                f"{snapshot.active_pokemon} ({our_hp:.0%}) vs "
                f"{snapshot.opponent_active_pokemon} ({opp_hp:.0%})"
            )







async def main():
    global botToFight, botInfo
    basicFunctionUtil.ping()

    #while we don't have the bot, try to get and load it and if it doesn't work repeat the process
    while not botInfo:
        botToFight = input("please type the name of the configured bot you'd like to fight.\n")
        botInfo = basicFunctionUtil.loadFileAsJSON(f"./bots/{botToFight}.json")
        if botInfo:
            print(f"Bot found!")
        else:
            print("you messed up LOL")

    print(f"bot Name: {botInfo["name"]}")

    serverLoad.fullHousekeeping()
    #Sits for a bit for the server to start up
    await asyncio.sleep(5)
    serverLoad.launchSite()
    
    #tries to open the bot and kills everything if it fails
    try:
        isImpatient = botInfo["impatient"]

        bot = ObservationTrackingPlayer(
            avatar=botInfo["avatar"],
            account_configuration=AccountConfiguration(botInfo["name"], None),
            max_concurrent_battles=1,
            #if impatient, set timer upon launch
            start_timer_on_battle_start=botInfo["impatient"]
        )

        print("bot initialized!\n\n")

    except Exception as e:
        print(f"the bot couldn't be initialized. \n{str(e)}")
        return
        
    print("\nThe bot's now looking to accept a fight. Here's how to fight it:" \
    "\n1. Choose a name in the top right. If it's taken, choose a different name." \
    f"\n2. Click \"Find a User\" on the left, then search \"{botInfo["name"]}\"." \
    "Click \"Challenge\" under their profile, and set the challenge to be a Random Battle (it's that by default.) They should accept.")

    await bot.accept_challenges(None, 1)



    #okay now we're logicing


asyncio.run(main())