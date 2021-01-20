import sys
import discord
import mysql.connector
from datetime import datetime
sys.path.append("python_scripts")
from pokemon import pokemon

cursor = None
DB = None

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

#sys.stdout = open("psyduck.log","a")
#sys.stderr = open("psyduck.error.log","a")
emote_file = open("../python scripts/emotes.txt")
lines = emote_file.read().split("\n")
emote_file.close()
for line in lines:
    arr = line.split(" ")
    update("pokemon", ("emote",), (arr[1],), "national_number = \""+arr[0]+"\"")
emote_file = open("../python scripts/shiny_emotes.txt")
lines = emote_file.read().split("\n")
emote_file.close()
for line in lines:
    arr = line.split(" ")
    update("pokemon", ("shiny_emote",), (arr[1],), "national_number = \""+arr[0]+"\"")
