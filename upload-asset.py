#!/usr/bin/env python

# System packages
import argparse
import os

# Modules
from ubuntudesign import AssetMapper


# Get arguments
# ===
parser = argparse.ArgumentParser(
    description='Upload a file to an assets server.'
)
parser.add_argument(
    'file-path',
    help='The path to the file to upload'
)
parser.add_argument(
    '--url-path',
    help='The URL path to upload the file to'
)
parser.add_argument(
    '--auth-token',
    help='The URL of the server',
    default=os.environ.get('ASSETS_SERVER_TOKEN')
)
parser.add_argument(
    '--tags',
    help='The URL of the server',
    default=''
)
parser.add_argument(
    '--server-url',
    help='The URL of the server',
    default=os.environ.get('ASSETS_SERVER_URL', 'http://localhost:8080/v1/')
)

cmd_args = vars(parser.parse_args())

file_path = cmd_args['file-path']
url_path = cmd_args['url_path']
server_url = cmd_args['server_url']
auth_token = cmd_args['auth_token']
tags = cmd_args['tags']

asset_mapper = AssetMapper(
    server_url=server_url,
    auth_token=auth_token
)
with open(file_path) as upload_file:
    if url_path:
        response = asset_mapper.create_at_path(
            asset_content=upload_file.read(),
            url_path=url_path,
            tags=tags
        )
    else:
        response = asset_mapper.create(
            asset_content=upload_file.read(),
            friendly_name=upload_file.name,
            tags=tags
        )

print response
