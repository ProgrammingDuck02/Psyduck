import requests, re, mysql.connector

standard_stats = "<td colspan=\"[0-9]\" class=\"fooevo\"><h2>(<b>)?Stats(</b>)?</h2></td></tr><tr>"
galarian_stats = "<td colspan=\"[0-9]\" class=\"fooevo\"><h2>Stats - Galarian [^<]*</h2></td></tr><tr>"
alolan_stats = "<td colspan=\"[0-9]\" class=\"fooevo\"><h2>(<b>)?Stats - Alolan [^<]*(</b>)?</h2></td></tr><tr>"
exceptions = {

}

stats_line = (
    "<tr><td colspan=\"[0-9]\" width=\"14%\" class=\"fooinfo\">Base Stats - Total: [0-9]+</td>",
    "</tr>"
)
def get_stats_by_pokemon(pokemon_name, pokemon_number, dex = "SwSh"):
    if len(pokemon_number) > 3:
        if pokemon_number[3] == 'A':
            form = "alolan"
        elif pokemon_number[3] == 'G':
            form = "galarian"
        else:
            form = "standard"
        number = pokemon_number[:3]
    else:
        form = "standard"
        number = pokemon_number
    if dex == "SwSh":
        pokemon_name = pokemon_name.lower().replace(" ", "")
        url = "https://www.serebii.net/pokedex-swsh/"+pokemon_name+"/"
    else:
        url = "https://www.serebii.net/pokedex-sm/"+number+".shtml"
    try:
        ret = get_stats(url, pokemon_number, form)
    except FileNotFoundError as e:
        if dex == "SwSh":
            ret = get_stats_by_pokemon(pokemon_name, pokemon_number, "sm")
        else:
            raise e
    return ret

def get_stats(url, number, form="standard"):
    request = requests.get(url)
    if not request:
        raise(FileNotFoundError("Something went wrong..."))
    source = request.text
    return get_stats_with_source(source, number, form)

def get_stats_with_source(source, number, form="standard"):
    if number in exceptions.keys():
        stats = exceptions[number]
    elif form == "standard":
        stats = standard_stats
    elif form == "galarian":
        stats = galarian_stats
    elif form == "alolan":
        stats = alolan_stats
    query = re.compile(stats+".*</table>", re.DOTALL)
    temp = query.search(source)
    ret = False
    while(temp):
        ret = temp.group()
        l = len(ret) - 1
        source = ret[:l]
        temp = query.search(source)
    if not ret:
        return False
    query = re.compile(stats_line[0]+".*"+stats_line[1], re.DOTALL)
    temp = query.search(ret)
    ret = False
    while(temp):
        ret = temp.group()
        l = len(ret) - 1
        source = ret[:l]
        temp = query.search(source)
    if not ret:
        raise(Exception("Something went terribly wrong..."))
    ret = ret[(len(stats_line[0])-5):(len(ret)-len(stats_line[1])-5)].replace("<td align=\"center\" class=\"fooinfo\">", "")
    ret = ret.replace("<td colspan=\"3\" width=\"14%\">&nbsp;</td>", "").replace("\r\n", "")
    ret = ret.split("</td>")
    return {"stats": ret, "form": form}

def main():
    DB = mysql.connector.connect(
        host = 'localhost',
        user = 'psyduck',
        password = 'Uqp9MF[jf<!R(%:S',
        database = 'psyduckDB'
        )
    cursor = DB.cursor()
    cursor.execute("SELECT name, national_number FROM pokemon")
    pokemons = cursor.fetchall()
    for poke in pokemons:
        print(poke[0]+"...")
        ret = get_stats_by_pokemon(pokemon_name=poke[0], pokemon_number=poke[1])
        cursor = DB.cursor()
        print(ret, poke)
        cursor.execute("UPDATE pokemon SET hp = "+ret[0]+", attack = "+ret[1]+", defense = "+ret[2]+", special_attack = "+ret[3]+", special_defense = "+ret[4]+", speed = "+ret[5]+" WHERE national_number = \""+poke[1]+"\"")
        DB.commit()

if __name__ == "__main__":
    main()