import sys
sys.path.append("python_scripts")
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
            new_poke.set_region()
            pokemon_list.append(new_poke)
    return pokemon_list

pokemon_file = "Additional_files/pokemon_list.txt"
new_file = "Additional_files/pokemon_temp_list.txt"

pokemon_list = get_pokemon_from_file(pokemon_file)
text = ""
for poke in pokemon_list:
    text = text + poke.to_string() + "\n"
output_file = open(new_file,"w")
output_file.write(text)
output_file.close()