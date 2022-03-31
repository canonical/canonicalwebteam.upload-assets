# A command-line tool for managing [assets.ubuntu.com](https://github.com/canonical-web-and-design/assets.ubuntu.com)

This is intended to be a simple command-line tool for uploading assets to an <https://assets.ubuntu.com>-like assets
server.

## Installation

### Snap install

On a [snap](https://snapcraft.io/)-enabled system, you can simply:

``` bash
sudo snap install upload-assets
```

### Pip install

If you can't install the snap, you can install with pip.

First [install python3 pip](http://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3), then:

``` bash
sudo pip3 install canonicalwebteam.upload-assets
```

## Usage

You should now have access to the `upload-assets` command:

``` bash
$ upload-assets  \
    --api-domain assets.EXAMPLE.com  \
    --api-token XXXXXXXX  \
    ~/EXAMPLE_DIRECTORY ./EXAMPLE_IMAGE.png
[
    {"url": "https://assets.ubuntu.com/v1/2071d161-EXAMPLE_IMAGE.png", "filepath": "/home/robin/EXAMPLE_IMAGE.png"},
    {"url": "https://assets.ubuntu.com/v1/2071d161-IMAGE1.png", "filepath": "/home/robin/EXAMPLE_DIRECTORY/IMAGE1.png"},
    {"url": "https://assets.ubuntu.com/v1/2071d161-IMAGE2.png", "filepath": "/home/robin/EXAMPLE_DIRECTORY/IMAGE2.png"}
]
```

## Configuration

To avoid specifying them every time, you can store both the URL and the token for the assets API in environment variables:

``` bash
$ export UPLOAD_ASSETS_API_TOKEN=<api-token>
$ export UPLOAD_ASSETS_API_DOMAIN=assets.example.com
$ upload-assets EXAMPLE_IMAGE.png
```
