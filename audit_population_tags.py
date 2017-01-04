import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = 'tampa_florida.osm'

# Finding possible 'population' key issues
# For tags of the form name1:name2 we were instructed to make key = name2 and
# type = name1. It happens that there are tags named population and other tags
# of the form name1:population. If we follow the rules without any workaround
# we will overwrite the existing key population.

population_patt = re.compile(r'^([a-z]+:)?population(:[a-z]+)?$')

osm_file = open(OSMFILE, "r")
pop_types = defaultdict()
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if re.search(population_patt, tag.attrib['k']):
                val = tag.attrib['k']
                if val not in pop_types:
                    pop_types[val] = 1

                else:
                    pop_types[val] = pop_types.get(val) + 1

osm_file.close()
print pop_types
