import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'
# This script audits specifically streets names starting with the home number

for event, element in ET.iterparse(OSMFILE):
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter('tag'):
            s = tag.attrib['k']
            val = tag.attrib['v']

            if s == 'addr:street':
                street = val
                homenum_patt = re.compile(r'^\d\d\d\d\s?')
                m = homenum_patt.search(street)
                if m:
                    my_id = element.attrib['id']
                    print street, 'element_id: ', my_id
        element.clear
