import sys
import os
sys.path.append(".")
from pokemon import pokemon

def get_pokemon_from_file(filename):
    pokemon_list = []
    file = open(filename,"r")
    text = file.read()
    file.close()
    lines = text.split("\n")
    for line in lines:
        new_poke = pokemon()
        if new_poke.get_from_string(line):
            pokemon_list.append(new_poke)
    return pokemon_list

poke_list = "../Additional_files/pokemon_list.txt"
sprites_dir = "../Additional_files/pokemon_sprites/"
shiny_sprites_dir = "../Additional_files/shiny_pokemon_sprites/"
pokemon_list = get_pokemon_from_file(poke_list)
exceptions  = {}
exceptions["083"] = "farfetchd"
exceptions["083G"] = "farfetchd-galar"
exceptions["029"] = "nidoran-f"
exceptions["032"] = "nidoran-m"
exceptions["122"] = "mr-mime"
exceptions["122G"] = "mr-mime-galar"
exceptions["439"] = "mime-jr"
exceptions["669"] = "flabebe"
exceptions["772"] = "type-null"
exceptions["865"] = "sirfetchd"
exceptions["866"] = "mr-rime"
exceptions["785"] = "tapu-koko"
exceptions["786"] = "tapu-lele"
exceptions["787"] = "tapu-bulu"
exceptions["788"] = "tapu-fini"
ekeys = exceptions.keys()
for poke in pokemon_list:
    region = ""
    old_name = None
    for key in ekeys:
        if key == poke.national_number:
            old_name = exceptions[key]
            break
    if old_name == None:
        old_name = poke.name.lower()
        if poke.regional_variant():
            region = "-" + poke.region.lower()
        old_name = old_name + region
    try:
        os.rename(sprites_dir+old_name+".png", sprites_dir+poke.national_number+".png")
    except FileNotFoundError:
        pass
    try:
        os.rename(shiny_sprites_dir+old_name+".png", shiny_sprites_dir+poke.national_number+".png")
    except FileNotFoundError:
        pass