import sqlite3
conn = sqlite3.connect('hackathon.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE person
             (userid int, src_lat float, src_long float, dst_lat float, dst_long float)''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
