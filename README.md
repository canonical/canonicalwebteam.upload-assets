# A command-line tool for managing the [assets server](https://github.com/ubuntudesign/assets-server)

This is intended to be a simple command-line tool for managing assets on an [assets server](https://github.com/ubuntudesign/assets-server).

## Usage

First, install the [required dependencies](requirements.txt).

Then to upload an asset:

``` bash
$ ./upload-asset.py  \
    --server-url https://assets.EXAMPLE.com/v1/  \
    --auth-token XXXXXXXX  \
    MY-IMAGE.png
{'url': u'https://assets.EXAMPLE.com/v1/xxxxx-MY-IMAGE.png', 'image': True, 'created': u'Tue Sep 27 16:13:22 2016', 'file_path': u'xxxxx-MY-IMAGE.png', 'tags': u''}
```
