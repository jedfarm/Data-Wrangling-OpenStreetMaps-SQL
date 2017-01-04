import xml.etree.cElementTree as ET
OSMFILE = 'tampa_florida.osm'

# This allows a closer look to a whole element if anything wrong is found in the audits.
elemID = '450105376' # Change the element id here to explore the element of interest


def get_elements(osmfile, id_num):
    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            if elem.attrib['id'] == id_num:
                print elem.tag
                for tag in elem.iter():
                    print tag.attrib

    osm_file.close()

get_elements(OSMFILE, elemID)
