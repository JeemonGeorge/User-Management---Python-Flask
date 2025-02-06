import sqlite3 as sql

con = sql.connect('db_web.db')
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS users")

sql = '''CREATE TABLE users (
    UID INTEGER PRIMARY KEY AUTOINCREMENT,
    UNAME TEXT NOT NULL,
    CONTACT TEXT NOT NULL,
    EMAIL TEXT UNIQUE NOT NULL,
    PASSWORD TEXT NOT NULL,
    PROFILE_PIC TEXT
)'''
cur.execute(sql)

con.commit()
con.close()
print("Database created successfully!")
