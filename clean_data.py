# coding: utf-8
#!/usr/bin/env python
"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL
database.
To do so you will parse the elements in the OSM XML file, transforming them from document
format to tabular format, thus making it possible to write to .csv files.  These csv files can
then easily be imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct
  format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write
the output to csv files. Your task is to complete the shape_element function that will
transform each element into the correct format. To make this process easier we've already
defined a schema (see the schema.py file in the last code tab) for the .csv files and the
eventual tables. Using the cerberus library we can validate the output against this schema to
ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags
are child tags of node which have the tag name/type: "tag". Each dictionary should have the
following fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the
  colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag
  type and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they and they should be ignored and kept as
  part of the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.

The final return value for a "node" element should look something like:

{'node': {'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
       'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
      'changeset': 5288876},
 'node_tags': [{'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'name',
                'value': "Shelly's Tasty Freeze",
                'type': 'regular'}]}

### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules
asfor "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list
of dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element

The final return value for a "way" element should look something like:

{'way': {'id': 209809850,
         'user': 'chicago-buildings',
         'uid': 674454,
         'version': '1',
         'timestamp': '2013-03-13T15:58:04Z',
         'changeset': 15353317},
 'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
 'way_tags': [{'id': 209809850,
               'key': 'housenumber',
               'type': 'addr',
               'value': '1412'},
              {'id': 209809850,
               'key': 'street',
               'type': 'addr',
               'value': 'West Lexington St.'},
              {'id': 209809850,
               'key': 'street:name',
               'type': 'addr',
               'value': 'Lexington'},
              {'id': '209809850',
               'key': 'street:prefix',
               'type': 'addr',
               'value': 'West'},
              {'id': 209809850,
               'key': 'street:type',
               'type': 'addr',
               'value': 'Street'},
              {'id': 209809850,
               'key': 'building',
               'type': 'regular',
               'value': 'yes'},
              {'id': 209809850,
               'key': 'levels',
               'type': 'building',
               'value': '1'},
              {'id': 209809850,
               'key': 'building_id',
               'type': 'chicago',
               'value': '366409'}]}
"""

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "tampa_florida.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# By introducing a slight modification in the patterns a lot more of data can be included
#LOWER = re.compile(r'^([a-z]|_)*$')
LOWER = re.compile(r'^([a-z]|_)*[0-9]?$')
#LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z0-9]|_)+')

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
#Fortunatelly in our dataset there are just 3 items that match the PROBLEMCHARS pattern and
# they have an easy fix.
SPACE_PROBLEMCHARS = re.compile(r'^[a-z]+(\s[a-z]+)+$')
# Two items match the following pattern:
DASH = re.compile(r'^[a-z]+\-[a-z]+$')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
homenumber_re = re.compile(r'^\d\d\d\d\s')
zip_tampa = re.compile(r"^[3][3-4][0-9]{3}$")
comma_patt = re.compile(r'^\d+,\d+$')

state_roads_patt = re.compile(r'^((SR)|(FL))[\s-]', re.IGNORECASE)

cardinals = ['North','South', 'East', 'West', 'Northeast', 'Northwest', 'Southeast',
                 'Southwest', 'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

################################### MY FUNCTIONS #############################################

def char_repl(matchobj):
    if matchobj.group(0) == '-': return '_'
    elif matchobj.group(0) == ' ': return '_'
    else: return ''

def split_suite(s):
    '''Some street names contain suite numbers. This function splits up name and suite into
    different keys of a dictionary for further treatment. '''
    d = {}
    s_lower = s.lower()
    targets = ['suite', 'S #', '#']
    for t in targets:
        if s_lower.find(t) > -1:
            name = s[:s_lower.find(t)].strip()
            suite = s[s_lower.find(t)+ len(t):].strip()
            break
    if name.find(',') > -1:
        name = name[:name.find(',')]
    d['name'] = name

    if suite.find('#') > -1:
        suite = suite[1:].strip()
    d['suite'] = suite
    return d

def fix_suite(val):
    d = {}
    addr_dict = split_suite(val)
    d['key'] = 'suite'
    d['value'] = addr_dict['suite']
    d['type'] = 'addr'
    return d

def fix_zipcodes(zipcodes):
    '''Fix zip codes of the form 3####-#...#, 3####:#...# or Fl 3####, with the number
    following the 3 being just 3 or 4, according with the zip codes of Tampa area. The output
    is just a 5 digits string. If any other pattern is detected, the function returns FIXME'''

    fixed_zip = 'FIXME'
    pattern1 = re.compile(r'^3[3-4]\d\d\d')
    pattern2 = re.compile(r'^FL\s+3[3-4]\d\d\d$',  re.IGNORECASE)
    if re.search(pattern1, zipcodes):
        fixed_zip = zipcodes[:5]
    elif re.search(pattern2, zipcodes):
        fixed_zip = zipcodes[zipcodes.find('3'):]
    elif zipcodes == '35655': # A typo found for a zip code related to Trinity, FL.
        fixed_zip = '34655'
    return fixed_zip


def split_homenumber(name):
    '''In some cases home numbers appear at the beginning of the street names'''
    d ={}
    s_split = name.split()
    if s_split[0].isdigit() and int(s_split[0]) > 1000:
        d['homenumber'] = s_split[0]
        del s_split[0]
        d['name'] = ' '.join(w for w in s_split)
    return d

def unif_ushwy_names(name):
    """ Provides a standard name for the US Highways System -> US Highway #"""
    highways_patt = re.compile(r'((US)|(U.S.))[\s-]')
    if re.search(highways_patt, name):
        name = re.sub(r'U.S.', 'US', name)
        name = re.sub(r'-', ' ', name)
        name = re.sub(r'[Hh][Ww][Yy]', 'Highway', name)
        name = re.sub (r'\(FL\)', '', name)

        if 'highway' not in name.lower():
            name = re.sub(r'US', 'US Highway', name)

    return name.strip()

