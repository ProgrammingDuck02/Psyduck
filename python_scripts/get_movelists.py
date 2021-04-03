import requests, re
from xml.sax.saxutils import unescape
import pickle
import mysql.connector
import time
standard_attacks = (
    "<a name=\"attacks\"></a><table class=\"dextable\"><tr ><td colspan=\"10\" class=\"fooevo\"><h3><a name=\"standardlevel\"></a>Standard Level Up</h3></td></tr><tr><th class=\"attheader\">Level</th><th class=\"attheader\">Attack Name</th><th class=\"attheader\">Type</th><th class=\"attheader\">Cat\.</th><th class=\"attheader\">Att\.</th><th class=\"attheader\">Acc\.</th><th class=\"attheader\">PP</th><th class=\"attheader\">Effect %</th></tr>",
    "</table>"
)
galarian_attacks = (
    "<a name=\"attacks\"></a><table class=\"dextable\"><tr ><td colspan=\"10\" class=\"fooevo\"><h3><a name=\"galarianlevel\"></a>Galarian Form Level Up</h3></td></tr><tr><th class=\"attheader\">Level</th><th class=\"attheader\">Attack Name</th><th class=\"attheader\">Type</th><th class=\"attheader\">Cat\.</th><th class=\"attheader\">Att\.</th><th class=\"attheader\">Acc\.</th><th class=\"attheader\">PP</th><th class=\"attheader\">Effect %</th></tr>",
    "</table>"
)
alolan_attacks = (
    "<a name=\"attacks\"></a><table class=\"dextable\"><tr ><td colspan=\"10\" class=\"fooevo\"><h3><a name=\"alolalevel\"></a>Alola Form Level Up</h3></td></tr><tr><th class=\"attheader\">Level</th><th class=\"attheader\">Attack Name</th><th class=\"attheader\">Type</th><th class=\"attheader\">Cat\.</th><th class=\"attheader\">Att\.</th><th class=\"attheader\">Acc\.</th><th class=\"attheader\">PP</th><th class=\"attheader\">Effect %</th></tr>",
    "</table>"
)

types = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy"
]

attack_types = {
    "physical" : "physical",
    "special" : "special",
    "other" : "status"
}

def connect_db():
    global DB, cursor
    DB = mysql.connector.connect(
    host = 'localhost',
    user = 'psyduck',
    password = 'Uqp9MF[jf<!R(%:S',
    database = 'psyduckDB'
    )
    cursor = DB.cursor()

def select(table, values, conditions):
    connect_db()
    global cursor
    if len(values) == 0:
        values = ("*",)
    sql = "SELECT "+values[0]
    for i in range(1,len(values)):
        sql = sql + ", " + values[i]
    sql = sql + " FROM " + table
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
    return cursor.fetchall()

def select_one(table, values, conditions):
    connect_db()
    global cursor
    if len(values) == 0:
        values = ("*",)
    sql = "SELECT "+values[0]
    for i in range(1,len(values)):
        sql = sql + ", " + values[i]
    sql = sql + " FROM " + table
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
    return cursor.fetchone()

def insert(table, fields, values):
    connect_db()
    global cursor, DB
    if len(fields)==0:
        return False
    if len(fields)!=len(values):
        return False
    sql = "INSERT INTO "+table+" ("+fields[0]
    for i in range(len(fields)-1):
        sql = sql+", "+fields[i+1]
    sql = sql + ") VALUES (\""+values[0]+"\""
    for i in range(len(fields)-1):
        if values[i+1] == None:
            sql = sql+", NULL"
        else:
            sql = sql+", \""+values[i+1]+"\""
    sql = sql + ")"
    cursor.execute(sql)
    DB.commit()
    return True

