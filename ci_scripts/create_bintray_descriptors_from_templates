#!/usr/bin/env python

import json
import os.path
import sys
if sys.version_info.major < 3:
    import ci_tools as tools
    from .ci_constants import *
else:
    from ci_scripts import ci_tools as tools
    from ci_scripts.ci_constants import *


def read_templates():
    templates = {}
    for template_filename in os.listdir(BINTRAY_TEMPLATES_PATH):
        with open(template_filename) as json_data:
            templates[template_filename] = json.load(json_data)
    return templates


def remove_extension(filename):
    name_without_extension = os.path.splitext(filename)
    return name_without_extension


def create_descriptor(name, content, version):
    tag = remove_extension(name)
    descriptor_name = BINTRAY_DESCRIPTOR_NAME_FORMAT.format(tag=tag)
    descriptor_folder_path = os.path.join(BINTRAY_DESCRIPTORS_PATH,
                                          descriptor_name)
    content["version"]["name"] = "{prefix}{version}".format(prefix=VERSION_PREFIX,
                                                            version=version)
    with open(descriptor_folder_path) as descriptor:
        json.dump(content, descriptor)


if __name__ == '__main__':
    templates = read_templates()
    current_version = tools.get_current_version(VDIST_CONFIGURATION)
    for template_name, template_content in templates.items():
        create_descriptor(template_name, template_content, current_version)