def unif_state_road_names(name):
    if re.search(state_roads_patt, name):
        name = re.sub(r'(SR)|(FL)[\s-]', 'State Road ', name)
    return name.strip()

def update_name_2(name, mapping):
    '''Fixes the oversimplification of cardinals points and quadrants at the beginning or the
    end of the street name. Also gives a full name for the type of street in the one before
    the last word of the name. Corrects the name of the streets that belong to US Highways
    System by calling unif_ushwy_names function. Corrects the SR and FL names by calling
    unif_state_road_names function '''


    s_list = name.split()
# Removing the possible point after the cardinal(i.e. N.) keeps cardinals list short
    if '.' in s_list[0]:
        s_list[0]= s_list[0][0]
    elif '.' in s_list[len(s_list)-1]:
        s_list[len(s_list)-1] = s_list[len(s_list)-1][0]
    last = s_list[len(s_list)-1]

    if last in cardinals:
        if cardinals.index(last) > 7:
            s_list[len(s_list)-1] = cardinals[cardinals.index(last)-8]

        if s_list[len(s_list)-2] in mapping:
            s_list[len(s_list)-2] = mapping.get(s_list[len(s_list)-2])

        if s_list[0] in cardinals and cardinals.index(s_list[0]) > 7:
            s_list[0] = cardinals[cardinals.index(s_list[0])-8]

    elif s_list[0] in cardinals and cardinals.index(s_list[0]) > 7:
        s_list[0] = cardinals[cardinals.index(s_list[0])-8]
        if s_list[len(s_list)-1] in mapping:
            s_list[len(s_list)-1] = mapping.get(s_list[len(s_list)-1])
    name = ' '.join(s_list)

    name = unif_state_road_names(name)
    name = unif_ushwy_names(name)
    return name

def strip_cardinals(name):
    s_list = name.split()
    if s_list[0] in cardinals:
        del s_list[0]
        #name = ' '.join(s_list)
    if s_list[len(s_list)-1] in cardinals:
        del s_list[-1]
    name = ' '.join(s_list)
    return name



def fix_city_names(name):

    saint_pete_fixlist = ['St. Petersburg', 'St Petersbug',
                      'St Petersburg', 'St Petersburg ', 'St. Petersburg, Fl']
    land_o_lakes_fixlist = ['Land O Lakes, Fl', 'Land O Lakes']

    name_list = name.split()
    if len(name_list) == 1:
        name = name.capitalize().strip()
    elif len(name_list) > 1:
        name = ' '.join([s.capitalize() for s in name_list])
    else:
        name = 'FIXME'

    if name in saint_pete_fixlist:
        name = 'Saint Petersburg'
    elif name in land_o_lakes_fixlist:
        name = "Land O' Lakes"
    elif name == 'Tampa Bay':
        name = 'Tampa'
    elif name == 'Palm Harbor, Fl.':
        name = 'Palm Harbor'
    elif name == 'Clearwarer Beach':
        name = 'Clearwater Beach'

    return name

