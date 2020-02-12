import os
import re
import shutil
import json

import xml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


class XMLElement:
    """
    This class is used to store `xml.etree.ElementTree`'s properties with an addition `path` property.
    """

    def __init__(self, tag, text, attrib, path):
        self.tag = tag
        self.text = text
        self.attrib = attrib
        self.path = path

    def __repr__(self):
        # it seems that there is not better way to create multiline strings
        return f'''{self.path}
  tag: {self.tag}
  text: {repr(self.text)}
  attrib: {self.attrib}'''


def list_tree(e: Element, parent=None):
    e_list = []

    if parent is not None:
        e_path = f'{parent}/{e.tag}'
    else:
        e_path = e.tag

    xml_element = XMLElement(
        tag=e.tag,
        text=e.text,
        attrib=e.attrib,
        path=e_path,
    )

    if e.text is not None:
        if not e.text.isspace():
            e_list.append(xml_element)

    for child in e:
        e_list.extend(list_tree(child, parent=e_path))

    return e_list


def newtext_filename(filename):
    base_name, ext = os.path.splitext(filename)
    newtext_file = f'{base_name}_newtext{ext}'
    return newtext_file


def find_element(root: Element, path: list):
    if len(path) > 2:
        element = root.find(path[1])
        return find_element(element, path[1:])
    else:
        return root


def xml_path_to_elements(root: Element, path: list):
    # print(root.tag, path)
    if len(path) > 1:
        # print('return extend')
        element = root.find(path[1])
        elements = [element]
        _elements = xml_path_to_elements(element, path[1:])
        # print('_elements:', _elements)
        elements.extend(_elements)
        return elements
    else:
        # print('return empty list')
        return []


def remove_element(root: Element, path: str):
    path_components = path.split('/')

    if len(path_components) < 2:
        return

    elements = xml_path_to_elements(root, path_components)

    last_element = elements[-1]
    its_parent = elements[-2]
    its_parent.remove(last_element)


def convert_to_dict(obj):
    obj_dict = obj.__dict__

    return obj_dict


def remove_empty_element(e: Element, parent=None):
    children = [child for child in e]
    if len(children) == 0:
        if parent is not None:
            if e.text is not None:
                if e.text.isspace():
                    parent.remove(e)
                    return True
            else:
                if not e.tag == 'help' and not e.tag == 'description':
                    parent.remove(e)
                    return True
    else:
        removed = False
        for child in children:
            removed = removed or remove_empty_element(child, e)
        if removed:
            return remove_empty_element(e, parent)

    return False


def write_xml(root: Element, path: str):
    xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    with open(path, mode='w', encoding='utf-8') as out_file:
        out_file.write(xml_str)


if __name__ == '__main__':
    root_langs = 'c:/Users/qtng/source/repos/AFORM-1806/EPiServer.Forms.Samples/EmbeddedLangFiles'
    file_list = os.listdir(root_langs)

    base_lang = 'EPiServer.Forms.Samples_EN.xml'

    # filter newtext file and EN file
    file_list = list(filter(lambda x: not x == base_lang, file_list))
    file_list = list(filter(lambda x: not 'newtext' in x, file_list))

    # copy all lang files (except EN) and add `newtext` suffix
    for child_filename in file_list:
        child_path = f'{root_langs}/{child_filename}'

        newtext_path = f'{root_langs}/{newtext_filename(child_filename)}'

        shutil.copyfile(child_path, newtext_path)

    # re-list the directory as we want to keep the EN file for comparision
    file_list = os.listdir(root_langs)
    file_list = list(filter(lambda x: not 'newtext' in x, file_list))

    # list all the text in xml files
    langs_dict = {}
    for child_filename in file_list:
        child_path = f'{root_langs}/{child_filename}'
        xml_tree = ET.parse(child_path)
        element_list = list_tree(xml_tree.getroot())
        langs_dict[child_filename] = element_list

    base_el = langs_dict[base_lang]

    # filter EN as base language
    langs_to_diff = list(filter(lambda x: not x == base_lang, file_list))

    # create a diff based on text content of elements
    diff_lang_dict = {}
    for lang in langs_to_diff:
        print('='*10)
        print(lang)

        same_values = []
        diff_values = []

        element_list = langs_dict[lang]

        for e in element_list:
            base_element = list(filter(lambda x: x.path == e.path, base_el))
            if len(base_element) == 1:
                base_element = base_element[0]
                if e.text == base_element.text:
                    same_values.append(e)
                else:
                    diff_values.append(e)
            else:
                print(f'Base lang has multiple {repr(e.path)} entries')

        diff_lang_dict[lang] = {
            'same_values': same_values,
            'diff_values': diff_values,
        }

        print(f'same_values_len: {len(same_values)}')
        print(f'diff_values_len: {len(diff_values)}')

    with open('diff_lang_dict.json', mode='w', encoding='utf-8') as out_file:
        json_str = json.dumps(diff_lang_dict, default=convert_to_dict)
        out_file.write(json_str)

    for lang in langs_to_diff:
        print(f'Modifying {lang}')
        # remove `same_values` from origin language file
        lang_path = f'{root_langs}/{lang}'
        tree = ET.parse(lang_path)
        root = tree.getroot()

        same_values = diff_lang_dict[lang]['same_values']
        for element in same_values:
            remove_element(root, element.path)

        remove_empty_element(root)
        # write_xml(root, lang_path)
        tree.write(
            lang_path,
            encoding='utf-8',
            xml_declaration=True,
            short_empty_elements=False,
        )

        # remove `diff_values` from newtext language file
        newtext_path = f'{root_langs}/{newtext_filename(lang)}'
        tree = ET.parse(newtext_path)
        root = tree.getroot()

        diff_values = diff_lang_dict[lang]['diff_values']
        for element in diff_values:
            remove_element(root, element.path)

        remove_empty_element(root)
        # write_xml(root, newtext_path)
        tree.write(
            newtext_path,
            encoding='utf-8',
            xml_declaration=True,
            short_empty_elements=False,
        )
