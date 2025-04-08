"""
Functions for uploading files to an assets.ubuntu.com-like assets server
"""

# Core packages
import glob
import json
import os
import re
import sys
from http import HTTPStatus
from pathlib import Path

# Third party packages
import requests


def _upload_file(
    filepath,
    api_domain,
    api_token,
    google_drive_link,
    salesforce_campaign_id,
    language=None,
    deprecated=None,
    asset_type=None,
    author=None,
    tags=None,
    url_path=None,
    error_on_exists=False,
    insecure=False,
    products=None,
    optimize="",
):
    """
    Upload an individual file to an assets.ubuntu.com-like assets server
    """
    filename = Path(filepath).name.replace(" ", "+")
    api_url = "{scheme}://{domain}/v1".format(
        scheme="http" if insecure else "https",
        domain=api_domain,
    )
    headers = {
        "Authorization": f"token {api_token}",
        "Accept": "application/json",
    }

    with Path(filepath).open("rb") as asset_file:
        # Create a FormData object for the upload
        form_data = {
            "tags": tags,
            "products": products,
            "google_drive_link": google_drive_link,
            "salesforce_campaign_id": salesforce_campaign_id,
            "language": language,
            "deprecated": deprecated,
            "asset-type": asset_type,
            "author": author,
            "friendly-name": filename,
        }

        # Prepare the file for upload
        files = {"assets": asset_file}

        # Submit the form data with the file
        response = requests.post(
            api_url,
            data=form_data,
            files=files,
            headers=headers,
            timeout=60,  # Adding timeout for the request
        )

    try:
        response.raise_for_status()
        asset_info = response.json()
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.JSONDecodeError,
    ) as request_error:
        if request_error.response.status_code == HTTPStatus.CONFLICT:
            # Try to get the remote file path, or return the filename
            match = re.search(r".*<p>(.*)</p>", response.text)
            if match:
                file_url = f"{response.url}/{match.group(1)}"
            else:
                file_url = filename
            print(
                f"Error: This file has already been uploaded: {file_url}",
                file=sys.stderr,
            )
            sys.exit(1)
        elif request_error.response.status_code == HTTPStatus.FORBIDDEN:
            print(
                (
                    "Error: Permission denied. Did you provide a valid API token?"
                ),
                file=sys.stderr,
            )
            sys.exit(1)
        elif request_error.response.status_code == HTTPStatus.BAD_GATEWAY:
            print(
                (
                    "Error: Bad gateway. Check the API endpoint, "
                    "e.g. 'https://assets.ubuntu.com/v1'"
                ),
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            print(response.text)
            raise request_error

    return {
        "local_filepath": filepath,
        "url": os.path.join(
            api_url,
            filepath,
        ),
        "data": asset_info,
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
            path = os.path.join(path, "**")
        elif not os.path.isfile(path):
            print(
                "Warning: '{path}' is not a file".format(**locals()),
                file=sys.stderr,
            )

        for filepath in glob.glob(path, recursive=True):
            if os.path.isfile(filepath):
                filepaths.append(filepath)

    return filepaths


def upload_files(
    filepaths,
    api_domain,
    api_token,
    tags="",
    url_path="",
    insecure=False,
    asset_type="",
    optimize="",
    products="",
    author="",
    google_drive_link="",
    salesforce_campaign_id="",
    language="",
    deprecated=False,
):
    """
    Upload all the provided files to
    an assets.ubuntu.com-like assets server
    """

    if len(filepaths) == 0:
        print("Error: No files specified", file=sys.stderr)
        sys.exit(1)

    if url_path:
        if len(filepaths) == 1 and os.path.isfile(filepaths[0]):
            filepath = filepaths[0]
        else:
            print(
                (
                    'Error: The "--url-path" option can only '
                    "be used when uploading a single file"
                ),
                file=sys.stderr,
            )
            sys.exit(1)

        path_filename, path_extension = os.path.splitext(url_path)
        filename, file_extension = os.path.splitext(filepath)

        if path_extension != file_extension:
            print(
                (
                    'Error: The "--url-path"\'s extension '
                    "should match the file type"
                ),
                file=sys.stderr,
            )
            sys.exit(1)

        response = _upload_file(
            filepath=filepath,
            api_domain=api_domain,
            api_token=api_token,
            google_drive_link=google_drive_link,
            salesforce_campaign_id=salesforce_campaign_id,
            language=language,
            deprecated=deprecated,
            asset_type=asset_type,
            author=author,
            tags=tags,
            url_path=url_path,
            error_on_exists=True,
            insecure=insecure,
            products=products,
            optimize=optimize,
        )

        print("[" + json.dumps(response) + "]")

    elif len(filepaths) == 1:
        item_info = _upload_file(
            filepath=filepaths[-1],
            api_domain=api_domain,
            api_token=api_token,
            google_drive_link=google_drive_link,
            salesforce_campaign_id=salesforce_campaign_id,
            language=language,
            deprecated=deprecated,
            asset_type=asset_type,
            author=author,
            tags=tags,
            url_path=url_path,
            insecure=insecure,
            products=products,
            optimize=optimize,
        )
        print("[" + json.dumps(item_info) + "]")
    else:
        # Do the first item
        first_item_info = _upload_file(
            filepath=filepaths[0],
            api_domain=api_domain,
            api_token=api_token,
            google_drive_link=google_drive_link,
            salesforce_campaign_id=salesforce_campaign_id,
            language=language,
            deprecated=deprecated,
            asset_type=asset_type,
            author=author,
            tags=tags,
            url_path=url_path,
            insecure=insecure,
            products=products,
            optimize=optimize,
        )
        print("[\n  " + json.dumps(first_item_info))

        # Do all but the last item
        for filepath in filepaths[1:-1]:
            item_info = _upload_file(
                filepath=filepath,
                api_domain=api_domain,
                api_token=api_token,
                google_drive_link=google_drive_link,
                salesforce_campaign_id=salesforce_campaign_id,
                language=language,
                deprecated=deprecated,
                asset_type=asset_type,
                author=author,
                tags=tags,
                url_path=url_path,
                insecure=insecure,
                products=products,
                optimize=optimize,
            )
            print("  " + json.dumps(item_info) + ",")
            sys.stdout.flush()

        # Do the last item
        last_item_info = _upload_file(
            filepath=filepaths[-1],
            api_domain=api_domain,
            api_token=api_token,
            google_drive_link=google_drive_link,
            salesforce_campaign_id=salesforce_campaign_id,
            language=language,
            deprecated=deprecated,
            asset_type=asset_type,
            author=author,
            tags=tags,
            url_path=url_path,
            insecure=insecure,
            products=products,
            optimize=optimize,
        )
        print("  " + json.dumps(last_item_info) + "\n]")
