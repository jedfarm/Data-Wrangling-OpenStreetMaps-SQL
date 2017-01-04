import sqlite3
import pandas as pd

database = "TampaFlorida.db"

##################    QUERIES HERE    ##################

# Checking out the integrity of the postal_code tag
query01 = """SELECT value as zip_code, COUNT(*) as occurrences FROM ways_tags
WHERE key = 'postal_code' GROUP BY value;"""

# Number of nodes
query02 = """SELECT COUNT(*) as nodes FROM nodes;"""

#Number of ways
query03 = """SELECT COUNT(*) as ways FROM ways;"""

# Number of unique users
query04 = """SELECT COUNT(DISTINCT(e.uid)) as users
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;"""

# Top ten contributors
query05 = """SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;"""

# Amenities by number, top ten
query06 = """SELECT value, COUNT(*) as num FROM nodes_tags WHERE key='amenity'
GROUP BY value ORDER BY num DESC LIMIT 10;"""

# Streets with more restaurants, top ten
query07 = """SELECT nodes_tags.value as street, COUNT(*) as restaurants FROM nodes_tags
JOIN (SELECT DISTINCT(id), value FROM nodes_tags WHERE key='amenity'
and value = 'restaurant') i ON nodes_tags.id = i.id WHERE nodes_tags.key = 'street'
GROUP BY nodes_tags.value ORDER BY restaurants DESC LIMIT 10;"""

# Streets with more restaurants, top ten with unique street names
query08 = """SELECT nodes_tags.value as street, COUNT(*) as restaurants FROM nodes_tags
JOIN (SELECT DISTINCT(id), value FROM nodes_tags WHERE key='amenity'
and value = 'restaurant') i ON nodes_tags.id = i.id WHERE nodes_tags.key = 'u_street'
GROUP BY nodes_tags.value  ORDER BY restaurants DESC LIMIT 10;"""

# Counties covered in the dataset
query09 = """SELECT tags.value as county, COUNT(*) as count FROM (SELECT * FROM nodes_tags
UNION ALL SELECT * FROM ways_tags) tags WHERE tags.key='county' or tags.key ='county1'
GROUP BY tags.value ORDER BY count DESC;"""

# Top ten populated places in the area
query10 = """SELECT nodes_tags.value as place, i.value as population FROM nodes_tags JOIN
(SELECT DISTINCT(id), value FROM nodes_tags WHERE key='population') i
ON nodes_tags.id = i.id WHERE nodes_tags.key = 'name'ORDER BY i.value *1
DESC LIMIT 10"""

# Changes performed on the map of the area, per year
query11 = """SELECT strftime('%Y', t.timestamp) as Year, COUNT(*) as changes
FROM (SELECT nodes.timestamp FROM nodes UNION ALL SELECT ways.timestamp FROM ways) t
GROUP BY Year ORDER BY Year DESC;"""

# IMPORTANT NOTICE: The following query requires a VIEW (myview) to be created.
# It is necessary to run the script 'make_a_view.py' before proceding with query12.

# Top contributor each year since 2007.
query12 = """SELECT user, myview.Year, num as changes FROM myview
INNER JOIN (SELECT Year, MAX(num) AS maxnum FROM myview GROUP BY Year) q
ON myview.Year = q.Year AND myview.num = q.maxnum ORDER BY myview.Year DESC;"""


 ############## Change query at will ####################
db = sqlite3.connect(database)
df = pd.read_sql_query(query01, db)
db.close()
print df



# Using SQL queries we can also find out the size of the database:
"""
db = sqlite3.connect(database)
df1 = pd.read_sql_query('PRAGMA page_size;', db)
df2 = pd.read_sql_query('PRAGMA page_count;', db)
db.close()
print 'Database size: ', df1.loc[0][0] * df2.loc[0][0], 'bytes'

"""
