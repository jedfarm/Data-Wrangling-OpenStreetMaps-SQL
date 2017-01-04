import xml.etree.cElementTree as ET
import re
from collections import defaultdict
import operator

OSMFILE = 'tampa_florida.osm'


######### Audit the number of different primary and secondary tags (keys)  ################

tag_count = defaultdict(int) # Number of different tags
key_count = defaultdict(int) # Number of different keys in tag.attrib['k']

for event, element in ET.iterparse(OSMFILE):
    tag_count[element.tag] += 1
    for tag in element.iter('tag'):
        key_count[tag.attrib['k']] +=1
    element.clear

print 'Number of different tags: ', tag_count
print ' '
print 'Number of different keys: ', len(key_count)
print ' '
sorted_keys = sorted(key_count.items(), key=operator.itemgetter(1))
sorted_keys.reverse()

print 'Top 20 keys: ', sorted_keys[:20]
