import sys
import discord
import mysql.connector
import random
from os import path
from datetime import datetime
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
sys.path.append("python_scripts")
from python_scripts.pokemon import pokemon
from python_scripts.owned_pokemon import owned_pokemon

random.seed()
client = discord.Client()
slash = SlashCommand(client, sync_commands=True)
cursor = None
DB = None
prefix = "?"
coin_emoji = ":coin:"
guild_ids = []
#this is temporary
seller_picture_url = "https://cdn.costumewall.com/wp-content/uploads/2017/10/guzma.jpg"

pokemon_limit = 151

starters = []
starters.append(owned_pokemon(species = "001", level = 5))
starters.append(owned_pokemon(species = "004", level = 5))
starters.append(owned_pokemon(species = "007", level = 5))

def is_number(string):
    if len(string) == 0:
        return False
    for letter in string:
        if ord(letter) < ord("0"):
            return False
        if ord(letter) > ord("9"):
            return False
    return True

def has_key(dict, key):
    return key in dict.keys()

def number_to_nat_number(number):
    string = str(number)
    while(len(string)<3):
        string = "0"+string
    return string

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

def pow(base, power):
    if power == 0:
        return 1
    return pow(base, power - 1)*base

def int_to_bool_list(number, size):
    ret = [False] * size
    for i in range(size):
        if number % 2:
            ret[i] = True
        number = (int)(number/2)
    return ret

def bool_list_to_int(bool_list):
    ret = 0
    for i in range(len(bool_list)):
        if bool_list[i]:
            ret+=pow(2,i)
    return ret

###Mysql functions###
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

def delete(table, conditions):
    connect_db()
    global cursor, DB
    cmd = "DELETE FROM "+table
    if len(conditions) != 0:
        cmd = cmd + " WHERE " + conditions
    cursor.execute(cmd)
    DB.commit()

def update(table, fields, values, conditions):
    connect_db()
    global cursor, DB
    if len(fields) == 0:
        return False
    if len(fields) != len(values):
        return False
    sql = "UPDATE "+table+" SET "+fields[0]+" = \""+values[0]+"\""
    for i in range(1, len(values)):
        sql = sql + ", "+fields[i]+" = \""+values[i]+"\""
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
    DB.commit()
    return True

def level_up_party(trainer_id):
    connect_db()
    global cursor, DB
    sql = "UPDATE owned_pokemon SET exp = exp + 1 WHERE trainer_id = \""+trainer_id+"\" AND location = \"party\""
    cursor.execute(sql)
    DB.commit()
    sql = "UPDATE owned_pokemon SET level = level + 1, max_exp = 3 * level, exp = 0 WHERE trainer_id = \""+trainer_id+"\" AND location = \"party\" AND exp >= max_exp"
    cursor.execute(sql)
    DB.commit()

def shift_down(location, position, trainer_id):
    connect_db()
    global cursor, DB
    sql = "UPDATE owned_pokemon SET position = position - 1 WHERE location = \""+location+"\" AND position > "+position+" AND trainer_id = \""+str(trainer_id)+"\""
    cursor.execute(sql)
    DB.commit()
#########################

def give_pokemon_to(poke, trainer_id, shiny_rates = 1024):
    check = select("owned_pokemon", ("position",), "trainer_id = \""+trainer_id+"\" AND location = \"party\" AND position >= 1 AND position <= 6")
    if check:
        if len(check) >= 6:
            return False
    position = 1
    for each in check:
        if each[0] >= position:
            position = each[0]+1
    if shiny_rates > 0:
        if random.randrange(shiny_rates) == 0:
            poke.shiny = True
        else:
            poke.shiny = False
    else:
        poke.shiny = False
    params = [
        "trainer_id",
        "OT",
        "location",
        "position",
        "pokemon",
        "level",
        "max_exp"
    ]
    values = [
        trainer_id,
        trainer_id,
        "party",
        str(position),
        poke.pokemon.national_number,
        str(poke.level),
        str(3*poke.level)
    ]
    if poke.shiny:
        params.append("shiny")
        values.append("1")
    if not poke.name == None:
        params.append("name")
        values.append(poke.name)
    insert("owned_pokemon",params,values)
    return True

