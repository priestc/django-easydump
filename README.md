# At a glance #
* Simply create database dumps no matter how large your database is (Django's `loaddata` and `dumpdata` commands choke on tables greater than a few thousand rows)
* Customizable dumps that can exclude certain tables. Some tables contain static data which does not need to be backed up on the same schedule as, say, `UserProfile` data.
* Automatic dump storage and retrieval.

# How it works #
When you run the `make_dump` command, the plugin makes a call to `pg_dump` (only postgres supported at this time), creates a compressed dump, then uploads it to an S3 bucket. It is recommended to only run this command on your production deployment. Preferably in a cron.

When the `load_dump` command is called (it is recommended to only run this command on your local/qa/staging deployments), the app will download the latest dump from the bucket (based on the timestamp in the key), and will apply that database dump into the current database.

# Installation #
1. `pip install django-easydump`
2. add to `INSTALLED_APPS`

# Configuration #
In your settings, add three settings: `AWS_SECRET_KEY`, `AWS_ACCESS_KEY`, and `EASYDUMP_MANIFESTS`::

    AWS_SECRET_KEY = ''
    AWS_ACCESS_KEY = ''

    # optional, defaults to 'us-east-1'
    AWS_REGION = 'us-east-1'

    # optional: email address(es) to notify when make_dump fails
    EASYDUMP_FAILURE_EMAIL = 'admin@example.com'

    EASYDUMP_MANIFESTS = {
        'location': {
            'database': 'default',
            'include-models': 'Location',
            's3-bucket': 'my_dump_bucket'
        },
        'default': {
            'database': 'default',
            'exclude-models': 'Location',
            'extra-tables': ['django_deleted_model'],
            's3-bucket': 'my_dump_bucket'
        }
    }
    
* `database` must match one in your `DATABASES` setting (old `DATABASE_` settings are not recognized)
* `include-models` is a list of models that you want included in the dump (leave blank to include **all** models)
* `exclude-models` are models you want to not have included in dumps. This setting is ignored if `include-models` is defined.
* `extra-table` is a list of table names that do not correlate to a django model which you want included in the dump.
* `s3-bucket` is the name of the bucket you want dumps to be saved to.
* `reduced-redundancy` - When uploading dumps, if this value is `True`, it will save the file to S3 using the
[reduced_redundancy](http://aws.amazon.com/about-aws/whats-new/2010/05/19/announcing-amazon-s3-reduced-redundancy-storage/) flag.
* `EASYDUMP_FAILURE_EMAIL` (optional, global setting, not part of a manifest) - an email address, or list of addresses, to notify via Django's mail backend if `make_dump` fails for any reason (dump command errors, a corrupt/truncated dump, or an S3 upload failure). Sent using `DEFAULT_FROM_EMAIL` as the sender. If unset, no notification is sent - the command will still fail loudly (non-zero exit, logged error) either way.

# Usage #
`python manage.py make_dump default`

This command will dump your database based on the ``default`` manifest in your settings and upload it to the S3 bucket.

`python manage.py load_dump location`

This command will download the latest dump according to the `location` manifest from the S3 bucket and apply it to your database. Make sure you don't run this command on your production machine, it will overwrite data!!

`python manage.py rotate_dumps default`

This will go through your bucket and remove all dumps except for ones performed on at 9PM on a monday. This command is to keep your S3 bucket from getting huge. In future versions, this command will be customizable.

# Notes #
Postgres/Postgis currently only supported. Mysql/Oracle/SQLite support coming soon.

# Changelog #
### unreleased ###
* `make_dump` now checks the dump command's exit status and verifies dump integrity with `pg_restore` before uploading, instead of silently uploading a truncated/corrupt file
* added `EASYDUMP_FAILURE_EMAIL` setting to notify by email when `make_dump` fails
* fixed `Manifest._get_tables()` using `django.db.models.get_models()`, which was removed in Django 1.9 - now uses the `django.apps` registry, restoring compatibility with current Django
* removed a stray `pdb.set_trace()` left in `load_dump --drop`, which would hang the command when run non-interactively
* migrated from `boto` (unmaintained, superseded years ago) to `boto3` - added an optional `AWS_REGION` setting (defaults to `'us-east-1'`)

### v0.1.0 ###
* initial release

### v0.1.1 - v0.1.3 ##
* small documentation fixed

### v0.2.0 ###
* added progress output for uploads/downloads
* improved documentation

### v0.2.1 ###
* better documentation
* added ability to specify `extra-tables` in manifest
* got rid of `-d` option, now you just specify the dump manifest name.
* added changelog to `README`

### v0.2.2 - 0.2.5 ##
* fixed bugs in setup.py