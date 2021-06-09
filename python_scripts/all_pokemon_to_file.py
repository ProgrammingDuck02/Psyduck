import mysql.connector
DB = mysql.connector.connect(
    host = 'localhost',
    user = 'psyduck',
    password = 'Uqp9MF[jf<!R(%:S',
    database = 'psyduckDB'
    )
cursor = DB.cursor()
cursor.execute('SELECT national_number, name FROM pokemon')
pokemon = cursor.fetchall()
all_pokemon_file = open("all_pokemon", "w")
s = ""
for poke in pokemon:
    s += poke[0]+" "+poke[1]+"\n"
all_pokemon_file.write(s)
all_pokemon_file.close()