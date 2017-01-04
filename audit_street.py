import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSMFILE = "tampa_florida.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Loop",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way", "Terrace",
               "Circle", "Highway", "Causeway", "Bayway", "Plaza", "Bypass", "Bridge"]
# UPDATE THIS VARIABLE
mapping = {"St": "Street", "St.": "Street", "Ave": "Avenue", "Rd.": "Road",
               "Blvd": "Boulevard", "Blvd.": "Boulevard", "Dr": "Drive", "Dr.": "Drive",
               "Ct": "Court", "Cswy": "Causeway", "Pkwy": "Parkway", "Av": "Avenue",
               "AVE": "Avenue", "Ave.": "Avenue", "Pky": "Parkway", "drive": "Drive",
               "lane": "Lane", "road": "Road", "st": "Street", "Cir": "Circle",
               "Bolevard": "Boulevard", "Rd": "Road", "HWY": "Highway", "Ln": "Lane",
               "Notth": "North", "dr": "Drive", "Hwy": "Highway"}

def audit_street_type(street_types, street_name):
   m = street_type_re.search(street_name)
   if m:
       street_type = m.group()
       if street_type not in expected:
           street_types[street_type].add(street_name)

def is_street_name(elem):
   return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
   osm_file = open(osmfile, "r")
   street_types = defaultdict(set)
   for event, elem in ET.iterparse(osm_file, events=("start",)):

       if elem.tag == "node" or elem.tag == "way":
           for tag in elem.iter("tag"):
               if is_street_name(tag):
                   audit_street_type(street_types, tag.attrib['v'])
   osm_file.close()
   return street_types

print audit(OSMFILE)
