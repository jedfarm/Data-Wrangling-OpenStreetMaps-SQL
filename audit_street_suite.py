import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'
# This script audits streets names for suite numbers

for event, element in ET.iterparse(OSMFILE):
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter('tag'):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if s == 'addr:street':
                if 'suite' in val.lower() or '#' in val.lower():
                    my_id = element.attrib['id']
                    print val, 'element_id: ', my_id
        element.clear
