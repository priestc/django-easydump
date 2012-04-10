django-easydump
===============

Description:
------------
This application is for easily saving and loading database dumps between deployments. For instance you may want to copy the database
from your production machine onto your development machine for testing. It uses Amazon's S3 service to facilitate in transferring
and storing database dumps.

Installation:
-------------
1. `pip install django-easydump`
2. add to `INSTALLED_APPS`

Configuration:
--------------
In your settings, add three settings: `AWS_SECRET_KEY`, `AWS_ACCESS_KEY`, and `EASYDUMP_MANIFESTS`::

    AWS_SECRET_KEY = ''
    AWS_ACCESS_KEY = ''

    EASYDUMP_MANIFESTS = {
        'location': {
            'database': 'default',
            'include-models': 'Location',
            's3-bucket': 'my_dump_bucket'
        },
        'default': {
            'database': 'default',
            'exclude-models': 'Location',
            's3-bucket': 'my_dump_bucket'
        }
    }
    
* `database` must match one in your `DATABASES` setting (old `DATABASE_` settings are not recognized)
* `include-models` is a list of models that you want included in the dump
* `exclude-models` are models you want to not have included in dumps
* `s3-bucket` is the name of the bucket you want dumps to be saved to.

Usage:
------
`python manage.py make_dump -d default`

This command will dump your database based on the ``default`` manifest in your settings and upload it to the S3 bucket.

`python manage.py load_dump -d location`

This command will download the latest dump according to the `location` manifest from the S3 bucket and apply it to your database.
Make sure you don't run this command on your production machine, it will overwrite data!!

`python manage.py rotate_dumps -d default`

This will go through your bucket and remove all dumps except for ones performed on at 9PM on a monday. This command is to keep your S3 bucket from
getting huge. In future versions, this command will be customizable.

Notes:
------
Postgres/Postgis currently only supported. Mysql/Oracle/SQLite support coming soon.