def get_pokemon_by_nat(nat_number):
    poke_data = select_one("pokemon",("national_number", "regional_number", "name", "type1", "type2", "region", "emote", "shiny_emote"), "national_number = \""+nat_number+"\"")
    if not poke_data:
        return False
    poke = pokemon(poke_data[1], poke_data[0], poke_data[2], poke_data[3], poke_data[4], poke_data[5], poke_data[6], poke_data[7])
    return poke

def get_latest_moves(pokemon_number, level):
    select("movesets", ("move",), "pokemon = \""+pokemon_number+"\" and level <= "+str(level)+"ORDER BY level DESC LIMIT 4")

def generate_ok_dict(message):
    return {
        "status": "ok",
        "hidden": False,
        "message": message
    }

def generate_error_dict(message):
    return {
        "status": "error",
        "hidden": True,
        "message": message
    }

#commands
def party_cmd(author_name, author_avatar, author_id):
    embed = discord.Embed(color = discord.Color.green())
    embed.set_author(name = author_name, icon_url = author_avatar)
    temp_list = select("owned_pokemon", ("name", "pokemon", "shiny", "position", "level"), "trainer_id = \"" + str(author_id) + "\" AND location = \"party\"")
    if not temp_list:
        return {
            "status": "error",
            "hidden": True,
            "message": "Oops, looks like you don't have any pokemon on your team :cry:"
        }
    pokemon_names = {}
    pokemon_levels = {}
    pokemon_emotes = {}
    for poke in temp_list:
        species = select_one("pokemon", ("name", "emote", "shiny_emote"), "national_number = \"" + poke[1] + "\"")
        if poke[0] == None:
            pokemon_names[poke[3]-1] = species[0]
        else:
            pokemon_names[poke[3]-1] = poke[0]
        pokemon_levels[poke[3]-1] = str(poke[4])
        if poke[2] == 0:
            pokemon_emotes[poke[3]-1] = species[1]
        else:
            pokemon_emotes[poke[3]-1] = species[2]
    party_size = len(temp_list)
    party = pokemon_emotes[0] + pokemon_names[0] + " lvl." + pokemon_levels[0]
    for i in range(1, party_size):
        party += "\n" + pokemon_emotes[i] + pokemon_names[i] + " lvl." + pokemon_levels[i]
    embed.add_field(name = author_name + "'s party", value = party)
    return {
        "status": "ok",
        "hidden": False,
        "message": embed
    }

def box_cmd(box_number, author_id):
    embed = discord.Embed(color = discord.Color.gold())
    while box_number[0] == " ":
        box_number = box_number[1:]
    if not is_number(box_number):
        return generate_error_dict(box_number + " is not a valid box number")
    if int(box_number) < 1 or int(box_number) > 50:
        return generate_error_dict(box_number + " is not a valid box number")
    selected_box = "BOX"+box_number
    temp_list = select("owned_pokemon", ("name", "pokemon", "shiny", "position", "level"), "trainer_id = \"" + str(author_id) + "\" AND location = \""+selected_box+"\"")
    if not temp_list:
        temp_list = []
    emote = {}
    names = {}
    levels = {}
    for each in temp_list:
        poke = select_one("pokemon", ("name", "emote","shiny_emote"), "national_number = \""+each[1]+"\"")
        if each[0] == None:
            names[each[3]-1] = poke[0]
        else:
            names[each[3]-1] = each[0]
        if each[2] == 0:
            emote[each[3]-1] = poke[1]
        else:
            emote[each[3]-1] = poke[2]
        levels[each[3]-1] = str(each[4])
    text = ""
    for i in range(10):
        text += str(i+1) + ". "
        if has_key(names, i):
            text += emote[i] + names[i] + " lvl." + levels[i]
        else:
            text += "-------"
        text += "\n" 
    embed.add_field(name = selected_box, value = text)
    return generate_ok_dict(embed)

