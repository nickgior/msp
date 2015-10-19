#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="msp", # your username
                      passwd="monkey2", # your password
                      db="msp") # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor() 

# Use all the SQL you like
cur.execute("SELECT * FROM user")

# print all the first cell of all the rows
for row in cur.fetchall() :
    print ", ".join( (str(x) for x in row))

#cur.execute("insert into user values(NULL,28834,\"joe\",\"Eagles60\",\"Joe McJoe\")")

#cur.execute("insert into user values(NULL,9288322,\"laura\",\"Tx7^PL33$\",\"Laura P\")")

#db.commit()


