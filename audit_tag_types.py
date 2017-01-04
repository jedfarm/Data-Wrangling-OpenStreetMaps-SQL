import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

lower = re.compile(r'^([a-z]|_)*[0-9]?$')
lower_colon = re.compile(r'^([a-z]|_)+:([a-z0-9]|_)+')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
other_list = []
problem_list = []
other_id_list = []

for event, element in ET.iterparse(OSMFILE):
    if element.tag == 'node' or element.tag == 'way':
        for tag in element.iter('tag'):
                s = tag.attrib['k'].lower()

                if re.search(lower, s):
                    keys['lower'] +=1
                elif re.search(lower_colon, s):
                    keys['lower_colon'] +=1
                elif re.search(problemchars, s):
                    keys['problemchars'] +=1
                    problem_list.append(s)
                else:

                    keys['other'] +=1
                    other_list.append((s, element.attrib['id']))
                    other_id_list.append(element.attrib['id'])

#
        element.clear
print 'keys:', keys
print 'problem_list:', problem_list
print 'other_list:', other_list