def switch_cmd(from_where, to_where, author_id):
	location1 = ""
	pokemon1 = 0
	location2 = ""
	pokemon2 = 0
	if from_where.lower().startswith("box"):
		tmp = from_where.split(":")
		if len(tmp) < 2:
			return generate_error_dict("Wrong use of BOX option in the first parameter\nCorrect use BOX[box number]:[pokemon number in box]")
		box_number_str = tmp[0][3:]
		if not is_number(box_number_str):
			return generate_error_dict(tmp[0]+" is not a valid box name")
		box_number = int(box_number_str)
		if box_number < 1 or box_number > 50:
			return generate_error_dict(tmp[0]+" is not a valid box name")
		location1 = tmp[0].upper()
		if not is_number(tmp[1]):
			return generate_error_dict(tmp[1]+" is not a valid box name")
		pokemon1 = int(tmp[1])
		if pokemon1 < 1 or pokemon1 > 10:
			return generate_error_dict(tmp[1]+" is not a valid box name")
	else:
		location1 = "party"
		if not is_number(from_where):
			return generate_error_dict(from_where+" is not a valid party number")
		pokemon1 = int(from_where)
		if pokemon1 < 1 or pokemon1 > 10:
			return generate_error_dict(from_where+" is not a valid party number")
	if to_where.startswith("box"):
		tmp = to_where.split(":")
		if len(tmp) < 2:
			return generate_error_dict("Wrong use of BOX option in the first parameter\nCorrect use BOX[box number]:[pokemon number in box]")
		box_number_str = tmp[0][3:]
		if not is_number(box_number_str):
			return generate_error_dict(tmp[0]+" is not a valid box name")
		box_number = int(box_number_str)
		if box_number < 1 or box_number > 50:
			return generate_error_dict(tmp[0]+" is not a valid box name")
		location2 = tmp[0].upper()
		if not is_number(tmp[1]):
			return generate_error_dict(tmp[1]+" is not a valid box name")
		pokemon2 = int(tmp[1])
		if pokemon2 < 1 or pokemon2 > 10:
			return generate_error_dict(tmp[1]+" is not a valid box name")
	else:
		location2 = "party"
		if not is_number(to_where):
			return generate_error_dict(to_where+" is not a valid party number")
		pokemon2 = int(to_where)
		if pokemon2 < 1 or pokemon2 > 10:
			return generate_error_dict(to_where+" is not a valid party number")
	id1 = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(author_id)+"\" AND location = \""+location1+"\" AND position = \""+str(pokemon1)+"\"")
	id2 = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(author_id)+"\" AND location = \""+location2+"\" AND position = \""+str(pokemon2)+"\"")
	if not id1:
		return generate_error_dict("Oops, looks like you don't have any pokemon on position "+str(pokemon1)+" in your "+location1+"\nTry using "+prefix+"deposit or "+prefix+"withdraw")
	if not id2:
		return generate_error_dict("Oops, looks like you don't have any pokemon on position "+str(pokemon2)+" in your "+location2+"\nTry using "+prefix+"deposit or "+prefix+"withdraw")
	id1 = str(id1[0])
	id2 = str(id2[0])
	update("owned_pokemon", ("location", "position"), (location2, str(pokemon2)), "id = "+id1)
	update("owned_pokemon", ("location", "position"), (location1, str(pokemon1)), "id = "+id2)
	return {
        "status": "ok",
        "hidden": True,
        "message": "Pokemon switched places!"
    }

def deposit_cmd(poke, box_input, author_id):
    if box_input.lower().startswith("box"):
        box = box_input.upper()
    else:
        box = "BOX" + box_input
    if not is_number(poke):
        return generate_error_dict(poke + " is not a valid party number")
    if int(poke) < 1 or int(poke) > 6:
        return generate_error_dict(poke + " is not a valid party number")
    if not is_number(box[3:]):
        return generate_error_dict(box_input + " is not a valid box name or box number")
    if int(box[3:]) < 1 or int(box[3:]) > 50:
        return generate_error_dict(box_input + " is not a valid box name or box number")
    check = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(author_id) + "\" AND location = \"party\" AND position = " + str(poke))
    if not check:
        return generate_error_dict("Oops, looks like you don't have any pokemon in your party in position "+str(poke))
    pokemon_in_box = 0
    temp = select("owned_pokemon", ("position",), "trainer_id = \""+str(author_id) + "\" AND location = \""+ box + "\" AND position >= 1 AND position <= 10")
    if temp:
        pokemon_in_box = len(temp)
    if pokemon_in_box >= 10:
        return generate_error_dict("Oops, looks like your " + box + " is full. Consider changing boxes")
    new_position = 0
    for i in range(1,11):
        ok = True
        for each in temp:
            if each[0] == i:
                ok = False
                break
        if ok:
            new_position = i
            break
    update("owned_pokemon", ("location", "position"), (box, str(new_position)), "trainer_id = \""+str(author_id) + "\" AND location = \"party\" AND position = " + str(poke))
    shift_down("party", str(poke), author_id)
    return {
        "status": "ok",
        "hidden": True,
        "message": "Done! Your pokemon has been boxed into "+box
    }

