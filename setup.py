#! /usr/bin/env python3

# Standard library
import sys

# Packages
from setuptools import setup

# The importer relies heavily on glob recursive search capability.
# This was only introduced in Python 3.5:
# https://docs.python.org/3.6/whatsnew/3.5.html#glob
assert sys.version_info >= (3, 5), "upload-assets requires Python 3.5 or newer"

setup(
    name="canonicalwebteam.upload-assets",
    version="0.3.0",
    author="Canonical webteam",
    author_email="robin+pypi@canonical.com",
    url="https://github.com/canonical-web-and-design/upload-assets",
    packages=["canonicalwebteam.upload_assets"],
    description=(
        "A command-line tool for uploading assets to an assets server."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["requests>=2.13.0"],
    scripts=["upload-assets"],
)
