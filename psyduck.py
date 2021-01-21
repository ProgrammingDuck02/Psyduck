import sys
import discord
import mysql.connector
from datetime import datetime
sys.path.append("python_scripts")
from pokemon import pokemon

cursor = None
DB = None

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

#sys.stdout = open("psyduck.log","a")
#sys.stderr = open("psyduck.error.log","a")

start = 1
end = 898

out_file = "Additional_files/pokemon_list.txt"
file = open(out_file, "w")
for i in range(start, end+1):
    number = number_to_nat_number(i)
    poke = get_pokemon_by_nat(number)
    if poke:
        file.write(poke.to_string()+"\n")
    number = number + "A"
    poke = get_pokemon_by_nat(number)
    if poke:
        file.write(poke.to_string()+"\n")
    number = number[:3]
    number = number + "G"
    poke = get_pokemon_by_nat(number)
    if poke:
        file.write(poke.to_string()+"\n")
file.close()