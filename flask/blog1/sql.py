# sql.py create a simple sqlite3 table

import sqlite3

with sqlite3.connect("blog.db") as connection:
    cur = connection.cursor()

    cur.execute("CREATE TABLE posts (title TEXT, post TEXT)")

    cur.execute('INSERT INTO posts VALUES("First", "First blog post.")')
    cur.execute('INSERT INTO posts VALUES("Second", "Second blog post.")')
    cur.execute('INSERT INTO posts VALUES("Third", "Getting experienced now!")')
