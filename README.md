# A command-line tool for managing the [assets server](https://github.com/ubuntudesign/assets-server)

This is intended to be a simple command-line tool for managing assets on an [assets server](https://github.com/ubuntudesign/assets-server).

## Usage

First, install the [required dependencies](requirements.txt).

Then to upload an asset:

``` bash
$ ./upload-asset.py  \
    --api-url https://assets.EXAMPLE.com/v1/  \
    --api-token XXXXXXXX  \
    ~/EXAMPLE_DIRECTORY ./EXAMPLE_IMAGE.png
[
    {"url": "https://assets.ubuntu.com/v1/2071d161-EXAMPLE_IMAGE.png", "filepath": "/home/robin/EXAMPLE_IMAGE.png"},
    {"url": "https://assets.ubuntu.com/v1/2071d161-IMAGE1.png", "filepath": "/home/robin/EXAMPLE_DIRECTORY/IMAGE1.png"},
    {"url": "https://assets.ubuntu.com/v1/2071d161-IMAGE2.png", "filepath": "/home/robin/EXAMPLE_DIRECTORY/IMAGE2.png"}
]
```
