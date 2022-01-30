import sqlite3

db = sqlite3.connect('messages.sqlite')
cursor = db.cursor()
cursor.execute("SELECT SUM(msgs) FROM main WHERE guild_id = ? AND user_id = ?",('"Fourth International"','"NSZ#9679"',))
result = cursor.fetchone()
print(result)
db.commit()
cursor.close()
db.close()


