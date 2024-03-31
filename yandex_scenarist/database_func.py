import sqlite3

def create_db():
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        token INTEGER,
        gg TEXT,
        setting TEXT,
        janr TEXT,
        info TEXT,
        debug TEXT,
        text TEXT
    ); 
    '''
    cur.execute(query)
    con.commit()
    con.close()
def insert_data(id):
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    cur.execute(f'INSERT INTO users (user_id, debug, token) VALUES ({id}, "False", 6000);')
    con.commit()
    con.close()
def update_data(id, column, data):
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
    sql_query = f"UPDATE users SET {column} = ? WHERE user_id = ?;"
    cur.execute(sql_query , (data, id,))
    con.commit()
    con.close()
def select_data(id):
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
    data = cur.execute(f'''
    SELECT *
    FROM users
    WHERE user_id = {id}
    ''')
    data = data.fetchall()
    con.commit()
    con.close()
    return data
def datafr():
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
    data = cur.execute(f'''
    SELECT *
    FROM users
    ''')
    data = data.fetchall()
    con.commit()
    con.close()
    return data
def user_database(id):
    data = datafr()
    for i in range(len(data)):
        if data[i][1] == id:
            return True
    insert_data(id)
    return False
def user(id):
    data = datafr()
    for i in range(len(data)):
        if data[i][1] == id:
            return True
    return False
