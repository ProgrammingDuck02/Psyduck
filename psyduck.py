import sys
import discord
import mysql.connector
from datetime import datetime
sys.path.append("python_scripts")
from pokemon import pokemon

client = discord.Client()
cursor = None
DB = None
prefix = "?"

def is_number(string):
    for letter in string:
        if ord(letter) < ord("0"):
            return False
        if ord(letter) > ord("9"):
            return False
    return True

def has_key(dict, key):
    for k in dict.keys():
        if k == key:
            return True
    return False

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
#########################

def get_pokemon_by_nat(nat_number):
    poke_data = select_one("pokemon",("national_number", "regional_number", "name", "type1", "type2", "region", "emote", "shiny_emote"), "national_number = \""+nat_number+"\"")
    if not poke_data:
        return False
    poke = pokemon(poke_data[1], poke_data[0], poke_data[2], poke_data[3], poke_data[4], poke_data[5], poke_data[6], poke_data[7])
    return poke

@client.event
async def on_message(message):
    global prefix
    if message.author == client.user:
        return
    if not message.content.startswith(prefix):
        return
    mes = message.content[len(prefix):]
    if mes.lower() == "party":
        embed = discord.Embed(color = discord.Color.green())
        embed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
        temp_list = select("owned_pokemon", ("name", "pokemon", "shiny", "position", "level"), "trainer_id = \"" + str(message.author.id) + "\" AND location = \"party\"")
        if not temp_list:
            await message.channel.send("Oops, looks like you don't have any pokemon on your team :cry:")
            return
        pokemon_names = {}
        pokemon_levels = {}
        pokemon_emotes = {}
        for poke in temp_list:
            spieces = select_one("pokemon", ("name", "emote", "shiny_emote"), "national_number = \"" + poke[1] + "\"")
            if poke[0] == None:
                pokemon_names[poke[3]-1] = spieces[0]
            else:
                pokemon_names[poke[3]-1] = poke[0]
            pokemon_levels[poke[3]-1] = str(poke[4])
            if poke[2] == 0:
                pokemon_emotes[poke[3]-1] = spieces[1]
            else:
                pokemon_emotes[poke[3]-1] = spieces[2]
        party_size = len(temp_list)
        party = pokemon_emotes[0] + pokemon_names[0] + " lvl." + pokemon_levels[0]
        for i in range(1, party_size):
            party += "\n" + pokemon_emotes[i] + pokemon_names[i] + " lvl." + pokemon_levels[i]
        embed.add_field(name = message.author.name + "'s party", value = party)
        await message.channel.send(embed = embed)
        return

    if mes.lower().startswith("box"):
        embed = discord.Embed(color = discord.Color.gold())
        if len(mes) == 3:
            box_number = "1"
        else:
            box_number = mes[3:]
        while box_number[0] == " ":
            box_number = box_number[1:]
        if not is_number(box_number):
            await message.channel.send(box_number + " is not a valid box number")
            return
        if int(box_number) < 1 or int(box_number) > 50:
            await message.channel.send(box_number + " is not a valid box number")
            return
        selected_box = "BOX"+box_number
        temp_list = select("owned_pokemon", ("name", "pokemon", "shiny", "position", "level"), "trainer_id = \"" + str(message.author.id) + "\" AND location = \""+selected_box+"\"")
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
        await message.channel.send(embed = embed)
        return

    if mes.lower().startswith("switch"):
        params = mes.split(" ")
        params.remove(params[0])
        if len(params) < 2:
            await message.channel.send("Wrong number of parameters!\nCorrect use: "+prefix+"switch [pokemon1] [pokemon2]\nCheck "+prefix+"help for more informations")
            return
        location1 = ""
        pokemon1 = 0
        location2 = ""
        pokemon2 = 0
        if params[0].lower().startswith("box"):
            tmp = params[0].split(":")
            if len(tmp) < 2:
                await message.channel.send("Wrong use of BOX option in the first parameter\nCorrect use BOX[box number]:[pokemon number in box]")
                return
            box_number_str = tmp[0][3:]
            if not is_number(box_number_str):
                await message.channel.send(tmp[0]+" is not a valid box name")
                return
            box_number = int(box_number_str)
            if box_number < 1 or box_number > 50:
                await message.channel.send(tmp[0]+" is not a valid box name")
                return
            location1 = tmp[0].upper()
            if not is_number(tmp[1]):
                await message.channel.send(tmp[1]+" is not a valid box number")
                return
            pokemon1 = int(tmp[1])
            if pokemon1 < 1 or pokemon1 > 10:
                await message.channel.send(tmp[1]+" is not a valid box number")
                return
        else:
            location1 = "party"
            if not is_number(params[0]):
                await message.channel.send(params[0]+" is not a valid party number")
                return
            pokemon1 = int(params[0])
            if pokemon1 < 1 or pokemon1 > 10:
                await message.channel.send(params[0]+" is not a valid party number")
                return
        if params[1].lower().startswith("box"):
            tmp = params[1].split(":")
            if len(tmp) < 2:
                await message.channel.send("Wrong use of BOX option in the first parameter\nCorrect use BOX[box number]:[pokemon number in box]")
                return
            box_number_str = tmp[0][3:]
            if not is_number(box_number_str):
                await message.channel.send(tmp[0]+" is not a valid box name")
                return
            box_number = int(box_number_str)
            if box_number < 1 or box_number > 50:
                await message.channel.send(tmp[0]+" is not a valid box name")
                return
            location2 = tmp[0].upper()
            if not is_number(tmp[1]):
                await message.channel.send(tmp[1]+" is not a valid box number")
                return
            pokemon2 = int(tmp[1])
            if pokemon2 < 1 or pokemon2 > 10:
                await message.channel.send(tmp[1]+" is not a valid box number")
                return
        else:
            location2 = "party"
            if not is_number(params[1]):
                await message.channel.send(params[1]+" is not a valid party number")
                return
            pokemon2 = int(params[1])
            if pokemon2 < 1 or pokemon2 > 10:
                await message.channel.send(params[1]+" is not a valid party number")
                return
        id1 = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(message.author.id)+"\" AND location = \""+location1+"\" AND position = \""+str(pokemon1)+"\"")
        id2 = select_one("owned_pokemon", ("id",), "trainer_id = \""+str(message.author.id)+"\" AND location = \""+location2+"\" AND position = \""+str(pokemon2)+"\"")
        if not id1:
            await message.channel.send("Oops, looks like you don't have any pokemon on position "+str(pokemon1)+" in your "+location1+"\nTry using "+prefix+"deposit or "+prefix+"withdraw")
            return
        if not id2:
            await message.channel.send("Oops, looks like you don't have any pokemon on position "+str(pokemon2)+" in your "+location2+"\nTry using "+prefix+"deposit or "+prefix+"withdraw")
            return
        id1 = str(id1[0])
        id2 = str(id2[0])
        update("owned_pokemon", ("location", "position"), (location2, str(pokemon2)), "id = "+id1)
        update("owned_pokemon", ("location", "position"), (location1, str(pokemon1)), "id = "+id2)
        await message.channel.send("Pokemon switched places!")
        return

    #Delete before final distribution duh
    if mes.lower() == "off":
        await message.channel.send("Logging out...")
        await client.logout()
        return


@client.event
async def on_ready():
    print("Logged in as "+client.user.name)
    print("id: "+str(client.user.id))

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
client.run(TOKEN)