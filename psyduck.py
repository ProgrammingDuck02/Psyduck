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
#client.run(TOKEN)

s_emote_file = "Additional_files/shiny_emotes.txt"
file = open(s_emote_file)
text = file.read()
file.close()
emotes = text.split("\n")
for emote in emotes:
    temp_arr = emote.split(" ")
    id = temp_arr[0]
    emo = temp_arr[1]
    update("pokemon", ("shiny_emote",), (emo,), "national_number = \""+id+"\"")