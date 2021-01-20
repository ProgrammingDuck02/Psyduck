import sys
sys.path.append(".")
from pokemon import pokemon

def get_pokemon_from_file(filename):
    pokemon_list = []
    file = open(filename,"r")
    text = file.read()
    file.close()
    lines = text.split("\n")
    for line in lines:
        if line.startswith(" \t"):
            line = line[2:]
        if line[1:].startswith("dex"):
            continue
        if line.startswith("Ce/Co/Mo"):
            continue
        new_poke = pokemon()
        new_poke.get_from_string(line)
        if new_poke.regional_number.endswith("Ce"):
            new_poke.regional_number = new_poke.regional_number[:3]
        if new_poke.regional_number.endswith("Mo"):
            new_poke.regional_number = new_poke.regional_number[:3]
        if new_poke.regional_number.endswith("Co"):
            new_poke.regional_number = new_poke.regional_number[:3]
        pokemon_list.append(new_poke)
    return pokemon_list

pokemon_file = "../Additional_files/pokemon_list_original.txt"
new_file = "../Additional_files/pokemon_list.txt"

pokemon_list = get_pokemon_from_file(pokemon_file)
text = ""
for poke in pokemon_list:
    text = text + poke.to_string() + "\n"
output_file = open(new_file,"w")
output_file.write(text)
output_file.close()

