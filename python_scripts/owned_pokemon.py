import sys
from random import randrange, seed
sys.path.append('.')
from python_scripts.pokemon import pokemon
from python_scripts.constants import nature_modifier
seed()
class owned_pokemon:
    def __init__(self, species = None, level = None, shiny_odds = 0, ivs = None, nature = None):
        if ivs == None:
            ivs = {}
        stats = ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
        for stat in stats:
            if not stat in ivs.keys():
                ivs[stat] = None
        self.name = None
        self.level = level
        self.owner = None
        self.OT = None
        if shiny_odds == 0:
            self.shiny = False
        elif randrange(shiny_odds) == 0:
            self.shiny = True
        else:
            self.shiny = False
        if ivs["HP"] == None:
            self.hp_iv = randrange(32)
        else:
            self.hp_iv = ivs["HP"]
        if ivs["Attack"] == None:
            self.attack_iv = randrange(32)
        else:
            self.attack_iv = ivs["Attack"]
        if ivs["Defense"] == None:
            self.defense_iv = randrange(32)
        else:
            self.defense_iv = ivs["Defense"]
        if ivs["Special Attack"] == None:
            self.special_attack_iv = randrange(32)
        else:
            self.special_attack_iv = ivs["Special Attack"]
        if ivs["Special Defense"] == None:
            self.special_defense_iv = randrange(32)
        else:
            self.special_defense_iv = ivs["Special Defense"]
        if ivs["Speed"] == None:
            self.speed_iv = randrange(32)
        else:
            self.speed_iv = ivs["Speed"]
        self.location = None
        self.position = None
        self.pokemon = pokemon(national = species)
        if nature == None:
            natures = list(nature_modifier.keys())
            self.nature = natures[randrange(25)]
        else:
            self.nature = nature