"""
Functions for uploading files to an assets.ubuntu.com-like assets server
"""

# Core packages
import base64
import json
import os
import glob
import sys

# Third party packages
import requests


def _upload_file(
    filepath, api_domain, api_token,
    tags=None, url_path=None, error_on_exists=False, insecure=False
):
    """
    Upload an individual file to an assets.ubuntu.com-like assets server
    """

    filename = os.path.basename(filepath)
    api_url = "{scheme}://{domain}/v1".format(
        scheme="http" if insecure else "https",
        domain=api_domain
    )

    with open(filepath, 'rb') as asset_file:
        content = asset_file.read()

    response = requests.post(
        api_url,
        data={
            'asset': base64.b64encode(content),
            'friendly-name': filename.replace(' ', '+'),
            'url-path': url_path,
            'tags': tags,
            'type': 'base64',
            'token': api_token
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
                                api_url,
                                url_path
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
                        "e.g. 'https://assets.ubuntu.com/v1'"
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
            api_url,
            asset_info['file_path']
        )
    }


def gather_files(paths):
    """
    Given a list of valid filepaths from a given set of paths.
    Links will be followed, and files will be recursively found inside
    directories
    """

    filepaths = []

    for path in paths:
        path = os.path.realpath(path)

        if os.path.isdir(path):
            path = os.path.join(path, '**')
        elif not os.path.isfile(path):
            print(
                "Warning: '{path}' is not a file".format(**locals()),
                file=sys.stderr
            )

        for filepath in glob.glob(path, recursive=True):
            if os.path.isfile(filepath):
                filepaths.append(filepath)

    return filepaths


def upload_files(
    filepaths, api_domain, api_token,
    tags=None, url_path=None, insecure=False
):
    """
    Upload all the provided files to
    an assets.ubuntu.com-like assets server
    """

    if len(filepaths) == 0:
        print('Error: No files specified', file=sys.stderr)
        sys.exit(1)

    if url_path:
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

        path_filename, path_extension = os.path.splitext(url_path)
        filename, file_extension = os.path.splitext(filepath)

        if path_extension != file_extension:
            print(
                (
                    "Error: The \"--url-path\"'s extension "
                    "should match the file type"
                ),
                file=sys.stderr
            )
            sys.exit(1)

        response = _upload_file(
            filepath, api_domain, api_token, tags,
            url_path, error_on_exists=True
        )

        print("[" + json.dumps(response) + "]")

    else:
        if len(filepaths) == 1:
            item_info = _upload_file(
                filepaths[-1], api_domain, api_token, tags, url_path
            )
            print('[' + json.dumps(item_info) + ']')
        else:
            # Do the first item
            first_item_info = _upload_file(
                filepaths[0], api_domain, api_token, tags, url_path
            )
            print('[\n  ' + json.dumps(first_item_info))

            # Do all but the last item
            for filepath in filepaths[1:-1]:
                item_info = _upload_file(
                    filepath, api_domain, api_token, tags, url_path
                )
                print('  ' + json.dumps(item_info) + ',')
                sys.stdout.flush()

            # Do the last item
            last_item_info = _upload_file(
                filepaths[-1], api_domain, api_token, tags, url_path
            )
            print('  ' + json.dumps(last_item_info) + '\n]')
