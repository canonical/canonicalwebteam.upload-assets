#! /usr/bin/env python3

"""
A command-line tool for uploading assets to the assets server.

The only dependency is `requests`:

$ pip install requests
$ wget https://gist.githubusercontent.com/nottrobin/bad4d1b8f880bbb23ed10f5457d976bc/raw/707305dbd616dc46f38d0524e2f6248415173f57/upload-assets.py

Usage:

$ ./upload-assets.py --api-token xxxxxxxx asset1.png asset2.png  # Upload specific assets
$ ./upload-assets.py --api-token xxxxxxxx a_dir > output.json    # Upload all assets in a directory (recursively), store JSON output in a file
$ API_SECRET_TOKEN=xxxx ./upload-assets.py .                     # Upload all assets in the current directory, getting the API secret from an environment variable
"""

# Core packages
import argparse
import base64
import json
import os
import glob
import sys
import urllib

# Third party packages
import requests


api_base_url = os.environ.get('API_BASE_URL', 'https://assets.ubuntu.com/v1/')
api_secret_token = os.environ.get('API_SECRET_TOKEN')

parser = argparse.ArgumentParser(
    description='Upload assets from this directory'
)
parser.add_argument(
    '-u', '--api-url',
    help='The API base URL', default=api_base_url
)
parser.add_argument(
    '-s', '--api-token',
    help='The secret authentication token for the API',
    required=not bool(api_secret_token),
    default=api_secret_token
)
parser.add_argument(
    '-p', '--url-path',
    help='The URL path to upload the file to'
)
parser.add_argument(
    '-t', '--tags',
    help='Tags for uploaded assets', default='auto-upload'
)
parser.add_argument(
    'upload_paths',
    help='A list of paths to files or directories to upload',
    nargs='+'
)
args = vars(parser.parse_args())

uploaded = []


def upload_file(filepath, args, error_on_exists=False):
    filename = os.path.basename(filepath)

    with open(filepath, 'rb') as asset_file:
        content = asset_file.read()

    response = requests.post(
        args['api_url'],
        data={
            'asset': base64.b64encode(content),
            'friendly-name': filename.replace(' ', '+'),
            'url-path': args['url_path'],
            'tags': args['tags'],
            'type': 'base64',
            'token': args['api_token']
        }
    )

    if error_on_exists or response.status_code != 409:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as request_error:
            if request_error.response.status_code == 409:
                if error_on_exists:
                    print(
                        "Error: URL path already exists: {url}".format(
                            url=os.path.join(
                                args['api_url'],
                                args['url_path']
                            )
                        ),
                        file=sys.stderr
                    )
                    sys.exit(1)
                else:
                    pass
            elif request_error.response.status_code == 403:
                print(
                    (
                        "Error: Permission denied. "
                        "Did you provide a valid API token?"
                    ),
                    file=sys.stderr
                )
                sys.exit(1)
            elif request_error.response.status_code == 502:
                print(
                    (
                        "Error: Bad gateway. Check the API endpoint, "
                        "e.g. 'https://assets.ubuntu.com/v1/'"
                    ),
                    file=sys.stderr
                )
                sys.exit(1)
            else:
                raise request_error

    asset_info = response.json()

    return {
        'local_filepath': filepath,
        'url': os.path.join(
            args['api_url'],
            asset_info['file_path']
        )
    }


# Gather filepaths
filepaths = []

for upload_path in args['upload_paths']:
    if os.path.isdir(upload_path):
        upload_path = os.path.join(upload_path, '**')
    elif not os.path.isfile(upload_path):
        print(
            "Warning: '{upload_path}' is not a file".format(**locals()),
            file=sys.stderr
        )

    for filepath in glob.glob(upload_path, recursive=True):
        if os.path.isfile(filepath):
            filepaths.append(filepath)

if len(filepaths) == 0:
    print('Error: No files specified', file=sys.stderr)
    sys.exit(1)


if args['url_path']:
    if len(filepaths) == 1 and os.path.isfile(filepaths[0]):
        filepath = filepaths[0]
    else:
        print(
            (
                'Error: The "--url-path" option can only '
                'be used when uploading a single file'
            ),
            file=sys.stderr
        )
        sys.exit(1)

    path_filename, path_extension = os.path.splitext(args['url_path'])
    filename, file_extension = os.path.splitext(filepath)

    if path_extension != file_extension:
        print(
            "Error: The \"--url-path\"'s extension should match the file type",
            file=sys.stderr
        )
        sys.exit(1)

    response = upload_file(filepath, args, error_on_exists=True)

    print("[" + json.dumps(response) + "]")

else:
    if len(filepaths) == 1:
        print('[' + json.dumps(upload_file(filepaths[-1], args)) + ']')
    else:
        # Do the first item
        print('[\n  ' + json.dumps(upload_file(filepaths[0], args)))

        # Do all but the last item
        for filepath in filepaths[1:-1]:
            print('  ' + json.dumps(upload_file(filepath, args)) + ',')
            sys.stdout.flush()

        # Do the last item
        print('  ' + json.dumps(upload_file(filepaths[-1], args)) + '\n]')
