import mysql.connector
DB = None
cursor = None
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

def run():
    file = open("../Additional_files/evolutions.txt")
    lines = file.read().split("\n")
    file.close()
    for line in lines:
        evo = line.split("\t")
        pre = select("pokemon", ("national_number",), "name = \""+evo[0]+"\"")
        post = select("pokemon", ("national_number",), "name = \""+evo[2]+"\"")
        pre_id = None
        post_id = None
        for poke in pre:
            if poke[0][3:] == evo[3]:
                pre_id = poke[0]
                break
        if pre_id == None:
            pre_id = pre[0][0]
        for poke in post:
            if poke[0][3:] == evo[3]:
                post_id = poke[0]
                break
        if post_id == None:
            post_id = post[0][0]
        insert("evolutions", ("pokemon", "level", "evolution"), (pre_id, evo[1], post_id))

def disable_evolutions(limit):
    pokes = select("evolutions", ("id", "evolution"), "")
    ok = {}
    for poke in pokes:
        number = int(poke[1][:3])
        if number <= limit:
            ok[poke[0]] = "1"
        else:
            ok[poke[0]] = "0"
    keys = ok.keys()
    for key in keys:
        update("evolutions", ("avalible",), (ok[key],), "id = "+str(poke[0]))

disable_evolutions(151)
        