def withdraw_cmd(box, poke, author_id):
    global prefix
    original_box = box
    box = box.upper()
    if not box.startswith("BOX"):
        box = "BOX" + box
    if not is_number(box[3:]):
        return generate_error_dict(original_box + " is not a valid box name or box number")
    if int(box[3:]) < 1 or int(box[3:]) > 50:
        return generate_error_dict(original_box + " is not a valid box name or box number")
    if not is_number(poke):
        return generate_error_dict(poke + " is not a valid pokemon number")
    if int(poke) < 1 or int(poke) > 10:
        return generate_error_dict(poke + " is not a valid pokemon number")
    pokemon_in_team = 0
    temp = select("owned_pokemon", ("position",), "trainer_id = \""+str(author_id) + "\" AND location = \"party\" AND position >= 1 AND position <= 6")
    if temp:
        pokemon_in_team = len(temp)
    if pokemon_in_team >= 6:
        return generate_error_dict("Oops, looks like you don't have any more space in your party.\nTry using "+prefix+"switch or "+prefix+"deposit")
    position = 1
    if temp:
        for each in temp:
            if each[0] > position-1:
                position = each[0]+1
    check = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(author_id) + "\" AND location = \""+box+"\" AND position = "+poke)
    if not check:
        return generate_error_dict("Oops, looks like you don't have any pokemon on position "+poke+" in "+box)
    update("owned_pokemon", ("location", "position"), ("party", str(position)), "id = "+str(check[0]))
    shift_down(box, poke, author_id)
    return {
        "status": "ok",
        "hidden": True,
        "message": "Done! Your pokemon has been added into your party!"
    }

def release_cmd(poke, location, author_id):
    original_location = location
    if location.lower() == "party":
        location = location.lower()
    else:
        location = location.upper()
    if location != "party" and location.startswith("BOX"):
        return generate_error_dict(original_location + " is not a correct box name. Box names start with \"BOX\"(not case sensitive)")
    if not is_number(poke):
        return generate_error_dict(poke + " is not a correct pokemon number")
    if int(poke) < 1 or (location == "party" and int(poke) > 6) or int(poke) > 10:
        return generate_error_dict(poke + " is not a correct pokemon number")
    if not is_number(location[3:]) and location != "party":
        return generate_error_dict(original_location + " is not a correct box name")
    if location != "party" and (int(location[3:]) < 1 or int(location[3:]) > 50):
        return generate_error_dict(original_location + " is not a correct box name")
    count = select_one("owned_pokemon", ("count(*)",), "trainer_id = \""+str(author_id)+"\"")[0]
    if count == 1:
        return generate_error_dict("You only have one pokemon left! Don't release it!")
    check = select_one("owned_pokemon", ("id","name","pokemon"), "trainer_id = \""+str(author_id) + "\" AND location = \""+location+"\" AND position = "+poke)
    if not check:
        return generate_error_dict("Oops, looks like you don't have any pokemon on position "+poke+" in your "+location)
    name = check[1]
    if check[1] == None:
        name = select_one("pokemon", ("name",), "national_number = \""+check[2]+"\"")[0]
    delete("owned_pokemon", "id = "+str(check[0]))
    shift_down(location, poke, author_id)
    return {
        "status": "ok",
        "hidden": True,
        "message": name+" was released. Bye bye "+name+"!"
    }

def starters_cmd():
    if len(starters) == 0:
        return generate_error_dict("Oops, looks like there are no starters ready to pick :cry:")
    embed = discord.Embed(color = discord.Color.red())
    starter_list = ""
    for i in range(len(starters)):
        temp = select_one("pokemon", ("name", "emote"), "national_number = \""+starters[i].pokemon.national_number+"\"")
        starter_list += str(i+1) + ". " + temp[1] + temp[0] + "\n"
    embed.add_field(name = "Currently avalible starters to pick:", value = starter_list, inline = False)
    embed.add_field(name = "To pick your starter use "+prefix+"pick [number] command!", value = "You can only pick your starter if you don't have trainer account already", inline = False)
    return generate_ok_dict(embed)

