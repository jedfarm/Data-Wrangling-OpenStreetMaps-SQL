"""
This script creates a View (myview), which contains the number of changes made on
the map grouped by user and by year.
This will allow us to make more readable queries for certain kind of questions.

"""
import sqlite3

database = "TampaFlorida.db"

db = sqlite3.connect(database)
mydb = db.cursor()
mydb.execute("""CREATE VIEW myview AS SELECT e.user, strftime('%Y', e.timestamp) as Year,
COUNT(*) as num
FROM (SELECT user, timestamp FROM nodes UNION ALL SELECT user, timestamp FROM ways ) e
GROUP BY e.user, strftime('%Y', e.timestamp) ORDER BY num DESC,
strftime('%Y', e.timestamp) DESC""")
mydb.close()
