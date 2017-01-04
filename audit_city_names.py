import xml.etree.cElementTree as ET
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

osm_file = open(OSMFILE, "r")
city_names = defaultdict(int)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if s == 'addr:city':
                city_names[val] += 1

osm_file.close()
print city_names