def pick_starter_cmd(pick, author_id):
    check = select("trainers", ("id",), "id = \""+str(author_id)+"\"")
    if check:
        return generate_error_dict("Oops, looks like you already got your starter. Don't be greedy, let other trainers have some fun too :wink:")
    if not is_number(pick):
        return generate_error_dict(pick + " is not a correct starter number")
    pick = int(pick) - 1
    if pick < 0 or pick >= len(starters):
        return generate_error_dict(pick + " is not a correct starter number")
    temp = select_one("pokemon", ("name", "emote", "shiny_emote"), "national_number = \""+starters[pick].pokemon.national_number+"\"")
    temp_poke = starters[pick]
    give_pokemon_to(temp_poke, str(author_id))
    insert("trainers", ("id",), (str(author_id), ))
    emote_to_use = temp[1]
    if temp_poke.shiny:
        emote_to_use = temp[2]
    return generate_ok_dict("You picked "+emote_to_use+temp[0]+" as your starter! Hope you and "+temp[0]+" have a lot of fun together!")

def show_evolutions_cmd(poke):
    pokelist = select("pokemon", ("national_number", "emote", "name"), "LOWER(name) = \""+poke.lower()+"\"")
    if not pokelist:
        return generate_error_dict("Oops, looks like you made a typo in pokemon's name. I can't find "+poke+" in our pokemon database")
    if int(pokelist[0][0][:3]) > pokemon_limit:
        return generate_error_dict("We don't support this pokemon right now. Next generations will be added soon")
    embed = discord.Embed(color = discord.Color.teal())
    for poke in pokelist:
        text = "Looks like this pokemon doesn't have any evolutions or its evolutions are yet to be added"
        sql = "SELECT e.level, p.name, p.emote FROM evolutions AS e INNER JOIN pokemon AS p ON p.national_number = e.evolution where e.pokemon = \""+poke[0]+"\" and e.avalible = 1"
        connect_db()
        cursor.execute(sql)
        evolutions = cursor.fetchall()
        if evolutions:
            text = ""
            for evo in evolutions:
                text += evo[2] + evo[1] + " on level "+str(evo[0]) + "\n"
        embed.add_field(name = poke[1] + poke[2] + "'s evolutions:", value = text)
    return generate_ok_dict(embed)

def evolve_cmd(position, species, author_id):
    if position.upper().startswith("box"):
        tmp_lst = position.split(":",1)
        if len(tmp_lst) < 2:
            return generate_error_dict("To evolve pokemon in a box please use format "+prefix+"evolve [box name]:[pokemon in box] <evolution pokemon>")
        location = tmp_lst[0].upper()
        if len(location) == 3:
            location += "1"
        if not location[3:].isdigit():
            return generate_error_dict(location+" is not a valid box number")
        if int(location[3:]) < 1 or int(location[3:]) > 10:
            return generate_error_dict(location+" is not a valid box number")
        position = tmp_lst[1]
    else:
        location = "party"
    if not position.isdigit():
        return generate_error_dict(position+" is not a valid pokemon number")
    if int(position) < 1 or int(position) > 6:
        return generate_error_dict(position+" is not a valid pokemon number")
    poke = select_one("owned_pokemon", ("pokemon", "level", "shiny"), "trainer_id = \""+str(author_id)+"\" AND location = \""+location+"\" AND position = "+position)
    if not poke:
        return generate_error_dict("Oops, looks like you don't have any pokemon in that position")
    shiny = (poke[2] == 1)
    evolutions = select("evolutions", ("evolution",), "pokemon = \""+poke[0]+"\" AND avalible = 1 AND level <="+str(poke[1]))
    if len(evolutions) == 0:
        return generate_error_dict("Your pokemon is not able to evolve right now")
    choice = None
    if species == None:
        choice = evolutions[random.randrange(len(evolutions))][0]
    else:
        form = ""
        if species.lower().startswith("alolan "):
            form = "A"
            species = species.split(" ",1)[1]
        elif species.lower().startswith("galarian "):
            form = "G"
            species = species.split(" ",1)[1]
        chosen_poke = select_one("pokemon", ("national_number",), "name = \""+species+"\" AND CHAR_LENGTH(national_number) = "+str(3+len(form))+" AND national_number like \"%"+form+"\"")
        if not chosen_poke:
            return generate_error_dict("Oops, looks like you made a typo in pokemon evolution name. I can't find it in our pokemon database")
        for each in evolutions:
            if each[0] == chosen_poke[0]:
                choice = each[0]
    if choice == None:
        return generate_error_dict("Oops, looks like your pokemon is unable to evolve into "+species)
    new_poke = select_one("pokemon", ("name", "emote", "shiny_emote"), "national_number = \""+choice+"\"")
    emote = None
    if shiny:
        emote = new_poke[2]
    else:
        emote = new_poke[1]
    update("owned_pokemon", ("pokemon",), (choice,), "trainer_id = \""+str(author_id)+"\" AND location = \""+location+"\" AND position = "+position)
    return {
        "status": "ok",
        "hidden": True,
        "message": "Congratulations, your pokemon evolved into "+emote+new_poke[0]+"!"
    }

