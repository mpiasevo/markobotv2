import sqlite3

db = sqlite3.connect('messages.sqlite')
cursor = db.cursor()
cursor.execute("DELETE FROM main WHERE msgs = 0")
db.commit()
cursor.close()
db.close()