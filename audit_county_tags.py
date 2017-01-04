import xml.etree.cElementTree as ET
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

# Searching for tags related to county names
osm_file = open(OSMFILE, "r")
county_tags = defaultdict(int)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if 'county' in s.lower():
                county_tags[s]+=1

osm_file.close()
print county_tags