def daily_cmd(author_id):
    check = select_one("trainers", ("received_daily",), "id = \""+str(author_id)+"\"")
    if not check:
        return generate_error_dict("Oops, looks like you don't have a trainer profile set yet. View avalible starters with "+prefix+"starters and choose one with "+prefix+"pick [starter number]")
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    if check[0] != None:
        if str(check[0]) == today:
            return generate_error_dict("Oops, looks like you already accepted your daily award today, please try again tomorrow")
    sql = "UPDATE trainers set money = money + 200, received_daily = \""+today+"\" WHERE id = \""+str(author_id)+"\""
    cursor.execute(sql)
    DB.commit()
    return {
        "status": "ok",
        "hidden": True,
        "message": "Yay! You received your daily 200"+coin_emoji+"!"
    }

def balance_cmd(author_id):
    balance = select_one("trainers", ("money",), "id = \""+str(author_id)+"\"")
    if not balance:
        return generate_error_dict("Oops, looks like you don't have a trainer profile set yet. View avalible starters with "+prefix+"starters and choose one with "+prefix+"pick [starter number]")
    return {
        "status": "ok",
        "hidden": True,
        "message": "Your current balance is "+str(balance[0])+coin_emoji
    }

def get_new_shop_pokemon():
    temp = select("pokemon", ("national_number",), "for_sale = 1 order by rand() limit 5")
    datestamp = datetime.now().strftime("%Y-%m-%d")
    plik = open("daily_shop", "w")
    pokemons = []
    for poke in temp:
        pokemons.append(poke[0])
        plik.write(poke[0]+"\n")
    plik.write(datestamp)
    plik.close()
    return pokemons

def get_pokemon_from_shop():
    if not path.exists("daily_shop"):
        return get_new_shop_pokemon()
    else:
        plik = open("daily_shop", "r")
        lines = plik.read().split("\n")
        plik.close()
        if len(lines[0]) == 0:
            return get_new_shop_pokemon()
        else:
            datestamp = lines[5]
            today = datetime.now().strftime("%Y-%m-%d")
            if datestamp == today:
                pokemon_numbers = []
                for i in range(5):
                    pokemon_numbers.append(lines[i])
                return pokemon_numbers
            else:
                return get_new_shop_pokemon()

def shop_cmd():
    pokemon_numbers = get_pokemon_from_shop()
    pokemons = ""
    first = True
    for i in range(len(pokemon_numbers)):
        temp = select_one("pokemon", ("name", "emote", "price"), "national_number=\""+pokemon_numbers[i]+"\"")
        if first:
            first = False
        else:
            pokemons += "\n"
        pokemons += str(i+1) + ". " + temp[1] + temp[0] + " price: " + str(temp[2]) + coin_emoji
    embed = discord.Embed(color = discord.Color.gold())
    embed.set_author(name = "Guzma", icon_url = seller_picture_url)
    embed.add_field(name = "Wassat you need, punk?", value = pokemons)
    embed.set_footer(text = "Use "+prefix+"buy [pokemon_number] to buy the pokemon")
    return generate_ok_dict(embed)

