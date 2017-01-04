import xml.etree.cElementTree as ET
import re
from collections import defaultdict
import operator
OSMFILE = 'tampa_florida.osm'

############## Auditing zip codes ###########################
zip_tampa = re.compile(r"^[3][3-4][0-9]{3}$")
zip_any = re.compile(r'^[1-9][0-9]{4}$')
zip_fl = re.compile(r'^FL', re.IGNORECASE)
zip_codes = defaultdict(int)
zip_codes_tiger = defaultdict(int)
other_zip = defaultdict(int)
typo_zip = {} # If zipcodes are 5 digits but do not belong to the Tampa area.
fl_zip = {} # For zips that begin with FL
for event, element in ET.iterparse(OSMFILE):
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter('tag'):
            s = tag.attrib['k']
            val = tag.attrib['v']
            if not re.search(zip_tampa, val):
                if s == 'addr:postcode':
                    zip_codes[val] += 1
                    if re.search(zip_any, val):
                        typo_zip[val] = element.attrib['id'] # Allow us to search the whole element
                    if re.search(zip_fl, val):
                        fl_zip[val] = element.attrib['id']
                if s =='tiger:zip_left' or s == 'tiger:zip_right':
                     zip_codes_tiger[val] +=1
                if s == 'postal_code':
                     other_zip[val] +=1
        element.clear
print 'zip_codes: ', zip_codes
print 'tiger: ', zip_codes_tiger
print 'postal_code: ', other_zip
print 'fixme codes: ', typo_zip
