import sys
sys.path.append('.')
from python_scripts.pokemon import pokemon

class owned_pokemon:
    def __init__(self, spieces = None, level = None):
        self.name = None
        self.level = level
        self.owner = None
        self.OT = None
        self.shiny = False
        self.location = None
        self.position = None
        self.pokemon = pokemon(national = spieces)