def buy_cmd(poke, author_id):
    if not is_number(poke):
        return generate_error_dict(poke+" is not a correct pokemon number")
    if int(poke) < 1 or int(poke) > 5:
        return generate_error_dict(poke+" is not a correct pokemon number")
    poke = int(poke) - 1
    temp = select_one("trainers", ("money", "last_bought_on", "last_bought_what"), "id = "+str(author_id))
    money = temp[0]
    last_bought_on = temp[1]
    last_bought_what = temp[2]
    today = datetime.now().strftime("%Y-%m-%d")
    if last_bought_on != today:
        last_bought_on = today
        last_bought_what = 0
    pokemon_bought = int_to_bool_list(last_bought_what, 5)
    if pokemon_bought[poke]:
        return generate_error_dict("You've already bought this pokemon today. Wait tomorrow for shop refresh.")
    pokemons = get_pokemon_from_shop()
    pokemon_bought[poke] = True
    last_bought_what = bool_list_to_int(pokemon_bought)
    temp = select_one("pokemon", ("emote", "name", "price"), "national_number = \""+pokemons[poke] + "\"")
    if temp[2] > money:
        return generate_error_dict("You don't have enough money to buy that pokemon!")
    money -= temp[2]
    bought_pokemon = owned_pokemon(species = pokemons[poke], level=5)
    if not give_pokemon_to(bought_pokemon, str(author_id)):
        return generate_error_dict("You don't have a free space in your party. Free a space in your party and try again")
    update("trainers", ("money", "last_bough_on", "last_bought_what"), (str(money), last_bought_on, str(last_bought_what)), "id = \""+str(author_id)+"\"")
    return generate_ok_dict("Congratulations!\nYou bought "+temp[0]+temp[1]+"!\n"+temp[0]+temp[1]+" has been added to your party")

#slash commands
@slash.slash(name="party", description="Displays your party", guild_ids=guild_ids)
async def _party(ctx):
    ret = party_cmd(
        author_name=ctx.author.name,
        author_avatar=ctx.author.avatar_url,
        author_id=ctx.author_id
    )
    if ret["status"] == "ok":
        await ctx.send(embed = ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="box", description="Displays given box", guild_ids=guild_ids, options=[
    create_option(
        name="box_number",
        description="choose which box should be displayed (numbers 1-50)",
        option_type=3,
        required=True
    )
])
async def _box(ctx, box_number):
    ret = box_cmd(
        box_number=box_number,
        author_id=ctx.author_id
    )
    if ret["status"] == "ok":
        await ctx.send(embed = ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="switch", description="Switches pokemons in boxes and/or party", guild_ids=guild_ids, options=[
    create_option(
        name="switch_first",
        description="Choose the first pokemon that should be switched. ex. \"BOX1:3\" or \"3\" to move from party",
        option_type=3,
        required=True
    ),
    create_option(
        name="switch_second",
        description="Choose the second pokemon that should be switched. ex. \"BOX1:3\" or \"3\" to move to party",
        option_type=3,
        required=True
    )
])
async def _switch(ctx, switch_first, switch_second):
    ret = switch_cmd(switch_first, switch_second, ctx.author_id)
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="deposit", description="Deposits your pokemon from party to the specified box", guild_ids=guild_ids, options=[
    create_option(
        name="pokemon",
        description="Choose which pokemon to deposit by specifying its number in your party",
        option_type=3,
        required=True
    ),
    create_option(
        name="box",
        description="Choose to which box should the pokemon be sent to. ex. \"BOX3\" or just \"3\"",
        option_type=3,
        required=True
    )
])
async def _deposit(ctx, pokemon, box):
    ret = deposit_cmd(pokemon, box, ctx.author.id)
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="withdraw", description="Withdraws pokemon from your box and adds it to your party", guild_ids=guild_ids, options=[
    create_option(
        name="box",
        description="Choose from which box the pokemon should be withdrawn from. ex. \"BOX3\" or just \"3\"",
        option_type=3,
        required=True
    ),
    create_option(
        name="position",
        description="Specify which pokemon in the given box should be withdrawn",
        option_type=3,
        required=True
    )
])
async def _withdraw(ctx, box, position):
    ret = withdraw_cmd(box, position, ctx.author.id)
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="evolve", description="Evolves a pokemon if it meets the requirements", guild_ids=guild_ids, options=[
    create_option(
        name="pokemon_position", 
        description="Choose which pokemon to evolve. If you want to evolve a pokemon from box type in for ex. \"BOX2:4\"",
        option_type=3,
        required=True
    ),
    create_option(
        name="evolution",
        description="If pokemon has multiple evolutions, you can specify the name of the one you want!",
        option_type=3,
        required=False
    )
])
async def _evolve(ctx, pokemon_position, evolution = None):
    ret = evolve_cmd(pokemon_position, evolution, ctx.author.id)
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="daily", description="Collect your daily coins!", guild_ids=guild_ids)
async def _daily(ctx):
    ret = daily_cmd(ctx.author.id)
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@slash.slash(name="shop", description="Shows shop", guild_ids=guild_ids)
async def _shop(ctx):
    ret = shop_cmd()
    if ret["status"] == "ok":
        await ctx.send(ret["message"], hidden = ret["hidden"])
    elif ret["status"] == "error":
        await ctx.send(ret["message"], hidden = ret["hidden"])

