#!/usr/bin/env python

import sys
import traceback
if sys.version_info.major < 3:
    import ci_tools as tools
    from .ci_constants import *
else:
    from ci_scripts import ci_tools as tools
    from ci_scripts.ci_constants import *


def set_contact_data(username, email):
    print("Setting user and email for current commit...")
    tools.run_console_command(
        "git config --local user.name '{0}'".format(username))
    tools.run_console_command(
        "git config --local user.email '{0}'".format(email))
    print("User and email set.")


def set_version_tag(prefix):
    print("Setting tag for current commit...")
    version = tools.get_current_version(VDIST_CONFIGURATION)
    version_string = "{0}{1}".format(prefix, version)
    tools.run_console_command("git tag '{0}'".format(version_string))
    # tools.run_console_command("git push origin '{0}'".format(version_string))
    print("Tag set.")
    return version_string

# To make just one push, now tagging is called from merge_with_production_script.
#
# if __name__ == '__main__':
#     try:
#         set_contact_data(GIT_USERNAME, GIT_EMAIL)
#         set_version_tag(VERSION_PREFIX)
#     except:
#         traceback.print_exc(file=sys.stdout)
#         sys.exit(1)
#     else:
#         sys.exit(0)