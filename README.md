#         WRANGLING OpenStreetMaps DATA WITH SQL

We chose a metro area in the US and using the freely available data from OpenStreetMap; we performed a cleaning procedure on many of the features, created an SQL database and made some queries to answer interesting questions.

MAP AREA: Tampa FL United States.

![image](https://github.com/jedfarm/Data-Wrangling-OpenStreetMaps-SQL/blob/master/TampaBay.png)


MapZen URL: https://mapzen.com/data/metro-extracts/metro/tampa_florida/

OSM XML 23 MB file, direct link:
https://s3.amazonaws.com/metro-extracts.mapzen.com/tampa_florida.osm.bz2

OpenStreetMaps: http://www.openstreetmap.org/search?query=Tampa%2C%20FL#map=10/27.8348/-82.2931


## Problems encountered in the .osm file:

I. Inconsistencies in zip codes:

   - Zip codes with nine digits (i.e. 33613-4649) which are correct, but they are just a few in comparison to the standard five-digit codes that will result in a different outcome when querying for zip codes.
   - Zip codes with the standard format that do not belong to the area of interest. One found (35655).
   - Two zip codes separated by a colon (33701:33704). This kind of format could be valid for ways (tiger:zip_left, tiger:zip_right) but not for nodes.
   - Zip codes starting with state letter code (i.e. FL 34236)
   - Missing values. One found (FL)


II. Inconsistencies found in street names:

- Simplified street names (i.e. 51st St W)
- Different names for the same way in the State Road System (FL 54, SR 54, State Road 54, West Brandon Blvd (S.R. 60))
- Non-unique name pattern for ways in the US Highway System (US Hwy 19, US 19, U.S. 19, US Highway 19, US-19)
- Suite numbers as part of the street names (Ulmerton Rd, Suite 107)
- Home numbers included in the street names (12000 US Highway 92)
- Street names containing foreign language (2300 Bee Ridge Rd, Sarasota, FL 34239, Vereinigte Staaten) 
- Street names containing portions of the mailing address (1400 1st Ave W, Bradenton 34205)
 

III. City names
- Non-unique city names: (Saint Petersburg, St. Petersburg)

IV. County names
- Non-unique county names (i.e., Pinellas and Pinellas, FL)
- More than one item in the place for County name (Manatee, FL; Polk, FL:Polk, FL)

V. Secondary tag attributes 'k' that belong to the PROBLEMCHARS group.

We found out that there were just three entries in our dataset that matched the PROBLEMCHARS pattern, all of them sharing issues of a particular kind (space characters within the name) and we decided to make a fix for those names allowing the inclusion of the data related into our database.

VI. Secondary tags containing 'census:population' and 'population' displayed some duplicated information.

We separated the year of the census from the population data in census:population and created a new key in the dictionary (census) to avoid the overwriting of the key 'population' under the rules applied for secondary tags containing ':' chars. 


## Overview of the data

We used SQL queries with the aid of the sqlite3 and pandas modules in Python to gather information about our database.

- File sizes:

  Using python hurry.filesize:


```python
import sqlite3
import pandas as pd
database = "TampaFlorida.db"
from pprint import pprint
import os
from hurry.filesize import size
dirpath = '/Users/jedfarm/Documents/UDACITY/P3'
files_list = []
for path, dirs, files in os.walk(dirpath):
    files_list.extend([(filename, size(os.path.getsize(os.path.join(path, filename)))) 
                       for filename in files])
for filename, size in files_list:
    if not filename.startswith('.'):
        print '{:.<40s}: {:5s}'.format(filename,size)
```

    nodes.csv...............................: 120M 
    nodes_tags.csv..........................: 6M   
    tampa_florida.osm.......................: 330M 
    TampaFlorida.db.........................: 184M 
    ways.csv................................: 9M   
    ways_nodes.csv..........................: 40M  
    ways_tags.csv...........................: 30M  



Here are the questions we answered using our database. 

- Top ten contributors to OpenStreetMap

- Amenities in the area, by number, top 10.

- Streets with more restaurants (top 10):

- Population

- How active has been the OpenStreetMaps community in the area? 


We also explored more advanced SQL capabilities, such as creating a VIEW, to find the top contributors of the past ten years.


### Files 

The Python scripts containing audit in their filenames were used to clean the data for the specific feature that appears next.

- audit_city_names.py
- audit_county_names.py
- audit_county_tags.py
- audit_population_tags.py
- audit street.py
- audit_street_suite.py
- audit_streetnames_num.py
- audit_streets_state_roads.py
- audit_tags.py
- audit_tag_types.py
- audit_us_highway_names.py
- audit zipcodes.py

- create_db.py …………… Creates a database from .csv files
- create_sample_osm.py
- file_sizes.py
- get_element.py
- clean_data.py …………… Creates .csv files from a .osm file
- make_a_view.py
- query_db.py  …………… Executes queries to the database
- references.txt 
- sample.osm

- P3.html
- P3.pdf