def get_levelup_html(source, variant = "standard"):
    global standard_attacks, alolan_attacks, galarian_attacks
    if variant == "alolan":
        attacks = alolan_attacks
    elif variant == "galarian":
        attacks = galarian_attacks
    else:
        attacks = standard_attacks
    query = re.compile(attacks[0]+".*"+attacks[1], re.DOTALL)
    temp = query.search(source)
    ret = None
    while(temp):
        ret = temp.group()
        l = len(ret) - 1
        source = ret[:l]
        temp = query.search(source)
    return ret[(len(attacks[0])-3):(len(ret)-len(attacks[1]))].replace("\t", "").replace("\r\n", "")

def parse_number(number_s):
    if number_s == "--":
        return "0"
    return number_s

def get_levelupmovelist(source, variant = "standard"):
    global types, attack_types
    ret = []
    temp = get_levelup_html(source, variant)
    cur = []
    cur_str = ""
    skip = False
    buff = 0
    for t in types:
        temp = temp.replace("<img src=\"/pokedex-bw/type/"+t+".gif\"", t+"<")
    for key in attack_types:
        temp = temp.replace("<img src=\"/pokedex-bw/type/"+key+".png\"", attack_types[key]+"<")
    temp = unescape(temp, {"&eacute;" : "e", "&#8212;" : "0"})
    for i in range(len(temp)):
        akt = temp[i]
        akt_long = ""
        if len(temp) > i+5:
            akt_long = temp[i:i+5]
        if buff > 0:
            buff -= 1
        elif skip:
            if akt == ">":
                skip = False
        elif akt == "<" and not (akt_long == "</tr>" or akt_long == "</td>"):
            skip = True
            continue
        elif akt_long == "</td>":
            cur_str.replace("&eacute;","e")
            cur.append(cur_str)
            cur_str = ""
            buff = 4
            continue
        elif akt_long == "</tr>":
            ret.append(cur)
            cur = []
            buff = 4
            continue
        else:
            cur_str += temp[i]
    temp = ret
    ret = []    
    for i in range(int(len(temp)/2)):
        temp[2*i].append(temp[2*i+1][0])
        ret.append(temp[2*i])
    temp = ret
    ret = []
    for each in temp:
        temp_dict = {}
        temp_dict["method"] = "level"
        temp_dict["level"] = each(0)
        temp_dict["name"] = each[1]
        temp_dict["type"] = each[2].capitalize()
        temp_dict["category"] = each[3].capitalize()
        temp_dict["power"] = parse_number(each[4])
        temp_dict["accuracy"] = parse_number(each[5])
        temp_dict["PP"] = each[6]
        temp_dict["effect"] = parse_number(each[7])
        temp_dict["description"] = each[8]
        ret.append(temp_dict)
    return ret

def get_levelupmovelist_by_name(name, variant = "standard"):
    rq = requests.get("https://www.serebii.net/pokedex-swsh/"+name.lower()+"/")
    source = rq.text
    return get_levelupmovelist(source, variant)

def move_to_database(pokemon, move):
    temp = select_one("moves", ("id",), "name = \""+move["name"]+"\"")
    if temp:
        move_id = temp[0]
    else:
        insert("moves", ("name", "type", "category", "power", "accuracy", "PP", "effect", "description"), (move["name"], move["type"], move["category"], move["power"], move["accuracy"], move["PP"], move["effect"], move["description"]))
        move_id = select_one("moves", ("id",), "name = \""+move["name"]+"\"")[0]
    insert("movesets", ("pokemon", "move", "method", "level"), (pokemon, str(move_id), move["method"], move["level"]))

def main():
    pokes = select("pokemon", ("national_number", "name"), "convert(substring(national_number, 1, 3), unsigned integer) <= 151")
    for poke in pokes:
        time.sleep(1)
        print(poke[1]+"...")
        if len(poke[0]) > 3:
            if poke[3] == "G":
                variant = "galarian"
            elif poke[3] == "A":
                variant = "alolan"
            else:
                variant = "standard"
        else:
            variant = "standard"
        movelist = get_levelupmovelist_by_name(poke[1], variant)
        for move in movelist:
            move_to_database(poke[1], move)

if __name__ == "__main__":
    main()