@client.event
async def on_message(message):
    global cursor
    if message.author == client.user:
        return
    level_up_party(str(message.author.id))
    if not message.content.startswith(prefix):
        return
    mes = message.content[len(prefix):]
    words = mes.split(" ")
    if mes.lower() == "party":
        ret = party_cmd(author_name=message.author.name, author_avatar=message.author.avatar_url, author_id=message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("box"):
        if len(words) == 1:
            box_number = "1"
        else:
            box_number = words[1]
        ret = box_cmd(box_number=box_number, author_id=message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("switch"):
        params = mes.split(" ")
        params.remove(params[0])
        if len(params) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"switch [pokemon1] [pokemon2]\nCheck "+prefix+"help for more informations")
            return
        ret = switch_cmd(from_where=params[0], to_where=params[1], author_id=message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("deposit"):
        words = mes.split(" ")
        if len(words) < 3:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"deposit [pokemon] [box/box number]\nCheck "+prefix+"help for more informations")
            return
        ret = deposit_cmd(words[1], words[2], message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])
    
    if mes.lower().startswith("withdraw"):
        words = mes.split(" ")
        if len(words) < 3:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"withdraw [box/box number] [pokemon number in box]\nCheck "+prefix+"help for more informations")
            return
        ret = withdraw_cmd(words[1],words[2], message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])
        
    if mes.lower().startswith("release pokemon"):
        words = mes.split(" ")
        if len(words) < 5:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"release pokemon [pokemon_number] in [boxname/\"party\"]\nCheck "+prefix+"help for more informations")
            return
        if words[3].lower() != "in":
            await message.channel.send("Wrong format!\nCorrect use: "+prefix+"release pokemon [pokemon_number] in [boxname/\"party\"]\nCheck "+prefix+"help for more informations")
            return
        ret = release_cmd(words[2], words[4], message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])
    
    if mes.lower() == "starters":
        ret = starters_cmd()
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("pick"):
        temp = mes.split(" ")
        if len(temp) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"pick [number]\nCheck "+prefix+"help for more informations")
            return
        pick = temp[1]
        ret = pick_starter_cmd(pick, message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("evolution"):
        temp = mes.split(" ", 1)
        if len(temp) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"evolution [pokemon name]\nCheck "+prefix+"help for more informations")
            return
        ret = show_evolutions_cmd(temp[1])
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("evolve"):
        temp = mes.split(" ",2)
        if len(temp) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use "+prefix+"evolve [pokemon] <evolution pokemon>\nCheck "+prefix+"help for more informations")
            return
        if len(temp) == 2:
            ret = evolve_cmd(temp[1], None, message.author.id)
        else:
            ret = evolve_cmd(temp[1], temp[2], message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower() == "daily":
        ret = daily_cmd(message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower() == "balance":
        ret = balance_cmd(message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower() == "shop":
        ret = shop_cmd()
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    if mes.lower().startswith("buy"):
        temp = mes.split(" ", 1)
        if len(temp) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use "+prefix+"buy [pokemon]\nCheck "+prefix+"help for more informations")
            return
        ret = buy_cmd(temp[1], message.author.id)
        if ret["status"] == "ok":
            await message.channel.send(embed = ret["message"])
        elif ret["status"] == "error":
            await message.channel.send(ret["message"])

    #Delete before final distribution duh
    if mes.lower() == "off" and message.author.id != 370602661776588802:
        await message.channel.send("Logging out...")
        await client.logout()
        return


@client.event
async def on_ready():
    guild_ids = []
    for guild in client.guilds:
        guild_ids.append(guild.id)
    print("Logged in as "+client.user.name)
    print("id: "+str(client.user.id))

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
client.run(TOKEN)