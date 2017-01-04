from pprint import pprint
import os
from hurry.filesize import size
dirpath = '/Users/jedfarm/Documents/UDACITY/P3'
files_list = []
for path, dirs, files in os.walk(dirpath):
    files_list.extend([(filename, size(os.path.getsize(os.path.join(path, filename))))
                       for filename in files])
for filename, size in files_list:
    if not filename.startswith('.'):
        print '{:.<40s}: {:5s}'.format(filename,size)
