import os

BRANCH_TO_MERGE_INTO = "test_production"
BRANCH_TO_MERGE = "travis_integration"
GITHUB_URL = "https://github.com/"
GITHUB_REPO = "dante-signal31/vdist.git"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIT_USERNAME = "dante-signal31"
GIT_EMAIL = "dante.signal31@gmail.com"
VDIST_CONFIGURATION = "packaging/vdist_build.cnf"
VERSION_PREFIX = "v"
BINTRAY_TEMPLATES_PATH = "packaging/bintray_descriptor_templates"
BINTRAY_DESCRIPTORS_PATH = "packaging/"
BINTRAY_DESCRIPTOR_NAME_FORMAT = "vdist_{tag}_bintray_descriptor.json"