def fix_county_name(name):
    """ Returns a list with the name(s) of the county(ies) that appeared in name"""
    names = set()
    name_out = []
    name = re.sub(r', FL', '', name).strip()
    name = re.sub(r';', ' ', name)
    name = re.sub(r':', ' ', name)
    name_list = name.split()
    for item in name_list:
        names.add(item)
    name_out = list(names)
    return name_out

###############################################################################################

def update_name(name, mapping):
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    pat = re.search(street_type_re, name).group()
    if pat in mapping:
        name = re.sub(pat,mapping.get(pat), name)
    return name


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way", "Terrace",
            "Circle", "Highway", "Bayway", "Causeway", "Loop"]
    mapping = {"St": "Street", "St.": "Street", "Ave": "Avenue", "Rd.": "Road",
            "Blvd": "Boulevard", "Blvd.": "Boulevard", "Dr": "Drive", "Dr.": "Drive",
            "Ct": "Court", "Cswy": "Causeway", "Pkwy": "Parkway", "Av": "Avenue",
            "AVE": "Avenue", "Ave.": "Avenue", "Pky": "Parkway", "drive": "Drive",
            "lane": "Lane", "road": "Road", "st": "Street", "Cir": "Circle",
            "Bolevard": "Boulevard", "Hwy": "Highway", "Ln": "Lane", "Notth": "North",
            "Rd": "Road", "HWY": "Highway"}

    addr_keys =['city', 'postcode', 'state', 'country']

    if element.tag == 'node' or element.tag == 'way':
        tags = []
        for tag in element.iter('tag'):
            tag_att = {}
            tag_att['id']= element.attrib['id']
            tag_att['value']= tag.attrib['v']


            s = tag.attrib['k'].lower()
            val = tag.attrib['v']

            if re.search(LOWER, s):
                tag_att['key'] = s
                if s == 'postal_code' and val == '(813) 643-1700':
                    tag_att['key'] = 'phone' # Fixing a  particular mistake

                if 'fixme' in s:       # Keeps consistency with 'fixme: ...' in LOWER_COLON.
                    tag_att['type'] = 'fixme'
                else:
                    tag_att['type'] = 'regular'

                # Fix for some population numbers with thousand separator.
                if s == 'population':
                    val = val.strip()
                    if re.search(comma_patt, val):
                        val = val[:val.find(',')]+val[val.find(',')+1:]
                    tag_att['value'] = val

            elif re.search(LOWER_COLON, s):
                # Cleaning census and source to avoid the overwriting of
                # existing 'population' keys
                if s =='census:population':
                    tag_att['key'] = 'census'
                    tag_att['type'] = 'year'
                    tag_att['value'] = val.split(';')[1]
                elif s == 'source:population':
                    tag_att['key'] = 'refpopulation'
                    tag_att['type'] = s[: s.find(':')]
                else:
                    tag_att['key'] = s[s.find(':')+1:]
                    tag_att['type'] = s[: s.find(':')]

                if s == 'addr:street':
                # Cleaning for 'suite' in street names
                    if ' suite' in val.lower() or '#' in val.lower() :
                        addr_dict = split_suite(val)
                        suite_dict = fix_suite(val)
                        suite_dict['id'] = element.attrib['id']
                        tags.append(suite_dict)

                        val = addr_dict['name']

            ######### This is a fix for two nodes with german names. ###########
                    elif 'Vereinigte Staaten' in val:

                        my_values = val.split(',')
                        y = my_values[2].split() # splits up FL and the zip code
                        my_values[2]= y[1]
                        val = my_values.pop(0) # New street name, contains homenumber
                        my_values.pop()
                        my_values.append(y[0])
                        my_values.append('US')

                        for i in range(len(addr_keys)):
                            new_addr = {}
                            new_addr['key']= addr_keys[i]
                            new_addr['type'] = 'addr'
                            new_addr['value'] = my_values[i]
                            new_addr['id'] = element.attrib['id']
                            tags.append(new_addr)

                    # Fix for a single node
                    elif element.attrib['id'] == '1029614792':
                        my_values = val.split(',')
                        y = my_values[1].split() # splits up the city and the zip code
                        my_values[1] = y[0]
                        val = my_values.pop(0) # New street name, contains homenumber
                        my_values.append(y[1])
                        my_values.append('FL')
                        my_values.append('US')
                        for i in range(len(addr_keys)):
                            new_addr = {}
                            new_addr['key']= addr_keys[i]
                            new_addr['type'] = 'addr'
                            new_addr['value'] = my_values[i]
                            new_addr['id'] = element.attrib['id']
                            tags.append(new_addr)

                    # Fix for a single node
                    elif element.attrib['id'] == '2266845486':
                        my_values = val.split(',')
                        a = my_values[0][:my_values[0].find('St')].strip()
                        b = my_values[0][my_values[0].find('St'):].strip()
                        my_values[0] = a
                        my_values[1] = b
                        my_values.append('00000')# zip code already exists.
                        my_values.append('FL')
                        my_values.append('US')
                        val = my_values.pop(0)
                        for i in range(len(addr_keys)):
                            if i != 1:
                                new_addr = {}
                                new_addr['key']= addr_keys[i]
                                new_addr['type'] = 'addr'
                                new_addr['value'] = my_values[i]
                                new_addr['id'] = element.attrib['id']
                                tags.append(new_addr)

                    #Cleaning for home numbers in street names
                    if re.search(homenumber_re, val):
                        new_homenum ={}
                        h_dict = split_homenumber(val)
                        new_homenum['id'] = element.attrib['id']
                        new_homenum['key'] = 'homenumber'
                        new_homenum['type'] = 'addr'
                        new_homenum['value'] = h_dict['homenumber']
                        tags.append(new_homenum)

                        val = h_dict['name']

                    #Cleaning for oversimplified street names
                    m = re.search(street_type_re, val)
                    if m:
                        street_type = m.group()

                        #Creating a new tag to unify the street names (same street names
                        # without leading or trailing cardinals)
                        uniq_names = {}
                        uniq_names['id'] = element.attrib['id']
                        uniq_names['key'] = 'u_street'
                        uniq_names['type'] = 'addr'

                        if street_type not in expected:
                            long_street_name = update_name_2(update_name(val, mapping),
                                                            mapping)

                        else:
                            long_street_name = update_name_2(val, mapping)

                        uniq_names['value'] = strip_cardinals(long_street_name)
                        tag_att['value'] = long_street_name
                        tags.append(uniq_names)

                # More cleaning for suites
                if s == 'addr:housenumber':
                    if  ' suite' in val.lower():
                        addr_dict = split_suite(val)
                        suite_dict = fix_suite(val)
                        suite_dict['id'] = element.attrib['id']
                        tags.append(suite_dict)

                        tag_att['value'] = addr_dict['name']

                #Cleaning postal codes
                if s == 'addr:postcode':
                    if not re.search(zip_tampa, val):
                        tag_att['value'] = fix_zipcodes(val)

                #Cleaning city names
                if s == 'addr:city':
                    tag_att['value'] = fix_city_names(val)

                #Cleaning county names
                if s == 'tiger:county':
                    extra_counties ={}
                    county_names = fix_county_name(val)
                    tag_att['value'] = county_names[0]
                    if len(county_names) > 1:
                        del county_names[0]
                        extra_counties['id'] = element.attrib['id']
                        extra_counties['type'] = 'tiger'
                        for i, name in enumerate(county_names):
                            extra_counties['key'] = 'county' + str(i + 1)
                            extra_counties['value'] = name
                            tags.append(extra_counties)

            # Fixing a particular case of problemchars
            elif re.search(SPACE_PROBLEMCHARS, s):
                tag_att['key'] = re.sub(r'\s', char_repl, s)
                tag_att['type'] = 'regular'

            #Including the last two items:
            elif re.search(DASH, s):
                    tag_att['key'] = re.sub(r'\-', char_repl, s)
                    tag_att['type'] = 'regular'

            else:
                continue

            tags.append(tag_att)

        if element.tag == 'node':
            for field in NODE_FIELDS:
                node_attribs[field] = element.attrib[field]
            # Bowling alley out of business with problematic zip code
            if node_attribs['id'] != '2061928287':
                return {'node': node_attribs, 'node_tags': tags}

        elif element.tag == 'way':
            for field in WAY_FIELDS:
                way_attribs[field] = element.attrib[field]


            way_nodes =[]
            for i, nd in enumerate(element.iter('nd')):
                nd_att ={}
                nd_att['id'] = element.attrib['id']
                nd_att['node_id'] = nd.attrib['ref']
                nd_att['position'] = i
                way_nodes.append(nd_att)

            return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
