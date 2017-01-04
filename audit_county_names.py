import xml.etree.cElementTree as ET
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

# Checking the integrity of county related tags
osm_file = open(OSMFILE, "r")
gnis_county = defaultdict(int)
gnis_county_num = defaultdict(int)
gnis_county_id = defaultdict(int)
gnis_county_name = defaultdict(int)
tiger_county = defaultdict(int)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if  s == 'gnis:County':
                gnis_county[val]+=1
            elif s == 'gnis:County_num':
                gnis_county_num[val]+=1
            elif s == 'gnis:county_id':
                gnis_county_id[val]+=1
            elif s == 'gnis:county_name':
                gnis_county_name[val]+=1
            elif s == 'tiger:county':
                tiger_county[val] +=1
                if ',' in val or ';' in val:
                    print val, 'elem_id:', elem.attrib['id']

osm_file.close()

print gnis_county
print gnis_county_num
print gnis_county_id
print gnis_county_name
print tiger_county
