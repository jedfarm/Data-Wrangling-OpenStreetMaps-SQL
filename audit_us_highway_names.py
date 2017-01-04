import xml.etree.cElementTree as ET
import re
from collections import defaultdict

highways_patt = re.compile(r'((US)|(U.S.))[\s-]')

OSMFILE = 'tampa_florida.osm'
us_hwy = defaultdict(int)
for event, element in ET.iterparse(OSMFILE):
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter('tag'):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if s == 'addr:street':
                m = highways_patt.search(val)
                if m:
                    us_hwy[val]+=1
print us_hwy
