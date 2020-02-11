import os
import re

import xml
import xml.etree.ElementTree as ET

if __name__ == '__main__':
    root_langs = './EmbeddedLangFiles'
    file_list = os.listdir(root_langs)
    for fname in file_list:
        child_path = f'{root_langs}/{fname}'
        xml_tree = ET.parse(child_path)
        break
