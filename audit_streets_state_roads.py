import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

for event, element in ET.iterparse(OSMFILE):
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter('tag'):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if s == 'addr:street':
                state_roads_patt = re.compile(r'^((SR)|(FL))[\s-]', re.IGNORECASE)
                m = state_roads_patt.search(val)
                if m:
                    my_id = element.attrib['id']

                    print val,'element_id: ', my_id


        element.clear
